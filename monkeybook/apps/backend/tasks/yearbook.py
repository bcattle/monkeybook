import logging, itertools
from collections import defaultdict, Counter
from celery import task, group, current_task
from django.db import transaction
from monkeybook.apps.backend.tasks.albums import pull_album_photos
from monkeybook.apps.core import bulk
from monkeybook.apps.core.utils import merge_dicts
from monkeybook.apps.backend.fql import PhotosOfMeTask, CommentsOnPhotosOfMeTask, \
    OwnerPostsFromYearTask, OthersPostsFromYearTask, ProfileFieldsTask, FamilyTask
from monkeybook.apps.backend.getter import FreqDistResultGetter, ResultGetter
from monkeybook.apps.backend.models import PhotoRankings, FacebookPhoto, Yearbook
from monkeybook.apps.backend.settings import *
from backend.tasks.fql import run_task as rt
from pytz import utc

logger = logging.getLogger(__name__)


@task.task(ignore_result=True)
def pull_user_profile(user):
    profile_task = ProfileFieldsTask()
    results = profile_task.run(user)
    profile_task.save_profile_fields(user, results['profile_fields'])


@task.task()
@transaction.commit_manually
def save_to_db(user, family, photos_of_me):
    FamilyTask().save_family(user, family)
    transaction.commit()

    bulk.insert_or_update_many(FacebookPhoto, photos_of_me)
    transaction.commit()


@task.task()
# @profileit('run_yearbook')
def run_yearbook(user, results):
    # Run separate, async tasks to facebook
    fql_job = group([
        rt.subtask(kwargs={'task_cls': PhotosOfMeTask,           'user_id': user.id}),
        rt.subtask(kwargs={'task_cls': CommentsOnPhotosOfMeTask, 'user_id': user.id}),
        rt.subtask(kwargs={'task_cls': OwnerPostsFromYearTask,   'user_id': user.id}),
        rt.subtask(kwargs={'task_cls': OthersPostsFromYearTask,  'user_id': user.id}),
        rt.subtask(kwargs={'task_cls': FamilyTask,               'user_id': user.id}),
    ])
    job_async = fql_job.apply_async()
    job_results = job_async.get()

    results = merge_dicts(results, *job_results)

    ## Results contains
    #   'get_friends'               all friends     (already saved to db)
    #   'tagged_with_me'            `subject, object_id, created` from tags of photos I am in
    #   'comments_on_photos_of_me'
    #   'others_posts_from_year'
    #   'owner_posts_from_year'
    #   'photos_of_me'

    # Toss any results in 'tagged_with_me' that aren't in 'photos_of_me'
    results['tagged_with_me'] = results['tagged_with_me'].filter(
        lambda x: x['object_id'] in results['photos_of_me'].ids
        )

    # Get number of people in each photo
    num_tags_by_photo_id = FreqDistResultGetter(results['tagged_with_me'], id_field='object_id')

    # Get list of people in each photo
    tagged_people_by_photo_id = defaultdict(list)
    for tag in results['tagged_with_me']:
        tagged_people_by_photo_id[tag['object_id']].append(tag['subject'])

    comments_by_photo_id = defaultdict(list)
    comments_score_by_user_id = defaultdict(lambda: 0)
    for comment in results['comments_on_photos_of_me']:
        # Get the comments in each photo
        comments_by_photo_id[comment['object_id']].append(comment)

        # Get the number of commments by each user, discounted by year
        comments_score_by_user_id[comment['fromid']] += \
            TOP_FRIEND_POINTS_FOR_PHOTO_COMMENT / max((THIS_YEAR.year - comment['time'].year + 1.0), 1.0)

    # Save the photos to the database
    photos_of_me = []
    for photo in results['photos_of_me']:
        photo_db = FacebookPhoto(
            facebook_id     = photo['id'],
            created         = photo['created'],
            people_in_photo = num_tags_by_photo_id.fields_by_id[photo['id']]['count'] + 1 \
                                if photo['id'] in num_tags_by_photo_id.ids else 0,
            height          = photo['height'],
            width           = photo['width'],
            fb_url          = photo['fb_url'],
            all_sizes       = photo['all_sizes'],
            comments        = comments_by_photo_id[photo['id']],    # it's a defaultdict
            caption         = photo['caption']
        )
        photos_of_me.append(photo_db)

    # Save photos, profile fields, and family to db
