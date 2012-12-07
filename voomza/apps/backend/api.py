import logging
from datetime import datetime
from django.utils.timezone import make_aware
from django_facebook.api import FacebookUserConverter
from pytz import utc
from voomza.apps.core.utils import merge_spaces

logger = logging.getLogger(__name__)


class ResultGetter(object):
    """
    An error-tolerant helper class that simplifies
    getting data out of the results returned by facebook
    """
    _ids = None
    _fields_by_id = None
    _ordered = None

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

    def fields_ordered_by(self, name='id', descending=True):
        """
        Returns a sorted list of the values,
        ordered by the column indicated. Cached.
        """
        if name not in self._ordered:
            self._ordered[name] = sorted(self.fields, key=lambda x: x.get(name), reverse=descending)
        return self._ordered[name]

    def __len__(self):
        return len(self.ids)

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

        self.results = results
        for curr_result in self.results:
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
                            val = datetime.fromtimestamp(field1_val)
                        else:
                            val = field1_val
                        processed_fields[f[0]] = val
                    else :
                        # f[1] is the actual field name
                        if f[1] in timestamps:
                            # Assuming fb timestamps come in as UTC
                            val = make_aware(datetime.fromtimestamp(field1_val[f[1]]), timezone=utc)    # fail loudly!
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
    def __init__(self, results, id_field='object_id', fail_silently=True):
        self._ids = None
        self._fields_by_id = {}
        self._ordered = {}

        self.results = results
        for curr_result in self.results:
            try:
                # If we encounter any ValueError or KeyError,
                # scrub the whole entry (poor man's transaction)
                curr_id = int(curr_result[id_field])      # fail loudly!
                if curr_id in self._fields_by_id:
                    self._fields_by_id[curr_id]['count'] += 1
                else:
                    self._fields_by_id[curr_id] = {'id': curr_id, 'count': 1}
            except (ValueError, KeyError):
                if fail_silently:
                    continue
                else:
                    raise
        self._ids = set(self._fields_by_id.keys())


class BackendFacebookUserConverter(FacebookUserConverter):
    """
    API operations that pull data from facebook that we need
    for the yearbook (preview)

    This class pulls data and returns it in a format
    that other processes can deal with
    (i.e. it does no processing)
    """
    PHOTO_FIELDS = 'object_id, images, created, comment_info, like_info'

    def _process_photo_results(self, results, scoring_fxn=None):
        """
        Resolves the fields we know about for photos
        """
        self._set_largest_images(results)
        extra_fields = {}
        if scoring_fxn:
            extra_fields['score'] = scoring_fxn
        getter = ResultGetter(
            results,
            fields = ['created', 'height', 'width', 'fb_url',
                      'comment_info.comment_count', 'like_info.like_count'],
            timestamps = ['created'],
            extra_fields = extra_fields,
            fail_silently=False
        )
        return getter

    def _set_largest_images(self, results):
        """
        Handle the fact that the `images` struct
        has a few values. We want the largest
        """
        for photo in results:
            largest_width = 0
            largest = None
            try:
                for image in photo['images']:
                    if image['width'] > largest_width:
                        largest_width = image['width']
                        largest = image
                if largest:
                    photo['height'] = largest['height']
                    photo['width'] = largest['width']
                    photo['fb_url'] = largest['source']
                    del photo['images']
            except KeyError:
                continue

    def get_all_photos_i_am_in(self, scoring_fxn=None):
        """
        Returns all of the photos the current user is tagged in
        This is a field we need to do fast joins on again and again,
        so save it in memory
        """
        # TODO: add pagination to this call?
        # Are we worried about how many results it'll return at a time?
        fb_resp = self.open_facebook.fql(merge_spaces('''
            SELECT %s FROM photo
                WHERE object_id IN
                    (SELECT object_id FROM photo_tag WHERE subject=me())
        ''' % self.PHOTO_FIELDS))
        fb_results = len(fb_resp)
        # Get the getter
        getter = self._process_photo_results(fb_resp, scoring_fxn)
        getter_results = len(getter)
        if fb_results != getter_results:
            logger.warning('Facebook returned %d results, our getter only produced %d' % (fb_results, getter_results))
        else:
            logger.info('Pulled %d photos' % getter_results)
        return getter


    def get_all_photos_i_like(self):
        fb_resp = self.open_facebook.fql(merge_spaces('''
            SELECT object_id FROM photo WHERE object_id IN
                (SELECT object_id FROM like WHERE user_id=me())
        '''))
        return ResultGetter(fb_resp)


    def get_other_tags_of_photos_im_in(self):
        """
        Gets all other people tagged in photos I'm in
        """
        fb_resp = self.open_facebook.fql(merge_spaces('''
            SELECT object_id FROM photo_tag WHERE object_id IN
               (SELECT object_id FROM photo_tag WHERE subject=me())
            AND subject!=me()
        '''))
        return FreqDistResultGetter(fb_resp)


    def get_photos_by_user_id(self, facebook_id, scoring_fxn=None):
        """
        Returns all of the photos a specified user is tagged in,
        along with the number of comments and likes they have
        """
        fb_resp = self.open_facebook.fql(merge_spaces('''
            SELECT %s FROM photo
                WHERE object_id IN
                (SELECT object_id FROM photo_tag WHERE subject=$%d)
        ''' % (self.PHOTO_FIELDS, facebook_id)))
        getter = self._process_photo_results(fb_resp, scoring_fxn)
        return getter
