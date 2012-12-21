import logging
from celery import task, group
from backend.tasks.fql import run_task as rt
from voomza.apps.backend.fql.photos import PhotosOfMeTask, CommentsOnPhotosOfMeTask
from voomza.apps.backend.fql.posts import OwnerPostsFromYearTask, OthersPostsFromYearTask
from voomza.apps.backend.models import PhotoRankings
from voomza.apps.core.utils import timeit, merge_dicts

logger = logging.getLogger(__name__)


@timeit
@task.task()
def run_yearbook(user, results):
    # Results contains
    #   'get_friends'       all frends
    #   'tagged_with_me'    `subject, object_id, created` from tags from a photo I too am in
    job = group([
            rt.subtask(kwargs={'task_cls': PhotosOfMeTask, 'user_id': user.id}),
            rt.subtask(kwargs={'task_cls': CommentsOnPhotosOfMeTask, 'user_id': user.id}),
            rt.subtask(kwargs={'task_cls': OwnerPostsFromYearTask, 'user_id': user.id}),
            rt.subtask(kwargs={'task_cls': OthersPostsFromYearTask, 'user_id': user.id}),
        ])

    # Run
    job_async = job.apply_async()
    job_results = job_async.get()

    results = merge_dicts(results, *job_results)

    import ipdb
    ipdb.set_trace()

    # Find the top post
    # Get it

    # Calculate top friends and top photos




#    job = group([
#        group([
#            rt.subtask(kwargs={'task_cls': PhotosILikeTask, 'user_id': user.id}) |
#            rt.subtask(kwargs={'task_cls': PhotosOfMeTask, 'user_id': user.id}),
#            rt.subtask(kwargs={'task_cls': TaggedWithMeTask, 'user_id': user.id}) |
#            get_most_tagged.subtask(),
#            rt.subtask(kwargs={'task_cls': TopPostersFromYearTask, 'user_id': user.id}),
#            ]) | get_top_friends_and_groups.subtask((user,)),
#
#        rt.subtask(kwargs={'task_cls': PostsFromYearTask, 'user_id': user.id}) |
#        get_top_post_of_year.subtask((user, )),
#
#        rt.subtask(kwargs={'task_cls': BirthdayPostsTask, 'user_id': user.id,
#                           'init_args': {'birthday': user.profile.date_of_birth}}),
#        get_photo_comments.subtask((user,)),
#        ])

    # TODO: fix this so it doesn't choke if something returns None or an exception is thrown
    results = merge_dicts(*results)
    # Wait for the album photos subtask to finish
    subtask_results = results['on_photos_of_me_async'].get()
    results = merge_dicts(results, *subtask_results)

    # Save fields to the PhotoRankings class
    rankings = PhotoRankings(user=user)
    #    rankings, created = PhotoRankings.objects.get_or_create(user=user)

    # TODO prob want to fail gracefully if a key doesn't exist
    rankings.top_photos = results['photos_of_me_this_year']
    rankings.top_photos_first_half = results['top_photos_of_me_first_half']
    rankings.top_photos_second_half = results['top_photos_of_me_second_half']

    rankings.group_shots = results['group_shots']
    rankings.top_friends = results['top_friends']
    rankings.top_albums = results['top_albums_photos']
    rankings.top_albums_info = results['top_albums']
    rankings.back_in_time = results['back_in_time']

    rankings.save()


    # All fields in PhotoRankings are filled.
    # Assign photos to the Yearbook, avoiding duplicates
    #    try:
    #        old_yb = Yearbook.objects.get(rankings=rankings)
    #        old_yb.delete()
    #    except Yearbook.DoesNotExist: pass
    yb = Yearbook(rankings=rankings)

    # Grab top_post and birthday_posts from results
    yb.top_post = results['top_post']
    yb.birthday_posts = results['birthday_posts']

    # We go through the fields and assign the first unused photo to each field
    yb.top_photo_1 = yb.get_first_unused_photo_landscape(rankings.top_photos)           # landscape
    yb.top_photo_2 = yb.get_first_unused_photo(rankings.top_photos)
    yb.top_photo_3 = yb.get_first_unused_photo(rankings.top_photos)
    yb.top_photo_4 = yb.get_first_unused_photo(rankings.top_photos)
    yb.top_photo_5 = yb.get_first_unused_photo(rankings.top_photos)
    yb.first_half_photo_1 = yb.get_first_unused_photo_landscape(rankings.top_photos_first_half)     # landscape
    yb.first_half_photo_2, fh_photo_2_id = yb.get_first_unused_photo(rankings.top_photos_first_half, return_id=True)
    yb.first_half_photo_3, fh_photo_3_id = yb.get_first_unused_photo(rankings.top_photos_first_half, return_id=True)

    # If #2 was portrait, try to pull a #4 that is also portrait
    try:
        fh_photo_2_db = FacebookPhoto.objects.get(facebook_id=fh_photo_2_id)
        if fh_photo_2_db.is_portrait():
            yb.first_half_photo_4 = yb.get_first_unused_photo_portrait(rankings.top_photos_first_half)
    except FacebookPhoto.DoesNotExist: pass

    # If #3 was portrait, try to pull a #4 that is also portrait
    try:
        fh_photo_3_db = FacebookPhoto.objects.get(facebook_id=fh_photo_3_id)
        if fh_photo_3_db.is_portrait():
            yb.first_half_photo_5 = yb.get_first_unused_photo_portrait(rankings.top_photos_first_half)
    except FacebookPhoto.DoesNotExist: pass

    yb.second_half_photo_1 = yb.get_first_unused_photo_landscape(rankings.top_photos_second_half)   # landscape
    yb.second_half_photo_2, sh_photo_2_id = yb.get_first_unused_photo(rankings.top_photos_second_half, return_id=True)
    yb.second_half_photo_3, sh_photo_3_id = yb.get_first_unused_photo(rankings.top_photos_second_half, return_id=True)

    # If #2 was portrait, try to pull a #4 that is also portrait
    try:
        sh_photo_2_db = FacebookPhoto.objects.get(facebook_id=sh_photo_2_id)
        if sh_photo_2_db.is_portrait():
            yb.first_half_photo_4 = yb.get_first_unused_photo_portrait(rankings.top_photos_first_half)
    except FacebookPhoto.DoesNotExist: pass

    # If #3 was portrait, try to pull a #4 that is also portrait
    try:
        sh_photo_3_db = FacebookPhoto.objects.get(facebook_id=sh_photo_3_id)
        if sh_photo_3_db.is_portrait():
            yb.first_half_photo_5 = yb.get_first_unused_photo_portrait(rankings.top_photos_first_half)
    except FacebookPhoto.DoesNotExist: pass

    yb.group_photo_1 = yb.get_first_unused_photo_landscape(rankings.group_shots)            # landscape
    #    yb.group_photo_2 = yb.get_first_unused_photo(rankings.group_shots)
    #    yb.group_photo_3 = yb.get_first_unused_photo(rankings.group_shots)

    # Top friends
    save_top_friends_unused_photos(user, yb, results['most_tagged'])
    # Top albums
    save_top_albums_unused_photos(yb)
    # Back in time photos
    save_back_in_time_unused_photos(yb)

    # Save the runtime
    yb.save()

    # Initiate a task to start downloading user's yearbook photos?

    return yb


