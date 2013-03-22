from __future__ import division, print_function, unicode_literals
import datetime
from voomza.apps.books_common.fql.base import FQLTask
from voomza.apps.books_common.getter import process_photo_results, ResultGetter
from voomza.apps.books_common.settings import *
from voomza.apps.core.utils import unix_date_from_datetime
from pytz import utc


class TaggedWithMeTask(FQLTask):
    """
    Returns all of the tags of all photos I am in
    We do this because we can't pull `tags`
    from the `photo` table.
    --> This is a workaround for the fact that
        facebook WHERE queries are broken for `photo_tags`
    """
    def __init__(self, end_time=None, name=None):
        end_time_str = ''
        if end_time:
            end_time_unix = unix_date_from_datetime(end_time)
            end_time_str = 'AND created < %s' % end_time_unix

        self.fql = '''
            SELECT subject, object_id, created FROM photo_tag WHERE object_id IN
                (SELECT object_id FROM photo_tag WHERE subject=me())
            AND subject!=me() %s ORDER BY created DESC
        ''' % end_time_str

        super(TaggedWithMeTask, self).__init__(name)

    def on_results(self, results):
        """
        Build a list of user ids that are tagged with
        the current user
        """
        # We *don't* want to collapse on the object_id field here
        # 2/20: sometimes the `created` field comes back None
        # for some people
        getter = ResultGetter(
            results,
            auto_id_field=True,
            fields=['subject', 'created'],
            integer_fields=['object_id', 'subject'],
            timestamps=['created'],
            # Set a default `created` date in case facebook doesn't give us one
            defaults={'created': datetime.datetime(2012 - 2, 1, 1, tzinfo=utc)},
            )
        return getter


class PhotosOfMeTask(FQLTask):
    """
    Returns all of the photos the current user is tagged in.
    """
    def __init__(self, end_time=None, name=None):
        end_time_str = ''
        if end_time:
            end_time_unix = unix_date_from_datetime(end_time)
            end_time_str = 'created < %s AND ' % end_time_unix

        self.fql = '''
            SELECT %s, album_object_id, caption FROM photo
                WHERE %s object_id IN
                    (SELECT object_id FROM photo_tag WHERE subject=me())
        ''' % (PHOTO_FIELDS, end_time_str)

        super(PhotosOfMeTask, self).__init__(name)

    def on_results(self, results):
        getter = process_photo_results(
            results,
            add_to_fields=['album_object_id', 'caption'],
            add_to_defaults={'caption': ''},
            commit=False,
        )
        return getter


class CommentsOnPhotosOfMeTask(FQLTask):
    """
    Returns all comments on the photos the current user is tagged in
    """
    def __init__(self, end_time=None, name=None):
        end_time_str = ''
        if end_time:
            end_time_str = 'time < %s AND ' % end_time

        self.fql = '''
            SELECT object_id, fromid, time, text, likes, user_likes
                FROM comment WHERE %s object_id IN
                    (SELECT object_id FROM photo_tag WHERE subject=me())
        ''' % end_time_str

        super(CommentsOnPhotosOfMeTask, self).__init__(name)

    def on_results(self, results):
        getter = ResultGetter(
            results,
            auto_id_field=True,
            fields=['object_id', 'fromid', 'time', 'text', 'likes', 'user_likes'],
            integer_fields=['object_id', 'fromid', 'likes'],
            timestamps=['time'],
        )
        return getter
