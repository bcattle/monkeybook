import logging, datetime
from celery.exceptions import TimeoutError
from pytz import utc
from celery import task, group
from voomza.apps.backend.getter import FreqDistResultGetter
from voomza.apps.backend.models import PhotoRankings
from voomza.apps.backend.pipeline.yearbook import *
from voomza.apps.backend.settings import *
from backend.pipeline import run_task as rt

logger = logging.getLogger(__name__)


@task.task()
def get_photos_by_year(results):
    import ipdb
    ipdb.set_trace()

    # Bucket the photos by year
    max_year, photos_of_me_by_year = results['photos_of_me'].bucket_by_year()
    photos_of_me_this_year = photos_of_me_by_year[max_year]

    results['photos_of_me_by_year'] = photos_of_me_by_year
    results['photos_of_me_this_year'] = photos_of_me_this_year
    return results


@task.task()
def get_top_albums(results, user):
    """
    Returns a ranked list of all of the albums
    the user is in
    """
    assert 'photos_of_me_by_year' in results
    import ipdb
    ipdb.set_trace()

    # We have the *photos* bucketed by year,
    # collapse into albums by year
    albums_by_year = {
        year:
            FreqDistResultGetter(
                bucket.fields,
                id_field='album_object_id',
            ).order_by('count')
        for year, bucket in results['photos_of_me_by_year'].items()
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
            task_results = task.run(user)
            # Results came back as a list of getters
            # ea w/ a single element. Flatten to a dictionary
            results_by_id = {}
            for getter in task_results['album_info']:
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
                            results['albums_flat'] = albums_flat
                            results['top_albums'] = top_albums
                            return results

                            # We pulled the ten albums
            # and didn't get enough, repeat
            album_ids_to_call = []

    # If we got here we ran out of albums
    # Just return what we had
    results['albums_flat'] = []
    results['top_albums'] = top_albums
    return results


@task.task()
def get_top_albums_photos(results, user):
    import ipdb
    ipdb.set_trace()

    assert 'top_albums' in results
    assert 'photos_i_like' in results

    # Pull photos for the top albums
    task = AlbumPhotosTask([album['id'] for album in results['top_albums']], results['photos_i_like'])
    result = task.run(user)
    top_albums_photos = result['album_photos']
    results['top_albums_photos'] = top_albums_photos
    return results


@task.task()
def get_top_post_of_year(results, user):
    assert 'posts_from_year' in results
    top_post = results['posts_from_year'].order_by('score')[0]
    get_post_task = GetPostTask(top_post['id'])
    top_post = get_post_task.run(user)
    # Return JSON of top post
    results['top_post'] = top_post
    return results


#@task.task()
#def on_photos_i_like(photos_i_like, user):
#    job = group([
#        rt.subtask((PhotosOfMeTask,     user.id)),
#        get_top_albums.subtask((photos_i_like, user,)) | get_top_albums_photos.subtask((photos_i_like, user,)),
#    ])
#    job_async = job.apply_async()
#    return job_async


@task.task()
def run_yearbook(user):
    # Fire all tasks
    job = group([
#        rt.subtask(kwargs={'task_cls': PhotosILikeTask, 'user_id': user.id}) |
#            rt.subtask(kwargs={'task_cls': PhotosOfMeTask, 'user_id': user.id}) |
#            get_photos_by_year.subtask() |
#            get_top_albums.subtask((user,)) |
#            get_top_albums_photos.subtask((user,)),

#        rt.subtask(kwargs={'task_cls': TaggedWithMeTask,        'user_id': user.id}),
#        rt.subtask(kwargs={'task_cls': TaggedWithThisYearTask,  'user_id': user.id}),
#        rt.subtask(kwargs={'task_cls': TopPostersFromYearTask,  'user_id': user.id}),

#        rt.subtask(kwargs={'task_cls': GroupShotsTask,          'user_id': user.id}),

#        rt.subtask(kwargs={'task_cls': PostsFromYearTask, 'user_id': user.id}) |
#            get_top_post_of_year.subtask((user, )),

        rt.subtask(kwargs={'task_cls': BirthdayPostsTask,  'user_id': user.id,
                           'init_args': {'birthday': user.profile.date_of_birth}}),
    ])
    job_async = job.apply_async()

    # Wait for everything to finish
    try:
        results = job_async.get()
    except TimeoutError:
        # TODO handle the timeout
        pass

    import ipdb
    ipdb.set_trace()

    pass


@task.task()
def run_yearbook2(user):
    pipeline = YearbookTaskPipeline(user)

    # Perform all the I/O intensive operations
    results = pipeline.run()

    # Perform the (minimally) CPU-intensive operations
    # otherwise known as sorting lists of like a thousand elements

    # Sort the photos in score order


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
    tagged_with_me = results['tagged_with_me'].order_by('score')
    family_ids = {family_member['facebook_id'] for family_member in user.family.values('facebook_id')}
    family_photos = []
    if family_ids:
        family_photos = [
            photo['object_id'] for photo in tagged_with_me
                if photo['subject'] in family_ids
        ]

    # Pull gf/bf photos out of 'tagged_with_me'
    gf_bf_photos = []
    if user.profile.significant_other_id:
        gf_bf_photos = [
            photo['object_id'] for photo in tagged_with_me
                if photo['subject'] == user.profile.significant_other_id
        ]

    # Top photos back in time
    # photos_of_me_by_year[year].order_by('score')

    ## Later: Look for same groups back in time

    # Top post of the year
    # results['posts_from_year'].order_by('score')[0

    # Pull the top post
    top_post_task = GetPostTask(post_id=results['posts_from_year'].order_by('score')[0]['id'])
    top_post_json = top_post_task.run(user)

    # Birthday comments
    birthday_posts_task = BirthdayPostsTask(user.profile.date_of_birth)
    birthday_posts_json = birthday_posts_task.run(user)

    # Top friends

    import ipdb
    ipdb.set_trace()


    # Grab any derivative tasks
    if top_albums_async.ready():
        top_albums_photos, top_albums, next_albums = top_albums_async.get()
        # Top albums photos     is a list of getters, 1 per album
        # Top albums            is a list of dicts with id, owner, name, size
        # Next albums           is a list of dicts with id, count
    else:
        logger.error('Top albums task failed to complete, skipping')


    # Save the photos to the db


    # Build the tables of photo ids
    rankings = PhotoRankings(user=user)
    # These are serialized lists of photo ids
    rankings.family_with = family_photos
    rankings.gfbf_with = gf_bf_photos

    # Need to do a join on `score` in results['photos_of_me'].fields_by_id[ ]
    rankings.group_shots = results['group_shots'].order_by

    # Save everything to the db
    pass


