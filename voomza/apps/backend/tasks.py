import logging, datetime
from celery.exceptions import TimeoutError
from pytz import utc
from celery import task, group
from voomza.apps.core.utils import merge_dicts
from voomza.apps.backend.getter import FreqDistResultGetter
from voomza.apps.backend.models import PhotoRankings, Yearbook
from voomza.apps.backend.pipeline.yearbook import *
from voomza.apps.backend.settings import *
from backend.pipeline import run_task as rt

logger = logging.getLogger(__name__)


@task.task()
def get_photos_by_year(results, user):
    # Bucket the photos by year
    max_year, photos_of_me_by_year = results['photos_of_me'].bucket_by_year()
    photos_of_me_this_year = photos_of_me_by_year[max_year]

    # Get the top photos, both halves of the year
    half_way = datetime.datetime(datetime.datetime.now().year, 6, 29, tzinfo=utc)
    top_photos_of_me_first_half = photos_of_me_this_year.filter(lambda x: x['created'] < half_way)
    top_photos_of_me_second_half = photos_of_me_this_year.filter(lambda x: x['created'] >= half_way)

    # Serialize and store
    rankings = PhotoRankings.objects.get(user=user)

    years = list(sorted(photos_of_me_by_year.keys(), reverse=True))
    for index, year in enumerate(years[1:NUM_PREV_YEARS + 1]):
        setattr(rankings, 'you_back_in_time_year_%d' % (index + 1), photos_of_me_by_year[year].order_by('score'))

    rankings.top_photos = photos_of_me_this_year.order_by('score')
    rankings.top_photos_first_half = top_photos_of_me_first_half.order_by('score')
    rankings.top_photos_second_half = top_photos_of_me_second_half.order_by('score')
    rankings.save()

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
    assert 'top_albums' in results
    assert 'photos_i_like' in results
    assert 'photos_of_me' in results

    # Pull photos for the top albums
    task = AlbumPhotosTask(
        [album['id'] for album in results['top_albums']],
        results['photos_i_like']
    )
    result = task.run(user)
    top_albums_photos = result['album_photos']

    albums_by_score = [
        [
            {'id': photo['id'], 'score':photo['score']}
            for photo in getter.order_by('score')
        ] for getter in top_albums_photos
    ]

    # Boost highest-scoring photos *of user* in album to front
    for album in albums_by_score:
        found_photos = 0
        for photo_index in range(len(album)):
            if album[photo_index]['id'] in results['photos_of_me'].ids:
                # Move it to the front
                photo = album.pop(photo_index)
                album.insert(0, photo)
                photo_index += 1
                found_photos += 1
                if found_photos >= PICS_OF_USER_TO_PROMOTE:
                    break


    # Save ranked photos
    rankings = PhotoRankings.objects.get(user=user)
    rankings.top_albums = albums_by_score
    rankings.save()

    results['top_albums_photos'] = top_albums_photos
    return results


@task.task()
def get_most_tagged_recently(results):
    assert 'tagged_with_me' in results
    this_year = datetime.datetime(datetime.datetime.now().year - 3, 1, 1, tzinfo=utc)
    tagged_recently = results['tagged_with_me']['tagged_with_me'].filter(
        lambda x: x['created'] > this_year
    )
    results['most_tagged_recently'] = FreqDistResultGetter(
        tagged_recently.fields, id_field='subject'
    )
    return results


@task.task()
def get_top_post_of_year(results, user):
    assert 'posts_from_year' in results
    top_post = results['posts_from_year'].order_by('score')[0]
    get_post_task = GetPostTask(top_post['id'])
    top_post = get_post_task.run(user)

    rankings = PhotoRankings.objects.get(user=user)
    rankings.top_post = top_post
    rankings.save()

    # Return JSON of top post
    results['top_post'] = top_post
    return results


