import logging, datetime
from pytz import utc
from celery import task
from voomza.apps.backend.getter import FreqDistResultGetter
from voomza.apps.backend.pipeline.yearbook import YearbookTaskPipeline, \
    AlbumInfoTask, AlbumPhotosTask, TopPostOfYearTask
from voomza.apps.backend.settings import *

logger = logging.getLogger(__name__)


@task.task()
def get_top_post_of_year(user):
    task = TopPostOfYearTask()
    results = task.run(user)



    pass


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
    years = sorted(albums_by_year.keys(), reverse=True)
    albums_flat = []
    for year in years:
        albums_flat.extend(albums_by_year[year])

    # Pull 10 albums at a time from the server
    top_albums = []
    album_ids_to_call = []
    while albums_flat:
        album = albums_flat.pop(0)
        album_ids_to_call.append(album['id'])
        if len(album_ids_to_call) == ALBUMS_TO_PULL_AT_ONCE:
            # Make the API call
            task = AlbumInfoTask(album_ids_to_call)
            results = task.run(user)
            # Results came back as a list of getters
            # ea w/ a single element. Flatten to a dictionary
            results_by_id = {}
            for getter in results['album_info']:
                # Albums we don't have access to didn't return any items
                if getter.fields_by_id.items():
                    k,v = getter.fields_by_id.items()[0]
                    results_by_id[k] = v

            # The albums came back in *random* order
            for album_id in album_ids_to_call:
                # Toss if no results, name banned, or has < 4 photos
                if album_id in results_by_id:
                    album = results_by_id[album_id]
                    if album['name'].lower() not in BANNED_ALBUM_NAMES \
                        and album['size'] >= 4:
                        top_albums.append(album)
                        if len(top_albums) >= NUM_TOP_ALBUMS:
                            # We're done
                            # We need to keep track of what album we stopped on
                            # in case an `edit` link pushes us to the next album
                            return albums_flat, top_albums

            # We pulled the ten albums
            # and didn't get enough, repeat
            album_ids_to_call = []

    # If we got here we ran out of albums
    # Just return what we had
    return [], top_albums


@task.task()
def get_top_albums_photos(top_albums_response, user, photos_i_like):
    next_albums, top_albums = top_albums_response

    # Pull photos for the top albums
    task = AlbumPhotosTask([album['id'] for album in top_albums], photos_i_like)
    result = task.run(user)
    top_albums_photos = result['album_photos']
    return top_albums_photos, top_albums, next_albums


@task.task()
def run_yearbook(user):
    pipeline = YearbookTaskPipeline(user)
    # Dispatch the top comments task, since its slow

    # Perform all the I/O intensive operations
    results = pipeline.run()

    # Perform the (minimally) CPU-intensive operations
    # otherwise known as sorting lists of like a thousand elements

    # Bucket the photos by year
    max_year, photos_of_me_by_year = results['photos_of_me'].bucket_by_year()
    photos_of_me_this_year = photos_of_me_by_year[max_year]

    # Get top albums, then pull their photos
    top_albums_async = (
        get_top_albums.subtask((user, photos_of_me_by_year, )) |
        get_top_albums_photos.subtask((user, results['photos_i_like']))
    ).apply_async()
#    next_albums, top_albums = get_top_albums(user, photos_of_me_by_year)

    # Get the top photos, both halves of the year
    half_way = datetime.datetime(datetime.datetime.now().year, 6, 29, tzinfo=utc)
    top_photos_of_me_first_half = photos_of_me_this_year.filter(lambda x: x['created'] < half_way).order_by('score')
    top_photos_of_me_second_half = photos_of_me_this_year.filter(lambda x: x['created'] >= half_way).order_by('score')


    # Pull family photos out of 'tagged_with_me'
    family_ids = {family_member['facebook_id'] for family_member in user.family.values('facebook_id')}
    if family_ids:
        family_photos = [
            photo['object_id'] for photo in results['tagged_with_me'].fields
                if photo['subject'] in family_ids
        ]

    # Pull gf/bf photos out of 'tagged_with_me'
    if user.profile.significant_other_id:
        gf_bf_photos = [
            photo['object_id'] for photo in results['tagged_with_me'].fields
                if photo['subject'] == user.profile.significant_other_id
        ]

    import ipdb
    ipdb.set_trace()

    # Top photos back in time
    # photos_of_me_by_year[year].order_by('score')


    ## Later: Look for same groups back in time

    # Top friends
    # Top comment
    # Birthday comments

    # Grab any derivative tasks
    if top_albums_async.ready():
        top_albums_photos, top_albums, next_albums = top_albums_async.get()
        # Top albums photos     is a list of getters, 1 per album
        # Top albums            is a list of dicts with id, owner, name, size
        # Next albums           is a list of dicts with id, count
    else:
        logger.error('Top albums task failed to complete, skipping')


    # Save everything to the db
    pass