#    save_to_db.delay(user, profile_task, results['profile_fields'],
#                     family_task, results['family'], photos_of_me)
#    save_to_db.delay(user, family_task, results['family'], photos_of_me)
    save_to_db_async = save_to_db.delay(user, results['family'], photos_of_me)

    ## Calculate top friends

    # Combine the lists of posts
    all_posts_this_year = ResultGetter.from_fields(itertools.chain(
        results['others_posts_from_year'],
        results['owner_posts_from_year'],
    ))

    # Strip posts that have an attachment that is a photo?
#    .filter(lambda x: 'attachment' in x and 'fb_object_type' in x['attachment'] and x['attachment'])

    # Assign each friend points for each post they made
    posts_score_by_user_id = defaultdict(lambda: 0)
    for post in all_posts_this_year:
        # if 'score' not in post:
        #     post['score'] = 0
        # post['score'] += TOP_FRIEND_POINTS_FOR_POST
        posts_score_by_user_id[post['actor_id']] += TOP_FRIEND_POINTS_FOR_POST

    # Calculate photo score for each user, discounted by year
    tags_by_user_id = defaultdict(list)
    for tag in results['tagged_with_me']:
        tags_by_user_id[tag['subject']].append(tag)

    photos_score_by_user_id = defaultdict(lambda: 0.0)
    for friend_id, tag_list in tags_by_user_id.items():
        for tag in tag_list:
            photo_id = tag['object_id']
            peeps_in_photo = num_tags_by_photo_id.fields_by_id[photo_id]['count'] + 1   # num tags + me
            photo = results['photos_of_me'].fields_by_id[photo_id]