@task.task()
def get_top_friends_and_groups(results, user):
    """
    This takes input from PhotosOfMe and
    TaggedWithMe, TaggedWithThisYear, and TopPostersFromYear

    For convenience, it fires off the group that depends on PhotosOfMe
    """

    # Flatten the results returned from the group
    results = merge_dicts(*results)

    on_photos_of_me = group([
        get_photos_by_year.subtask((results,user,)) |
        get_top_albums.subtask((user,)) |
        get_top_albums_photos.subtask((user,))
    ])
    on_photos_of_me_async = on_photos_of_me.apply_async()

    top_friends = results['most_tagged_recently'].join_on_field(
        lambda x, y: x['count'] + y['count'],
        results['top_posters_from_year'],
        new_field_name='count',
        discard_orphans=False
    )

    # For each top friend, pull the photos they are tagged in
    # (in top friends order)
    # Just do them all since it doesn't involve another round trip to the server
    # Top friend photos are stored in a *list* so the order is known
    top_friend_photos = []
    for friend in top_friends.order_by('count'):
        friend_photos = [tag for tag in results['tagged_with_me']['tagged_with_me'].fields
                         if tag['subject']==friend['id']]
        if len(friend_photos) > TOP_FRIEND_MIN_PHOTOS:
            top_friend_photos.append(friend_photos)

    # For each group photo, grab its score from 'photos_of_me'
    group_photos = []
    for group_photo in results['tagged_with_me']['group_photos'].fields:
        group_photo_id = group_photo['id']
        if group_photo_id in results['photos_of_me'].fields_by_id:
            group_photos.append(results['photos_of_me'].fields_by_id[group_photo_id])
        else:
            logger.warn('Received a group photo %s that wasn\'t in \'photos_of_me\'. Odd.' % group_photo_id )
    # Sort by score
    group_photos.sort(key=lambda x: x['score'], reverse=True)


    # Serialize the lists
    rankings = PhotoRankings.objects.get(user=user)
    rankings.top_friends = top_friend_photos
    rankings.group_shots = group_photos
    rankings.save()

    results['top_friends'] = top_friend_photos
    results['on_photos_of_me_async'] = on_photos_of_me_async
    return results


@task.task()
def run_yearbook(user):
    # Create db model if needed
    rankings, created = PhotoRankings.objects.get_or_create(user=user)

    # Fire all tasks
    job = group([
        group([
            rt.subtask(kwargs={'task_cls': PhotosILikeTask, 'user_id': user.id}) |
                rt.subtask(kwargs={'task_cls': PhotosOfMeTask, 'user_id': user.id}),
            rt.subtask(kwargs={'task_cls': TaggedWithMeTask, 'user_id': user.id}) |
                get_most_tagged_recently.subtask(),
            rt.subtask(kwargs={'task_cls': TopPostersFromYearTask, 'user_id': user.id}),
        ]) | get_top_friends_and_groups.subtask((user,)),

        rt.subtask(kwargs={'task_cls': PostsFromYearTask, 'user_id': user.id}) |
            get_top_post_of_year.subtask((user, )),

        rt.subtask(kwargs={'task_cls': BirthdayPostsTask, 'user_id': user.id,
                           'init_args': {'birthday': user.profile.date_of_birth}}),
    ])
    job_async = job.apply_async()

    # Wait for everything to finish
    try:
        results = job_async.get()
        results = merge_dicts(*results)
        # Wait for the album photos subtask to finish
        results['on_photos_of_me_async'].get()
    except TimeoutError:
        # TODO handle the timeout
        pass

    # All fields in PhotoRankings are filled.
    # Assign photos to the Yearbook, avoiding duplicates
    try:
        old_yb = Yearbook.objects.get(owner=user)
        old_yb.delete()
    except Yearbook.DoesNotExist: pass
    yb = Yearbook(owner=user)

    # Grab top_post and birthday_posts from results
    yb.top_post = results['top_post']
    yb.birthday_posts = results['birthday_posts']

    # We go through the fields and assign the first unused photo to each field
    yb.top_photo = yb.get_first_unused_photo(rankings.top_photos)
    if rankings.gfbf_with:
        yb.gfbf_photo_1 = yb.get_first_unused_photo(rankings.gfbf_with)
        yb.gfbf_photo_2 = yb.get_first_unused_photo(rankings.gfbf_with)
        yb.gfbf_photo_3 = yb.get_first_unused_photo(rankings.gfbf_with)
        yb.gfbf_photo_4 = yb.get_first_unused_photo(rankings.gfbf_with)
    if rankings.family_with:
        yb.family_photo_1 = yb.get_first_unused_photo(rankings.family_with)
        yb.family_photo_2 = yb.get_first_unused_photo(rankings.family_with)
        yb.family_photo_3 = yb.get_first_unused_photo(rankings.family_with)
        yb.family_photo_4 = yb.get_first_unused_photo(rankings.family_with)
    yb.group_photo_1 = yb.get_first_unused_photo(rankings.group_shots)
    yb.group_photo_2 = yb.get_first_unused_photo(rankings.group_shots)
    yb.group_photo_3 = yb.get_first_unused_photo(rankings.group_shots)
    yb.group_photo_4 = yb.get_first_unused_photo(rankings.group_shots)
    yb.first_half_photo_1 = yb.get_first_unused_photo(rankings.top_photos_first_half)
    yb.first_half_photo_2 = yb.get_first_unused_photo(rankings.top_photos_first_half)
    yb.first_half_photo_3 = yb.get_first_unused_photo(rankings.top_photos_first_half)
    yb.second_half_photo_1 = yb.get_first_unused_photo(rankings.top_photos_second_half)
    yb.second_half_photo_2 = yb.get_first_unused_photo(rankings.top_photos_second_half)
    yb.second_half_photo_3 = yb.get_first_unused_photo(rankings.top_photos_second_half)

    # Top friends
    save_top_friends_unused_photos(user, rankings, yb)

    # Top albums
    save_top_albums_unused_photos(rankings, yb)

    # Back in time photos
    yb.back_in_time_photo_1 = yb.get_first_unused_photo(rankings.you_back_in_time_year_1)
    yb.back_in_time_photo_2 = yb.get_first_unused_photo(rankings.you_back_in_time_year_2)
    yb.back_in_time_photo_3 = yb.get_first_unused_photo(rankings.you_back_in_time_year_3)
    yb.back_in_time_photo_4 = yb.get_first_unused_photo(rankings.you_back_in_time_year_4)
    yb.back_in_time_photo_5 = yb.get_first_unused_photo(rankings.you_back_in_time_year_5)
    yb.back_in_time_photo_6 = yb.get_first_unused_photo(rankings.you_back_in_time_year_6)
    yb.back_in_time_photo_7 = yb.get_first_unused_photo(rankings.you_back_in_time_year_7)

    yb.save()
    logger.info('Yearbook created')


