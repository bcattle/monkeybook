from voomza.apps.backend.pipeline import FQLTask, TaskPipeline
from voomza.apps.backend import getter
from voomza.apps.backend.settings import *


def _photo_score(photo, photos_i_like_ids):
    """
    Calculates the "top photos" ranking score for a photo
    """
    score =\
    PHOTO_COMMENT_POINTS * photo['comment_count'] +\
    PHOTO_LIKE_POINTS * photo['like_count'] +\
    PHOTO_I_LIKE_POINTS * (1 if photo['id'] in photos_i_like_ids else 0)
    return score


class PhotoResultsTask(FQLTask):
    """
    A task that pulls our standard PHOTO_FIELDS
    """
    depends_on = ['photos_i_like']

    def on_results(self, results, photos_i_like):
        getter = getter.process_photo_results(
            results,
            scoring_fxn=lambda photo: _photo_score(photo, photos_i_like)
        )
        return getter


# name becomes 'photos_i_like'
class PhotosILikeTask(FQLTask):
    fql = '''
        SELECT object_id FROM photo WHERE object_id IN
            (SELECT object_id FROM like WHERE user_id=me())
    '''


class PhotosWithMeTask(PhotoResultsTask):
    """
    Returns all of the photos the current user is tagged in
    This is a field we need to do fast joins on again and again,
    so save it in memory
    """
    fql = '''
        SELECT %s FROM photo
            WHERE object_id IN
                (SELECT object_id FROM photo_tag WHERE subject=me())
            LIMIT 3000
    ''' % getter.PHOTO_FIELDS

    # TODO: add pagination to this call?
    # Are we worried about how many results it'll return at a time?


class OtherTagsPhotosWithMeTask(FQLTask):
    """
    Gets all other people tagged in photos I'm in
    """
    fql = '''
        SELECT object_id FROM photo_tag WHERE object_id IN
           (SELECT object_id FROM photo_tag WHERE subject=me())
        AND subject!=me()
    '''

    def on_results(self, results):
        return getter.FreqDistResultGetter(fb_resp)


class PhotosWithUserTask(PhotoResultsTask):
    def __init__(self, user_id):
        super(PhotosWithUserTask, self).__init__()
        self.fql = '''
            SELECT %s FROM photo
                WHERE object_id IN
                    (SELECT object_id FROM photo_tag WHERE subject=$%d)
        ''' % (getter.PHOTO_FIELDS, user_id)



class YearbookTaskPipeline(TaskPipeline):
    class Meta:
        tasks = [
            PhotosILikeTask(),
            PhotosWithMeTask(),
            OtherTagsPhotosWithMeTask(),
        ]

    def __init__(self, user):
        # Add significant_other and family ids to `tasks`
        super(YearbookTaskPipeline, self).__init__(user)