#            photo_age = 2012 - photo['created'].year + 1.0
            photo_age = datetime.date.today().year - photo['created'].year + 1.0
            if peeps_in_photo == 2:
                photos_score_by_user_id[friend_id] += TOP_FRIEND_POINTS_FOR_PHOTO_OF_2 / photo_age
            elif peeps_in_photo == 3:
                photos_score_by_user_id[friend_id] += TOP_FRIEND_POINTS_FOR_PHOTO_OF_3 / photo_age
            elif peeps_in_photo >= 4:
                photos_score_by_user_id[friend_id] += TOP_FRIEND_POINTS_FOR_PHOTO_OF_4 / photo_age

    # Add em up
    top_friend_ids = (set(comments_score_by_user_id.keys()) | set(posts_score_by_user_id.keys())
        | set(photos_score_by_user_id))
    top_friend_ids.remove(user.profile.facebook_id)
    top_friend_score_by_id = {
        friend_id: comments_score_by_user_id[friend_id] + posts_score_by_user_id[friend_id] +
                   photos_score_by_user_id[friend_id]
        for friend_id in top_friend_ids
    }
    top_20_friends_score_by_id = dict(sorted(top_friend_score_by_id.items(), key=lambda x: x[1], reverse=True)[:20])

    ## Calculate top photos

    # For each photo, get the number of top friends in the photo
    num_top_friends_by_photo_id = defaultdict(lambda: 0)
    for tag in results['tagged_with_me']:
        if tag['subject'] in top_friend_ids:
            points = 1
            # Double points if the user in top-20
            if tag['subject'] in top_20_friends_score_by_id:
                points += 1
            num_top_friends_by_photo_id[tag['object_id']] += points

    # Photos of all time
    top_photo_score_by_id = {}
    for photo in results['photos_of_me']:
        # How many comments by friends of mine?
        comments_from_friends = 0
        for comment in comments_by_photo_id[photo['id']]:
            if comment['fromid'] in results['get_friends'].ids:
                comments_from_friends += 1

        score = ((TOP_PHOTO_POINTS_FOR_TOP_FRIENDS * num_top_friends_by_photo_id[photo['id']] +
                  TOP_PHOTO_POINTS_FOR_COMMENT * comments_from_friends +
                  TOP_PHOTO_POINTS_FOR_LIKE * photo['like_count']) /
                      max(num_tags_by_photo_id.fields_by_id[photo['id']]['count'] - 2.0, 1.0)
                          if photo['id'] in num_tags_by_photo_id.fields_by_id else 1)

        top_photo_score_by_id[photo['id']] = photo['score'] = score

    # Update list to have scores
    tags_by_user_id = defaultdict(list)
    for tag in results['tagged_with_me']:
        tags_by_user_id[tag['subject']].append(tag)

    ## Calculate top group photos
    # group_photos_this_year is only 1 for me
    group_photos = results['photos_of_me'] \
        .filter(lambda x: x['id'] in num_tags_by_photo_id.fields_by_id) \
        .filter(lambda x: num_tags_by_photo_id.fields_by_id[x['id']]['count'] >= GROUP_PHOTO_IS)\
        .filter(lambda x: x['created'] > GROUP_PHOTO_CUTOFF)

    group_photo_score_by_id = {}
    for photo in group_photos:
        score = GROUP_PHOTO_POINTS_FOR_TOP_FRIENDS * num_top_friends_by_photo_id[photo['id']] +\
                GROUP_PHOTO_POINTS_FOR_COMMENT * photo['comment_count'] +\
                GROUP_PHOTO_POINTS_FOR_LIKE * photo['like_count']
        group_photo_score_by_id[photo['id']] = {'score': score, 'created': photo['created']}

    ## Calculate top albums
    album_score_and_date_by_id = defaultdict(lambda: {'score': 0, 'created': None})
    for photo in results['photos_of_me']:
        album_score_and_date_by_id[photo['album_object_id']]['score'] += photo['score']
        # Also tag with the date
        album_score_and_date_by_id[photo['album_object_id']]['created'] = photo['created']

    ## Calculate top post
    for post in all_posts_this_year:
        top_friend_comments = 0
        for comment in post['comments']['comment_list']:
            if comment['fromid'] in top_friend_ids:
                top_friend_comments += 1
        post['score'] = \
            (COMMENT_POINTS_FOR_MADE_BY_ME * 1 if post['actor_id'] == user.profile.facebook_id else 0) +\
            COMMENT_POINTS_FOR_COMMENT * top_friend_comments + \
            COMMENT_POINTS_FOR_LIKE * post['like_count']

    ## Pull out birthday posts
    birthday_posts = []
    if user.profile.date_of_birth:
        birthday = user.profile.date_of_birth
        birthday_this_year = datetime.datetime(2012, birthday.month, birthday.day, 0, 0, 0, tzinfo=utc)
        start_time = birthday_this_year - datetime.timedelta(days=1)
        end_time = birthday_this_year + datetime.timedelta(days=3)
        birthday_posts = all_posts_this_year.filter(
            lambda x: start_time < x['created_time'] < end_time and x['message'] and x['actor_id'] in results['get_friends'].ids
        )

    ## Save fields to the PhotoRankings class

    rankings = PhotoRankings(user=user)
