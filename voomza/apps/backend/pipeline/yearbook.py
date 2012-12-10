import logging, datetime, calendar
from pytz import utc
from voomza.apps.backend.pipeline import FQLTask, FqlTaskPipeline
from voomza.apps.backend.getter import process_photo_results, FreqDistResultGetter, ResultGetter
from voomza.apps.backend.settings import *

logger = logging.getLogger(__name__)


def _photo_score(photo, photos_i_like_ids):
    """
    Calculates the "top photos" ranking score for a photo
    """
    score =\
        PHOTO_COMMENT_POINTS * photo['comment_count'] +\
        PHOTO_LIKE_POINTS * photo['like_count'] +\
        PHOTO_I_LIKE_POINTS * (1 if photo['id'] in photos_i_like_ids else 0)
    return score

def _post_score(post):
    score = \
        POST_COMMENT_POINTS * post['comment_count'] +\
        POST_LIKE_POINTS * post['like_count']
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


class PhotosILikeTask(FQLTask):
    fql = '''
        SELECT object_id FROM photo WHERE object_id IN
            (SELECT object_id FROM like WHERE user_id=me())
    '''


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
        AND subject!=me() ORDER BY created DESC
    '''
    # TODO: future improvement? - pull date of photo instead of tag
    def on_results(self, results):
        """
        Build a list of user ids that are tagged with
        the current user
        """
        # We *don't* want to collapse on the object_id field here
        getter = ResultGetter(
            results,
            auto_id_field=True,
            fields=['subject'],
            integer_fields=['object_id', 'subject']
        )
        logger.info('Got %d tags with user' % len(getter))
        return getter


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


# NOT NEEDED
# We need this so we can index into the friends array
class AllFriendsTask(FQLTask):
    fql = '''
        SELECT uid2 FROM friend WHERE uid1=me()
    '''

    def on_results(self, results):
        return ResultGetter(results, id_field='uid2')


# DOESN'T WORK
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


class PostsFromYearTask(FQLTask):
    def __init__(self, name=None):
        # http://stackoverflow.com/a/11409065/1161906
        nyd = datetime.datetime(datetime.datetime.now().year - 1, 1, 1, tzinfo=utc)
        unix_time = calendar.timegm(nyd.utctimetuple())
        self.fql = '''
            SELECT post_id, comments, likes FROM stream
                WHERE source_id = me() AND created_time < %s LIMIT 500
        ''' % unix_time
        super(PostsFromYearTask, self).__init__(name)

    def on_results(self, results):
        getter = ResultGetter(
            results,
            id_field='post_id',
            id_is_int=False,
            fields=['comments.count', 'likes.count'],
            field_names={'comments.count': 'comment_count', 'likes.count': 'like_count'},
            defaults={'comments.count': 0, 'likes.count':0 },
            extra_fields={'score': _post_score},
        )
        logger.info('Got %d wall posts' % len(getter))
        return getter


class GetPostTask(FQLTask):
    def __init__(self, post_id, name=None):
        self.fql = '''
            SELECT message, comments, likes, created_time, place, attachment
                FROM stream WHERE post_id = '%s'
        ''' % post_id
        super(GetPostTask, self).__init__(name)

    def on_results(self, results):
        # This one requires looping through to get the comments (and likes for that matter)
        # Just return the JSON
        return results


class BirthdayPostsTask(FQLTask):
    def __init__(self, birthday, name=None):
        birthday_this_year = datetime.datetime(datetime.date.today().year, birthday.month, birthday.day, 0, 0, 0)
        start_time = birthday_this_year - datetime.timedelta(days=1)
        end_time = birthday_this_year + datetime.timedelta(days=3)
        start_unix_time = calendar.timegm(start_time.utctimetuple())
        end_unix_time = calendar.timegm(end_time.utctimetuple())

        self.fql = '''
            SELECT post_id, actor_id, message, comments FROM stream
                WHERE filter_key = 'others' AND source_id = me() AND target_id = me()
                AND created_time > %s AND created_time < %s LIMIT 200
        ''' % (start_unix_time, end_unix_time)
        super(BirthdayPostsTask, self).__init__(name)

    def on_results(self, results):
        return results


class TopPostersFromYearTask(FQLTask):
    def __init__(self, name=None):
        nyd = datetime.datetime(datetime.datetime.now().year - 1, 1, 1, tzinfo=utc)
        unix_time = calendar.timegm(nyd.utctimetuple())
        self.fql = '''
            SELECT actor_id FROM stream WHERE filter_key = 'others' AND source_id = me()
                AND target_id = me() AND created_time < %s LIMIT 500
        ''' % unix_time
        super(TopPostersFromYearTask, self).__init__(name)

    def on_results(self, results):
        getter = FreqDistResultGetter(
            results,
            id_field='actor_id',
        )
        return getter


class TaggedWithThisYearTask(FQLTask):
    def __init__(self, name=None):
        nyd = datetime.datetime(datetime.datetime.now().year - 1, 1, 1, tzinfo=utc)
        unix_time = calendar.timegm(nyd.utctimetuple())
        self.fql = '''
            SELECT subject FROM photo_tag WHERE object_id IN
                (SELECT object_id FROM photo_tag WHERE subject = me())
            AND created < %s LIMIT 500
        ''' % unix_time
        super(TaggedWithThisYearTask, self).__init__(name)

    def on_results(self, results):
        getter = FreqDistResultGetter(
            results,
            id_field='subject',
        )
        return getter


## ALBUM TASKS

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


class AlbumPhotosTask(FQLTask):
    """
    Pulls photos from the specified albums
    """
    def __init__(self, album_ids, photos_i_like):
        self.photos_i_like = photos_i_like
        # Build the queries
        self.fql = [
            'SELECT %s FROM photo WHERE album_object_id=%s LIMIT 40' % (PHOTO_FIELDS, album_id)
            for album_id in album_ids
        ]
        super(AlbumPhotosTask, self).__init__()

    def on_results(self, results):
        # Results is an array of results for each query
        return [
            process_photo_results(
                query_results,
                scoring_fxn=lambda photo: _photo_score(photo, self.photos_i_like.ids)
            )
            for query_results in results
        ]


## PIPELINE

#class YearbookTaskPipeline(FqlTaskPipeline):
#    class Meta:
#        tasks = [
#            PhotosILikeTask(),
#            PhotosOfMeTask(),
#            TaggedWithMeTask(),
#            GroupShotsTask(),
#            PostsFromYearTask(),
#            TopPostersFromYearTask(),
#            TaggedWithThisYearTask(),
#        ]
#
#    def __init__(self, user):
#        super(YearbookTaskPipeline, self).__init__(user)
#
