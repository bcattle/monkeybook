from voomza.apps.backend.pipeline import FQLTask, FqlTaskPipeline
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


class BasePhotoResultsTask(FQLTask):
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


class PhotosWithMeTask(BasePhotoResultsTask):
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
    ''' % PHOTO_FIELDS

    # TODO: add pagination to this call?
    # Are we worried about how many results it'll return at a time?


class GroupShotsTask(FQLTask):
    """
    Gets all other people tagged in photos I'm in
    """
    fql = '''
        SELECT object_id FROM photo_tag WHERE object_id IN
           (SELECT object_id FROM photo_tag WHERE subject=me())
        AND subject!=me()
    '''

    def on_results(self, results):
        photo_tag_counts = getter.FreqDistResultGetter(results)
        group_photos = filter(
            lambda x: x['count'] >= 4,
            photo_tag_counts.fields_ordered_by('count')
        )
        return group_photos


class PhotosWithUserTask(BasePhotoResultsTask):
    def __init__(self, user_id, name=None):
        super(PhotosWithUserTask, self).__init__(name)
        self.fql = '''
            SELECT %s FROM photo
                WHERE object_id IN
                    (SELECT object_id FROM photo_tag WHERE subject=%d)
        ''' % (PHOTO_FIELDS, user_id)

    depends_on = ['photos_with_me']

    def on_results(self, results, photos_i_like, photos_with_me):
        photos_of_user = super(PhotosWithUserTask, self).on_results(results, photos_i_like)
        both_of_us = photos_of_user | photos_with_me.ids
        just_them = photos_of_user - photos_with_me.ids
        return both_of_us, just_them


class TopAlbumsTask(FQLTask):
    """
    Returns the albums I'm most tagged in
    """
    # For every photo I'm in, pull its album id
    # return a frequency distribution
    fql = '''
        SELECT album_object_id FROM photo WHERE object_id IN
           (SELECT object_id FROM photo_tag WHERE subject=me())
    '''

    def on_results(self, results):
        return getter.FreqDistResultGetter(results)


class TopFriendsTask(FQLTask):
    fql = '''

    '''

    def on_results(self, results):
        pass


## PIPELINE RUNS ALL OF THE ABOVE

class YearbookTaskPipeline(FqlTaskPipeline):
    class Meta:
        tasks = [
            PhotosILikeTask(),
#            PhotosWithMeTask(),
            GroupShotsTask(),
#            TopAlbumsTask(),
#            TopFriendsTask(),
        ]

    def __init__(self, user):
        # Add significant_other and family ids to `tasks`
#        for index, fam_member in enumerate(user.family):
#            self.Meta.tasks.append(PhotosWithUserTask(user_id=fam_member, name='photos_with_family_%d' % index))
#        if user.profile.significant_other_id:
#            self.Meta.tasks.append(PhotosWithUserTask(user_id=user.profile.significant_other_id, name='photos_with_gfbf'))

        super(YearbookTaskPipeline, self).__init__(user)


## SECOND MINI PIPELINE

class AlbumPhotosTask(FQLTask):
    """
    Pulls photos from the top `n` albums I'm most tagged in
    """
    def __init__(self, top_albums, photos_i_like):
        self.photos_i_like = photos_i_like
        # Build the queries
        self.fql = [
            'SELECT %s FROM photo WHERE album_object_id=%d'
                % (PHOTO_FIELDS, top_albums.order_by_field('count')[n])
            for n in range(NUM_TOP_ALBUMS)
        ]
        super(AlbumPhotosTask, self).__init__()

    def on_results(self, results):
        # Results is an array of query results
        album_photos = [
            getter.process_photo_results(
                album_results,
                scoring_fxn=lambda photo: _photo_score(photo, self.photos_i_like)
            )
            for album_results in results
        ]
        return album_photos

