from celery import task
from voomza.apps.backend.pipeline.yearbook import YearbookTaskPipeline, \
    AlbumPhotosTask


@task.task()
def run_yearbook(user):
    pipeline = YearbookTaskPipeline(user)
    # Perform all the I/O intensive operations
    results = pipeline.run()

    # Spin off the AlbumPhotos task since its *query*
    # depends on ids returned by another task
    album_photos_async = pull_album_photos.delay(user, top_albums, photos_i_like)

    # Perform the (minimally) CPU-intensive operations
    # otherwise known as sorting lists of a thousand elements

    # Sort for top photos of year
    # Sort for top photos of first half of year
    # Sort for top photos of second half of year
    # Sort for top photos back in time

    # Look for same groups back in time

    # Save everything to the db

    # Make sure any derivative tasks finished
    album_photos_async.get()


@task.task(ignore_result=True)
def pull_album_photos(user, top_albums, photos_i_like):
    """
    This runs in its own task since it involves
     another roundtrip to fb
    """
    album_photos_task = AlbumPhotosTask(top_albums, photos_i_like)
    album_photos = album_photos_task.run(user)
    # Save to db
    return album_photos
