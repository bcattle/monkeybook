import datetime
from pytz import utc
from celery import task
from voomza.apps.backend.getter import FreqDistResultGetter
from voomza.apps.backend.pipeline.yearbook import YearbookTaskPipeline, \
    AlbumInfoTask
from voomza.apps.backend.settings import *


@task.task()
def get_top_albums(user, photos_of_me_by_year):
    """
    Returns a ranked list of all of the albums
    the user is in
    """
    # We have the *photos* bucketed by year,
    # collapse into albums by year
    albums_by_year = {
        year:
            FreqDistResultGetter(
                bucket.fields,
                id_field='album_object_id',
            ).order_by('count')
        for year, bucket in photos_of_me_by_year.items()
    }

    # Make a flat list so we can iterate across year boundaries
    years = reversed(albums_by_year.keys())
    albums_flat = []
    for year in years:
        albums_flat.extend(albums_by_year[year])

    # Pull 10 albums at a time from the server
    top_albums = []
    albums_to_call = []
    while albums_flat:
        albums_to_call.append(albums_flat.pop(0))
        if len(albums_to_call) == ALBUMS_TO_PULL_AT_ONCE:
            # Make the API call
            task = AlbumInfoTask([album['id'] for album in albums_to_call])
            results = task.run(user)
            # Results came back as a list of getters
            # ea w/ a single element. Flatten to a dictionary
            results_by_id = {}
            for getter in results['album_info']:
                # Albums we don't have access to didn't return any items
                if getter.fields_by_id.items():
                    k,v = getter.fields_by_id.items()[0]
                    results_by_id[k] = v

            import ipdb
            ipdb.set_trace()

            # The albums came back in *random* order
            for album_id in albums_to_call:
                album = results_by_id[album_id]
                # Toss if name banned, or has < 4 photos
                if album['name'].lower() not in BANNED_ALBUM_NAMES.lower() \
                    and album['size'] >= 4:
                    top_albums.append(album)
                    if len(top_albums) >= NUM_TOP_ALBUMS:
                        # We're done
                        # We need to keep track of what album we stopped on
                        # in case an `edit` link pushes us to the next album
                        return albums_flat, top_albums

    # If we got here we ran out of albums
    # Just return what we had
    return [], top_albums






@task.task()
def run_yearbook(user):
    pipeline = YearbookTaskPipeline(user)
    # Perform all the I/O intensive operations
    results = pipeline.run()

    # Perform the (minimally) CPU-intensive operations
    # otherwise known as sorting lists of like a thousand elements

    # Bucket the photos by year
    max_year, photos_of_me_by_year = results['photos_of_me'].bucket_by_year()

    photos_of_me_this_year = photos_of_me_by_year[max_year]
    half_way = datetime.datetime(datetime.datetime.now().year, 6, 29, tzinfo=utc)
    # Get the top photos, both halves of the year
    top_photos_of_me_first_half = photos_of_me_this_year.filter(lambda x: x['created'] < half_way).order_by('score')
    top_photos_of_me_second_half = photos_of_me_this_year.filter(lambda x: x['created'] >= half_way).order_by('score')

    # Get top albums
#    top_albums_async = get_top_albums.delay(user, photos_of_me_by_year)
    top_albums = get_top_albums(user, photos_of_me_by_year)

    # Pull photos for the top n albums
#    album_photos_async = pull_album_photos.delay(user, top_albums, results['photos_i_like'])


    # Pull family photos out of 'tagged_with_me'
    family_ids = user.profile.family.all().values('facebook_id')
#    if family_ids:
#        family_photos =
    # Pull gf/bf photos out of 'tagged_with_me'
    if user.profile.significant_other_id:
#    gf_bf_photos =
        pass

    # Sort for top photos back in time
    # Find one photo per bucket

    ## Later: Look for same groups back in time

    # Top friends
    # Top comment
    # Birthday comments


    # Save everything to the db

    # Make sure any derivative tasks finished
    album_photos_async.get()

#
#@task.task(ignore_result=True)
#def pull_album_photos(user, top_albums, photos_i_like):
#    """
#    This runs in its own task since it involves
#     another roundtrip to fb
#    """
#    album_photos_task = AlbumPhotosTask(top_albums, photos_i_like)
#    album_photos = album_photos_task.run(user)
#    # Save to db
#    return album_photos