#    rankings, created = PhotoRankings.objects.get_or_create(user=user)

    top_photos_this_year = results['photos_of_me'].filter(lambda x: x['created'] > THIS_YEAR)\
        .order_by('score')

    # If they don't have enough photos this year, bail out of the yearbook process
    if len(top_photos_this_year) < MIN_TOP_PHOTOS_FOR_BOOK:
        current_task.update_state(state='NOT_ENOUGH_PHOTOS')
        # This is a hack because celery overwrites the task state when you return
        # could also use an `after_return` handler, see http://bit.ly/16U6YKv
        return 'NOT_ENOUGH_PHOTOS'

    rankings.top_photos = top_photos_this_year
    rankings.group_shots = [
        k for k, v in sorted(
            group_photo_score_by_id.items(),
            # Sort by year, score
            key=lambda x: (x[1]['created'].year, x[1]['score']),
            reverse=True
        )
    ]
    rankings.top_posts = all_posts_this_year.order_by('score')[:10]

    # Back in time
    max_year, photos_of_me_by_year = results['photos_of_me'].bucket_by_year()
    years = list(sorted(photos_of_me_by_year.keys(), reverse=True))
    back_in_time = []
    for index, year in enumerate(years[1:NUM_PREV_YEARS + 1]):
        year_photo_ids = []
        for photo in photos_of_me_by_year[year].order_by('score'):
            year_photo_ids.append(photo['id'])
        back_in_time.append(year_photo_ids)
    rankings.back_in_time = back_in_time

    ## Assign photos to the Yearbook, avoiding duplicates
    #    try:
    #        old_yb = Yearbook.objects.get(rankings=rankings)
    #        old_yb.delete()
    #    except Yearbook.DoesNotExist: pass
    yb = Yearbook(rankings=rankings)
    yb.top_post = 0
    yb.birthday_posts = birthday_posts.fields

    yb.top_photo_1 = yb.get_first_unused_photo_landscape(rankings.top_photos)           # landscape
    yb.top_photo_2 = yb.get_first_unused_photo(rankings.top_photos)
    yb.top_photo_3 = yb.get_first_unused_photo(rankings.top_photos)
    yb.top_photo_4 = yb.get_first_unused_photo(rankings.top_photos)
    yb.top_photo_5 = yb.get_first_unused_photo(rankings.top_photos)

    # `assign_group_photos` uses FacebookPhoto classes to determine portrait/landscape
    # make sure they finished saving to the db
    # print 'save_to_db state: %s' % save_to_db_async.state
    save_to_db_async.get()

    # Assign the group photos from different albums, if possible
    # Make one pass assigning from different albums,
    # then a second filling in the gaps
#    assigned_group_photos = assign_group_photos(yb, rankings, results['photos_of_me'], do_unique_albums=True)
#    if assigned_group_photos < NUM_GROUP_PHOTOS:
#        assign_group_photos(yb, rankings, results['photos_of_me'], do_unique_albums=False)

    ## Top friends
    # Do this after we assign the top photos and top group photos,
    # so we can make sure there are enough unused photos of them

    # We need to make sure the user exists in the db
    # Users that came back from the db are still in results['get_friends']
    saved_friends_ids = results['get_friends'].ids

    family_ids = user.family.all().values_list('facebook_id', flat=True)
    top_friend_ids = []
    gfbf_added = False
    for user_id, score in sorted(top_friend_score_by_id.items(), key=lambda x: x[1], reverse=True):
        if yb.num_unused_photos(tags_by_user_id[user_id]) >= TOP_FRIEND_MIN_UNUSED_PHOTOS and user_id in saved_friends_ids:
            # If user is family or gfbf, insert at front
            if user_id == user.profile.significant_other_id:
                top_friend_ids.insert(0, user_id)
                gfbf_added = True
            elif user_id in family_ids:
                top_friend_ids.insert(1 if gfbf_added else 0, user_id)
            else:
                top_friend_ids.append(user_id)

    # Need to build another list that combines tag and photo score
    rankings.top_friends_ids = top_friend_ids[:NUM_TOP_FRIENDS_STORED]
    top_friends_photos = []
    for friend_id in top_friend_ids:
        friend_tags = tags_by_user_id[friend_id]
        top_friend_photos = []
        for tag in friend_tags:
            tag_id = tag['object_id']
            photo = results['photos_of_me'].fields_by_id[tag_id]
            top_friend_photos.append({'id': tag_id, 'score': top_photo_score_by_id[tag_id],
                                      'width': photo['width'], 'height': photo['height']})
        top_friend_photos.sort(key=lambda x: x['score'], reverse=True)
        top_friends_photos.append(top_friend_photos)
    rankings.top_friends_photos = top_friends_photos

    ## Assign the top friends
#    used_albums = []
    for index in range(min(NUM_TOP_FRIENDS, len(top_friend_ids))):
        # Index
        setattr(yb, 'top_friend_%d' % (index + 1), index)
        # Friend stat
        if top_friend_ids[index] == user.profile.significant_other_id:
            friend_stat = SIGNIFICANT_OTHER_STAT
        elif top_friend_ids[index] in family_ids:
            friend_stat = FAMILY_STAT
        else:
            num_tags = len(rankings.top_friends_photos[index])
            friend_stat = u'Tagged in %d photo%s with you' % (num_tags, 's' if num_tags > 1 else '')
        setattr(yb, 'top_friend_%d_stat' % (index + 1), friend_stat)
        # Set photo
