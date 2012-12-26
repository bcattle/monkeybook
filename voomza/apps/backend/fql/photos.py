from voomza.apps.backend.fql.base import FQLTask
from voomza.apps.backend.getter import process_photo_results, ResultGetter
from voomza.apps.backend.settings import *

class PhotosOfMeTask(FQLTask):
    """
    Returns all of the photos the current user is tagged in.
    """
    fql = '''
        SELECT %s, album_object_id, caption FROM photo
            WHERE object_id IN
                (SELECT object_id FROM photo_tag WHERE subject=me())
    ''' % PHOTO_FIELDS

    def on_results(self, results):
        getter = process_photo_results(
            results,
            add_to_fields=['album_object_id', 'caption'],
            commit=False,
        )
        return getter


class CommentsOnPhotosOfMeTask(FQLTask):
    """
    Returns all comments on the photos the current user is tagged in
    """
    fql = '''
        SELECT object_id, fromid, time, text, likes, user_likes
            FROM comment WHERE object_id IN
        (SELECT object_id FROM photo_tag WHERE subject=me())
    '''
    def on_results(self, results):
        getter = ResultGetter(
            results,
            auto_id_field=True,
            fields=['object_id', 'fromid', 'time', 'text', 'likes', 'user_likes'],
            integer_fields=['object_id', 'fromid', 'likes'],
            timestamps=['time'],
        )
        return getter
