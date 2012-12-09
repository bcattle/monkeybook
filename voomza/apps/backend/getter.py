import logging
from datetime import datetime
from pytz import utc
from voomza.apps.backend.settings import *

logger = logging.getLogger(__name__)


class ResultGetter(object):
    """
    An error-tolerant helper class that simplifies
    getting data out of the results returned by facebook
    """
    _ids = None
    _fields_by_id = None
    _ordered = None

    def filter(self, function):
        """
        Filters the elements in this Getter by `function`,
        returning a new getter with the new results set
        """
        pass_filter = filter(function, self.fields)
        return self.from_fields(pass_filter)

    @classmethod
    def from_fields(cls, fields):
        """
        Creates a new getter by setting the fields
        directly, i.e. not parsing them from facebook data
        """
        new_getter = cls([])
        new_fields_by_id = {}
        for element in fields:
            new_fields_by_id[element['id']] = element
        new_getter._fields_by_id = new_fields_by_id
        return new_getter

    @property
    def ids(self):
        if not self._ids:
            self._ids = set(self._fields_by_id.keys())
        return self._ids

    @property
    def fields_by_id(self):
        return self._fields_by_id

    @property
    def fields(self):
        return self._fields_by_id.values()

    def order_by(self, name='id', descending=True):
        """
        Returns a sorted list of the values,
        ordered by the column indicated. Cached.
        """
        if name not in self._ordered:
            self._ordered[name] = sorted(self.fields, key=lambda x: x.get(name), reverse=descending)
        return self._ordered[name]

    def bucket_by_year(self, date_field='created'):
        """
        Returns a tuple (latest_year, results)
        results[year] is a getter for just that year
        """
        fields_by_year = {}
        for item in self.fields:
            item_year = item[date_field].year
            if item_year in fields_by_year:
                fields_by_year[item_year].append(item)
            else:
                fields_by_year[item_year] = [item]
        getters_by_year = {}
        for year, bucket in fields_by_year.items():
            getters_by_year[year] = self.from_fields(bucket)
        max_year = max(getters_by_year.keys())
        return max_year, getters_by_year

    def __len__(self):
        return len(self.ids)

#    def __iter__(self):
#        return self.fields.__iter__()

    def __init__(self, results, id_field='object_id',
                 fields=None, timestamps=None, extra_fields=None, fail_silently=True):
        """
        extra_fields    a dict of field names to add, and a function to call
                        on the existing entry, for instance to calculate a composite value

                        extra_fields={'likes_and_comments': lambda x: x['like_count'] + x['comment_count']}
        """
        self._ids = None
        self._fields_by_id = {}
        self._ordered = {}

        if not fields:
            fields = []
        if not extra_fields:
            extra_fields = {}
        if not timestamps:
            timestamps = []

#        self.results = results
        for curr_result in results:
            processed_fields = {}
            try:
                # If we encounter any ValueError or KeyError,
                # scrub the whole entry (poor man's transaction)
                curr_id = int(curr_result[id_field])      # fail loudly!
                for field in fields:
                    f = field.split('.')
                    field1_val = curr_result[f[0]]        # fail loudly!
                    if len(f) == 1:
                        if f[0] in timestamps:
                            val = datetime.utcfromtimestamp(field1_val).replace(tzinfo=utc)
                        else:
                            val = field1_val
                        processed_fields[f[0]] = val
                    else :
                        # f[1] is the actual field name
                        if f[1] in timestamps:
                            # Assuming fb timestamps come in as UTC
                            val = datetime.fromtimestamp(field1_val[f[1]]).replace(tzinfo=utc)    # fail loudly!
                        else:
                            val = field1_val[f[1]]        # fail loudly!
                        processed_fields[f[1]] = val
                processed_fields['id'] = curr_id
                for extra_name, callable in extra_fields.items():
                    processed_fields[extra_name] = callable(processed_fields)
            except (ValueError, KeyError):
                if fail_silently:
                    continue
                else:
                    raise
            # add to _fields_by_id
            self._fields_by_id[curr_id] = processed_fields


class FreqDistResultGetter(ResultGetter):
    """
    A result getter that returns the data
    in the form of a list of frequencies in descending order
    """
    def __init__(self, results, id_field='object_id', cutoff=0, fail_silently=True):
        """
        Elements that occur less-frequently than `cutoff` are discarded
        """
        self._ids = None
        self._ordered = {}

#        self.results = results
        fields_by_id = {}
        for curr_result in results:
            try:
                # If we encounter any ValueError or KeyError,
                # scrub the whole entry (poor man's transaction)
                curr_id = int(curr_result[id_field])      # fail loudly!
                if curr_id in fields_by_id:
                    fields_by_id[curr_id]['count'] += 1
                else:
                    fields_by_id[curr_id] = {'id': curr_id, 'count': 1}
            except (ValueError, KeyError):
                if fail_silently:
                    continue
                else:
                    raise

        filtered = filter(lambda x: x['count'] > cutoff, fields_by_id.values())
        self._fields_by_id = {item['id']: item for item in filtered}
        self._ids = set(self._fields_by_id.keys())


def process_photo_results(results, scoring_fxn=None, add_to_fields=None):
    """
    Resolves the fields we know about for photos
    """
    fields = ['created', 'height', 'width', 'fb_url',
              'comment_info.comment_count', 'like_info.like_count']
    if add_to_fields:
        fields.extend(add_to_fields)

    fb_results = len(results)
    _set_photo_by_width(results)
    extra_fields = {}
    if scoring_fxn:
        extra_fields['score'] = scoring_fxn
    getter = ResultGetter(
        results,
        fields = fields,
        timestamps = ['created'],
        extra_fields = extra_fields,
        fail_silently=False
    )
    getter_results = len(getter)
    if fb_results != getter_results:
        logger.warning('Facebook returned %d results, our getter only produced %d' % (fb_results, getter_results))
    else:
        logger.info('Pulled %d photos' % getter_results)
    return getter


def _set_photo_by_width(results):
    """
    Handle the fact that the `images` struct
    has a few values.
    We want the smallest > PHOTO_WIDTH_DESIRED or
    the largest otherwise
    """
    for photo in results:
        try:
            images = {image['width']: image for image in photo['images']}
            widths = sorted(images.keys(), reverse=True)
            above_cutoff = filter(lambda x: x > PHOTO_WIDTH_DESIRED, widths)
            if above_cutoff:
                chosen_width = above_cutoff[-1]
            else:
                # If none large enough, take the largest
                chosen_width = widths[0]
            photo['height'] = images[chosen_width]['height']
            photo['width'] = images[chosen_width]['width']
            photo['fb_url'] = images[chosen_width]['source']
            del photo['images']
        except KeyError:
            logger.warning('KeyError in _set_photo_by_width')
            continue