#        tf_photo_index = yb.get_first_unused_photo(rankings.top_friends_photos[index])
        tf_photo_index = yb.get_first_unused_photo_landscape(rankings.top_friends_photos[index])
        setattr(yb, 'top_friend_%d_photo_1' % (index + 1), tf_photo_index)
        # If photo was portrait, grab another one
#        tf_photo_id = rankings.top_friends_photos[index][tf_photo_index]['id']
#        tf_photo = results['photos_of_me'].fields_by_id[tf_photo_id]
#        if tf_photo['width'] / float(tf_photo['height']) < HIGHEST_SQUARE_ASPECT_RATIO:
#            tf_photo_index_2 = yb.get_first_unused_photo(rankings.top_friends_photos[index])
#            setattr(yb, 'top_friend_%d_photo_2' % (index + 1), tf_photo_index_2)

    ## Top albums

    # Start pulling album names, photos
    # Can't pickle defaultdict? so just call it here, wouldn't save us much time anyway
    #    pull_albums_async = pull_album_photos.delay(user, album_score_and_date_by_id)
    #    album_photos_by_score, albums_ranked = pull_albums_async.get()
    album_photos_by_score, albums_ranked = pull_album_photos(user, album_score_and_date_by_id)
    rankings.top_albums_photos = album_photos_by_score
    rankings.top_albums_ranked = albums_ranked

    albums_assigned = 0
    all_top_albums = rankings.top_albums_photos[:]
    curr_album_index = -1
    while all_top_albums:
        curr_album = all_top_albums.pop(0)
        curr_album_index += 1
        photos_to_show = []
        no_more_pics_of_user = False
        while True:
            if len(photos_to_show) < PICS_OF_USER_TO_PROMOTE and not no_more_pics_of_user:
                # Want a pic of the user, loop through album photos looking for one
                photo_of_user = get_next_unused_photo_of_user(
                    yb,
                    curr_album,
                    results['photos_of_me'],
                    used_indices=photos_to_show
                )
                if photo_of_user:
                    photos_to_show.append(photo_of_user)
                else:
                    # No more pics of user, just take the next highest unused photo
                    no_more_pics_of_user = True
            else:
                next_photo = yb.get_first_unused_photo(curr_album, used_indices=photos_to_show)
                if next_photo is not None:
                    photos_to_show.append(next_photo)
                else:
                    # No photos left, break
                    break
            if len(photos_to_show) >= ALBUM_PHOTOS_TO_SHOW:
                break
        if len(photos_to_show) < ALBUM_MIN_PHOTOS:
            # Didn't have enough photos, try the next album
            continue

        # Save the fields
        album_str = 'top_album_%d' % (albums_assigned + 1)
        setattr(yb, album_str, curr_album_index)
        for field_num in range(len(photos_to_show)):
            setattr(yb, album_str + '_photo_%d' % (field_num + 1), photos_to_show[field_num])
        albums_assigned += 1
        if albums_assigned >= NUM_TOP_ALBUMS:
            break

    ## Throughout the year photos

    yb.year_photo_1 = yb.get_first_unused_photo_landscape(rankings.top_photos)
    yb.year_photo_2 = yb.get_first_unused_photo(rankings.top_photos)
    yb.year_photo_6 = get_unused_if_portrait(yb.year_photo_2, rankings.top_photos, yb, results['photos_of_me'])
    yb.year_photo_3 = yb.get_first_unused_photo(rankings.top_photos)
    yb.year_photo_7 = get_unused_if_portrait(yb.year_photo_3, rankings.top_photos, yb, results['photos_of_me'])
    yb.year_photo_4 = yb.get_first_unused_photo(rankings.top_photos)
    yb.year_photo_8 = get_unused_if_portrait(yb.year_photo_4, rankings.top_photos, yb, results['photos_of_me'])
    yb.year_photo_5 = yb.get_first_unused_photo(rankings.top_photos)
    yb.year_photo_9 = get_unused_if_portrait(yb.year_photo_5, rankings.top_photos, yb, results['photos_of_me'])

    ## Back in time photos

    years_to_show = []
    for year_index, year in enumerate(back_in_time):
        curr_year_unused = yb.get_first_unused_photo(year)
        if curr_year_unused is None:
            continue
        years_to_show.append({'year_index': year_index, 'photo_index': curr_year_unused})
        if len(years_to_show) > NUM_PREV_YEARS:
            break

    # Special case: if only found one year, pull an additional photo from that year
    if len(years_to_show) == 1:
        that_year_index = years_to_show[0]['index']
        unused_photo_2 = yb.get_first_unused_photo(back_in_time[that_year_index])
        if unused_photo_2 is not None:
            years_to_show.append({'year_index': that_year_index, 'photo_index': unused_photo_2})

    # Save
    for year_num in range(len(years_to_show)):
        field_str = 'back_in_time_%d' % (year_num + 1)
        setattr(yb, field_str, years_to_show[year_num]['year_index'])
        setattr(yb, field_str + '_photo_1', years_to_show[year_num]['photo_index'])

    # Tabulate the list of all friends tagged in the book and store
    all_photos = yb._get_all_used_ids()
    all_tagged_people = itertools.chain(*[
        tagged_people_by_photo_id[photo_id] for photo_id in all_photos
    ])
    tagged_people_count = Counter(all_tagged_people)
    yb.friends_in_book = tagged_people_count.most_common()

    # Save everything
    rankings.save()
    yb.rankings = rankings
    yb.save()

    # Initiate a task to start downloading user's yearbook phointos?
    return yb

