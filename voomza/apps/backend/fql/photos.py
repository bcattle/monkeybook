from voomza.apps.backend.fql import FQLTask
from voomza.apps.backend.getter import process_photo_results, ResultGetter
from voomza.apps.backend.settings import *

class PhotosOfMeTask(FQLTask):
    """
    Returns all of the photos the current user is tagged in.
    """
    fql = '''
        SELECT %s, album_object_id FROM photo
            WHERE object_id IN
                (SELECT object_id FROM photo_tag WHERE subject=me())
    ''' % PHOTO_FIELDS

    depends_on = ['photos_i_like']

    def on_results(self, results, photos_i_like):
        from voomza.apps.backend.tasks.score import photo_score
        getter = process_photo_results(
            results,
            scoring_fxn=lambda photo: photo_score(photo, photos_i_like.ids),
            add_to_fields=['album_object_id'],
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
