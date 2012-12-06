import logging
from django_facebook.api import FacebookUserConverter

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
            self._ordered[name] = sorted(self.fields, key=lambda x: x.get(name), reverse=not descending)
        return self._ordered[name]

    def __len__(self):
        return len(self._ids)

    def __init__(self, results, id_field='object_id', fields=None, extra_fields=None):
        """
        extra_fields    a dict of field names to add, and a function to call
                        on the existing entry, for instance to calculate a composite value

                        extra_fields={'likes_and_comments': lambda x: x['like_count'] + x['comment_count']}
        """
        self._ids = set()
        self._fields_by_id = {}
        self._ordered = {}

        if not fields:
            fields = []
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
                        processed_fields[f[0]] = field1_val
                    else :
                        # f[1] is the actual field name
                        processed_fields[f[1]] = field1_val[f[1]]    # fail loudly!
                for extra_name, callable in extra_fields.items():
                    processed_fields[extra_name] = callable(processed_fields)
            except (ValueError, KeyError):
                print 'error'
                continue
            processed_fields['id'] = curr_id
            # add to _fields_by_id
            self._fields_by_id[curr_id] = processed_fields


class BackendFacebookUserConverter(FacebookUserConverter):
    """
    API operations that pull data from facebook that we need
    for the yearbook (preview)

    This class pulls data and returns it in a format
    that other processes can deal with
    (i.e. it does no processing)
    """
    def get_all_photos_i_am_in(self):
        """
        Returns all of the photos the current user is tagged in
        This is a field we need to do fast joins on again and again,
        so save it in memory
        """
        fb_resp = self.open_facebook.fql('''
            SELECT object_id FROM photo_tag WHERE subject=me()
        ''')
        return ResultGetter(fb_resp)


    def get_all_photos_i_like(self):
        fb_resp = self.open_facebook.fql('''
            SELECT object_id FROM photo WHERE object_id IN
                (SELECT object_id FROM like WHERE user_id=me())
        ''')
        return ResultGetter(fb_resp)


    def get_photos_by_user_id(self, facebook_id):
        """
        Returns all of the photos a specified user is tagged in,
        along with the number of comments and likes they have
        """
        fb_resp = self.open_facebook.fql('''
            SELECT object_id, like_info, comment_info FROM photo
                WHERE object_id IN
                (SELECT object_id FROM photo_tag WHERE subject=$%d)
        ''' % facebook_id)
        return ResultGetter(fb_resp)
