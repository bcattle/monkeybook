from voomza.apps.backend.fql import FQLTask
from voomza.apps.backend.getter import process_photo_results
from voomza.apps.backend.settings import *

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
            )
            for query_results in results
        ]