def save_top_friends_unused_photos(user, rankings, yearbook):
    # Exclude family and gf/bf
    exclude_ids = {family_member.facebook_id for family_member in user.family.all()}
    if user.profile.significant_other_id:
        exclude_ids.add(user.profile.significant_other_id)

    # If they have no family members or gf/bf. they get five friends
    num_top_friends = 5
    if rankings.gfbf_with:
        num_top_friends -= 1
    if rankings.family_with:
        num_top_friends -= 1

    top_friends_photos = []
    for friend_num in range(len(rankings.top_friends)):
        curr_friend = rankings.top_friends[friend_num]
        # curr_friend is a list of photo_tags
        if curr_friend[0]['subject'] in exclude_ids:
            continue
        # Find `n` unused photos of this person
        curr_friend_unused = yearbook.get_n_unused_photos(curr_friend, TOP_FRIEND_PHOTOS_TO_SHOW)
        if not curr_friend_unused or len(curr_friend_unused) < TOP_FRIEND_MIN_PHOTOS:
            continue
        top_friends_photos.append({'index': friend_num, 'photo_list': curr_friend_unused})
        if len(top_friends_photos) >= num_top_friends:
            break

    # Save the friend indices and lists of photos for each friend
    save_enumerated_fields(top_friends_photos, 'top_friend', yearbook)



def save_top_albums_unused_photos(rankings, yearbook):
    albums_to_show = []
    for album_num in range(len(rankings.top_albums)):
        curr_album = rankings.top_albums[album_num]
        # curr_album is a list of photo_tags
        # Find `n` unused photos from this album
        curr_album_unused = yearbook.get_n_unused_photos(curr_album, ALBUM_PHOTOS_TO_SHOW)
        if not curr_album_unused or len(curr_album_unused) < ALBUM_MIN_PHOTOS:
            continue
        albums_to_show.append({'index': album_num, 'photo_list': curr_album_unused})
        if len(albums_to_show) == NUM_TOP_ALBUMS:
            break

    # Sort albums by num. photos, if any returned less than 3
    # We want to see full albums first

    if len(albums_to_show) != NUM_TOP_ALBUMS:
        # We ran out of albums
        # TODO : pull more from server?
        pass

    # Save album indices and photos
    save_enumerated_fields(albums_to_show, 'top_album', yearbook)



def save_enumerated_fields(list_of_items, field_prefix, yearbook):
    """
    Saves fields of the form
        top_album_1     top_album_1_photo_1
        etc.
    """
    for item_field_num, item in enumerate(list_of_items):
        setattr(yearbook, '%s_%d' % (field_prefix, (item_field_num + 1)), item['index'])
        for photo_field_num, photo_index in enumerate(item['photo_list']):
            setattr(yearbook, '%s_%d_photo_%d' % (field_prefix, (item_field_num + 1), (photo_field_num + 1)), photo_index)