def save_top_friends_unused_photos(user, yearbook, most_tagged):
    family_ids = [family_member.facebook_id for family_member in user.family.all()]
    top_friends_photos = []
    for friend_num in range(len(yearbook.rankings.top_friends)):
        curr_friend = yearbook.rankings.top_friends[friend_num]
        # curr_friend is a list of photo_tags
        # Find `n` unused photos of this person
        curr_friend_unused = yearbook.get_n_unused_photos(curr_friend, TOP_FRIEND_PHOTOS_TO_SHOW)
        if curr_friend_unused is None or len(curr_friend_unused) < TOP_FRIEND_MIN_PHOTOS:
            continue
            # Friend "stats"
        curr_friend_id = curr_friend[0]['subject']
        if curr_friend_id == user.profile.significant_other_id:
            top_friend_stat = SIGNIFICANT_OTHER_STAT
        elif curr_friend_id in family_ids:
            top_friend_stat = FAMILY_STAT
        else:
            tag_count = most_tagged.fields_by_id[curr_friend_id]['count']
            top_friend_stat = u'Tagged in %d photo%s with you' % (tag_count, 's' if tag_count > 1 else '')
        top_friends_photos.append({'index': friend_num, 'photo_list': curr_friend_unused, 'stat': top_friend_stat})
        if len(top_friends_photos) >= NUM_TOP_FRIENDS:
            break

    # Save the friend indices and lists of photos for each friend
    save_enumerated_fields(top_friends_photos, 'top_friend', yearbook)
    # Save the friend stats
    for top_friend_num, top_friend in enumerate(top_friends_photos):
        setattr(yearbook, 'top_friend_%d_stat' % (top_friend_num + 1), top_friend['stat'])


def save_top_albums_unused_photos(yearbook):
    albums_to_show = []
    for album_num in range(len(yearbook.rankings.top_albums)):
        curr_album = yearbook.rankings.top_albums[album_num]
        # curr_album is a list of photo_tags
        # Find `n` unused photos from this album
        curr_album_unused = yearbook.get_n_unused_photos(curr_album, ALBUM_PHOTOS_TO_SHOW)
        if curr_album_unused is None or len(curr_album_unused) < ALBUM_MIN_PHOTOS:
            continue
        albums_to_show.append({'index': album_num, 'photo_list': curr_album_unused})
        if len(albums_to_show) == NUM_TOP_ALBUMS:
            break

    # TODO: sort albums by num. photos, if any returned less than 3
    # We want to see full albums first

    if len(albums_to_show) != NUM_TOP_ALBUMS:
        # We ran out of albums
        # TODO : pull more from server?
        pass

    # Save album indices and photos
    save_enumerated_fields(albums_to_show, 'top_album', yearbook)


def save_back_in_time_unused_photos(yearbook):
    years_to_show = []
    for year_number in range(len(yearbook.rankings.back_in_time)):
        curr_year = yearbook.rankings.back_in_time[year_number]
        # Find an unused photo from `curr_year`
        curr_year_unused = yearbook.get_n_unused_photos(curr_year, 1)
        if curr_year_unused is None:
            continue
        years_to_show.append({'index': year_number, 'photo_list': curr_year_unused})
        if len(years_to_show) > NUM_PREV_YEARS:
            break

    # Special case: if only found one year, pull an additional photo from that year
    if len(years_to_show) == 1:
        that_year_index = years_to_show[0]['index']
        unused_photo_2 = yearbook.get_first_unused_photo(yearbook.rankings.back_in_time[that_year_index])
        if unused_photo_2 is not None:
            years_to_show[0]['photo_list'].append(unused_photo_2)

    save_enumerated_fields(years_to_show, 'back_in_time', yearbook)


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
