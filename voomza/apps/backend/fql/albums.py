from voomza.apps.backend.fql.base import FQLTask
from voomza.apps.backend.getter import process_photo_results, ResultGetter
from voomza.apps.backend.settings import *


class AlbumPhotosTask(FQLTask):
    """
    Pulls photos from the specified albums
    """
    def __init__(self, album_ids):
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
                scoring_fxn=self._album_photo_score
            )
            for query_results in results
        ]

    def _album_photo_score(self, photo):
        """
        Calculates the "top photos" ranking score for a photo
        """
        score =\
            ALBUM_POINTS_FOR_COMMENT * photo['comment_count'] +\
            ALBUM_POINTS_FOR_LIKE * photo['like_count']
        return score


class AlbumInfoTask(FQLTask):
    """
    Pulls album name and size from the specified albums
    """
    def __init__(self, album_ids):
        self.fql = [
            'SELECT object_id, name, size FROM album WHERE object_id=%s' % album_id
            for album_id in album_ids
        ]
        super(AlbumInfoTask, self).__init__()

    def on_results(self, results):
        # Results is an array of results for each query
        return [
            ResultGetter(
                query_results,
                fields=['name', 'size'],
                integer_fields=['size']
            )
            for query_results in results
        ]