#    except FacebookSSLError, exc:
#        logger.error('run_yearbook: FacebookSSLError, retrying.')
#        raise self.retry(exc=exc)


def get_unused_if_portrait(photo_index, photo_list, yearbook, photos_of_me):
    photo_id = yearbook._get_id_from_dict_or_int(photo_list[photo_index])
    photo = photos_of_me.fields_by_id[photo_id]
    if photo['width'] / float(photo['height']) < HIGHEST_SQUARE_ASPECT_RATIO:
        return yearbook.get_first_unused_photo(photo_list)
    return None


def get_next_unused_photo_of_user(yearbook, photo_list, photos_of_me, used_indices=None):
    used_indices = used_indices or []
    list_to_loop = photo_list.items() if hasattr(photo_list, 'items') else photo_list
    for photo_index, photo in enumerate(list_to_loop):
        if photo_index in used_indices:
            continue
        photo_id = photo['id'] if hasattr(photo, 'keys') else photo
        is_used = yearbook.photo_is_used(photo)
        of_me = photo_id in photos_of_me.ids
        if not is_used and of_me:
            return photo_index
    return None


def assign_group_photos(yearbook, rankings, photos_of_me, do_unique_albums=False):
    assigned_group_photos = 0
    assigned_album_ids = []
    skipped_photo_indices = []
    photo_index = None
    while True:
        if not assigned_group_photos:
            # The first photo should be landscape
            photo_index, photo_id = yearbook.get_first_unused_photo_landscape(rankings.group_shots, return_id=True)
        if assigned_group_photos > 0 or photo_index is None:
            # Subsequent iterations or it failed
            photo_index, photo_id = yearbook.get_first_unused_photo(rankings.group_shots, used_indices=skipped_photo_indices, return_id=True)
        if photo_index is not None:
            if do_unique_albums:
                # Do we already have a photo from this album?
                album_id = photos_of_me.fields_by_id[photo_id]['album_object_id']
                if album_id in assigned_album_ids:
                    # Assign the photo id to the "skipped" list
                    skipped_photo_indices.append(photo_index)
                    continue
                else:
                    assigned_album_ids.append(album_id)
            # Actually assign the photo
            setattr(yearbook, 'group_photo_%d' % (assigned_group_photos + 1), photo_index)
            assigned_group_photos += 1
        if assigned_group_photos >= NUM_GROUP_PHOTOS or photo_index is None:
            # We have enough or no unused photo, roll on
            break
    return assigned_group_photos

