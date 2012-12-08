from voomza.apps.backend.pipeline import FQLTask, FqlTaskPipeline
from voomza.apps.backend.getter import process_photo_results, FreqDistResultGetter, ResultGetter
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
        getter = process_photo_results(
            results,
            scoring_fxn=lambda photo: _photo_score(photo, photos_i_like.ids)
        )
        return getter


# name becomes 'photos_i_like'
class PhotosILikeTask(FQLTask):
    fql = '''
        SELECT object_id FROM photo WHERE object_id IN
            (SELECT object_id FROM like WHERE user_id=me())
    '''

# We need this so we can index into the friends array
#class AllFriendsTask(FQLTask):
#    fql = '''
#        SELECT uid2 FROM friend WHERE uid1=me()
#    '''
#
#    def on_results(self, results):
#        return ResultGetter(results, id_field='uid2')


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
        getter = process_photo_results(
            results,
            scoring_fxn=lambda photo: _photo_score(photo, photos_i_like.ids),
            add_to_fields=['album_object_id'],
        )
        return getter


class TaggedWithMeTask(FQLTask):
    """
    Returns all of the tags of all photos I am in
    We do this because we can't pull `tags`
    from the `photo` table.
    --> This is a workaround for the fact that
        facebook WHERE queries are broken for `photo_tags`
    """
    fql = '''
        SELECT subject, object_id FROM photo_tag WHERE object_id IN
            (SELECT object_id FROM photo_tag WHERE subject=me())
    '''
    def on_results(self, results):
        """
        Build a list of user ids that are tagged with
        the current user
        """
        return ResultGetter(results, fields=['subject'])



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
        group_photos = FreqDistResultGetter(results, cutoff=GROUP_PHOTO_IS)
        return group_photos


class PhotosWithUserTask(BasePhotoResultsTask):
    depends_on = ['photos_i_like', 'all_friends']

    def __init__(self, user_id, name=None):
        """
        This is a HACK due to the fact that facebook's
        WHERE clauses aren't apparently working.

        We are able to do an IN clause, so we index into their friends,
        hoping that those friends are always returned in the same order.
        Currently they appear to be monotonic over id.
        """
        self.fql = '''
            SELECT %s FROM photo
                WHERE object_id IN
                    (SELECT object_id FROM photo_tag WHERE subject=%d)
        ''' % (PHOTO_FIELDS, user_id)
        super(PhotosWithUserTask, self).__init__(name)

    depends_on = ['photos_of_me']

    def on_results(self, results, photos_i_like, photos_of_me):
        photos_of_user = super(PhotosWithUserTask, self).on_results(results, photos_i_like)
        both_of_us = photos_of_user | photos_of_me.ids
        just_them = photos_of_user - photos_of_me.ids
        return both_of_us, just_them


class TopAlbumPhotosTask(FQLTask):
    """
    Returns photos from the identified top albums
    """
    fql = '''
    '''

    def on_results(self, results):
        return FreqDistResultGetter(results)


class TopFriendsTask(FQLTask):
    # Most-tagged NOT in group shots?
    fql = '''

    '''

    def on_results(self, results):
        pass


## PIPELINE RUNS ALL OF THE ABOVE

class YearbookTaskPipeline(FqlTaskPipeline):
    class Meta:
        tasks = [
            PhotosILikeTask(),
            PhotosOfMeTask(),
#            TaggedWithMeTask(),
#            GroupShotsTask(),
#            TopFriendsTask(),
        ]

    def __init__(self, user):
        # Add significant_other and family ids to `tasks`
#        for index, fam_member in enumerate(user.family.all()):
#            self.Meta.tasks.append(PhotosWithUserTask(user_id=fam_member, name='photos_with_family_%d' % index))
#        if user.profile.significant_other_id:
#            self.Meta.tasks.append(PhotosWithUserTask(user_id=user.profile.significant_other_id, name='photos_with_gfbf'))

        super(YearbookTaskPipeline, self).__init__(user)


## SECOND MINI PIPELINE

class AlbumInfoTask(FQLTask):
    """
    Returns photos from the identified top albums
    """
    # Note, size is "deprecated", whatever that means
    def __init__(self, album_ids):
        # Build the queries
        self.fql = [
            'SELECT object_id, owner, name, size FROM album WHERE object_id=%s' % album_id
            for album_id in album_ids
        ]
        super(AlbumInfoTask, self).__init__()

    def on_results(self, results):
        # Results is an array of results for each query
        return [
            ResultGetter(
                query_result,
                fields=['owner', 'name', 'size']
            )
            for query_result in results
        ]


class TopAlbumPhotosTask(FQLTask):
    """
    Pulls photos from the specified albums
    """
    def __init__(self, album_ids, photos_i_like):
        self.photos_i_like = photos_i_like
        # Build the queries
        self.fql = [
            'SELECT %s FROM photo WHERE album_object_id=%s' % (PHOTO_FIELDS, album_id)
            for album_id in album_ids
        ]
        super(TopAlbumPhotosTask, self).__init__()

    def on_results(self, results):
        # Results is an array of results for each query
        return [
            process_photo_results(
                query_results,
                scoring_fxn=lambda photo: _photo_score(photo, self.photos_i_like.ids)
            )
            for query_results in results
        ]
