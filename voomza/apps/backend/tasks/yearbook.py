import logging, itertools
from collections import defaultdict
from celery import task
from django.db import transaction
from voomza.apps.backend.tasks.albums import pull_album_photos
from voomza.apps.core import bulk
from voomza.apps.core.utils import timeit, merge_dicts
from voomza.apps.backend.fql import FqlTaskPipeline, PhotosOfMeTask, \
    CommentsOnPhotosOfMeTask, OwnerPostsFromYearTask, OthersPostsFromYearTask, \
    ProfileFieldsTask, FamilyTask
from voomza.apps.backend.getter import FreqDistResultGetter, ResultGetter
from voomza.apps.backend.models import PhotoRankings, FacebookPhoto, Yearbook
from voomza.apps.backend.settings import *
from backend.tasks.fql import run_task as rt

logger = logging.getLogger(__name__)


@task.task(ignore_result=True)
@transaction.commit_manually
def save_to_db(user, profile_task, profile_fields, family_task, family, photos_of_me):
    profile_task.save_profile_fields(user, profile_fields)
    transaction.commit()

    family_task.save_family(user, family)
    transaction.commit()

    bulk.insert_or_update_many(FacebookPhoto, photos_of_me)
    transaction.commit()


@task.task()
@timeit
def run_yearbook(user, results):
    profile_task = ProfileFieldsTask()
    family_task = FamilyTask()

    class YearbookPipeline(FqlTaskPipeline):
        class Meta:
            tasks = [
                PhotosOfMeTask(),
                CommentsOnPhotosOfMeTask(),
                OwnerPostsFromYearTask(),
                OthersPostsFromYearTask(),
                profile_task,
                family_task
            ]

    pipeline = YearbookPipeline(user)
    pipe_results = pipeline.run()
    results = merge_dicts(results, pipe_results)

    ## Results contains
    #   'get_friends'               all friends     (already saved to db)
    #   'tagged_with_me'            `subject, object_id, created` from tags of photos I am in
    #   'comments_on_photos_of_me'
    #   'others_posts_from_year'
    #   'owner_posts_from_year'
    #   'photos_of_me'

    # Get number of people in each photo
    num_tags_by_photo_id = FreqDistResultGetter(results['tagged_with_me'], id_field='object_id')

    comments_by_photo_id = defaultdict(list)
    for comment in results['comments_on_photos_of_me'].fields:
        comments_by_photo_id[comment['object_id']].append(comment)

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
            comments        = comments_by_photo_id[photo['id']],    # it's a defaultdict
            caption         = photo['caption']
        )
        photos_of_me.append(photo_db)

    # Save photos, profile fields, and family to db
    save_to_db.delay(user, profile_task, results['profile_fields'],
                     family_task, results['family'], photos_of_me)

    ## Calculate top friends

    # Get the number of commments by each user, discounted by year
    comments_score_by_user_id = defaultdict(lambda: 0)
    for comment in results['comments_on_photos_of_me']:
        comments_score_by_user_id[comment['fromid']] += \
            TOP_FRIEND_POINTS_FOR_PHOTO_COMMENT / (2012 - comment['time'].year + 1.0)

    # Combine the lists of posts
    all_posts_this_year = ResultGetter.from_fields(itertools.chain(
        results['others_posts_from_year'],
        results['owner_posts_from_year'],
    ))

    # Strip posts that have an attachment that is a photo?
#    .filter(lambda x: 'attachment' in x and 'fb_object_type' in x['attachment'] and x['attachment'])

    posts_score_by_user_id = defaultdict(lambda: 0)
    for post in all_posts_this_year:
        posts_score_by_user_id[post['actor_id']] += TOP_FRIEND_POINTS_FOR_POST

    # Calculate photo score for each user, discounted by year
    tags_by_user_id = defaultdict(list)
    for tag in results['tagged_with_me']:
        tags_by_user_id[tag['subject']].append(tag)

    photos_score_by_user_id = defaultdict(lambda: 0)
    for friend_id, tag_list in tags_by_user_id.items():
        for tag in tag_list:
            photo_id = tag['object_id']
            peeps_in_photo = num_tags_by_photo_id.fields_by_id[photo_id]['count'] + 1   # num tags + me
            photo = results['photos_of_me'].fields_by_id[photo_id]
            photo_age = 2012 - photo['created'].year + 1.0
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
        friend_id: comments_score_by_user_id[friend_id] + posts_score_by_user_id[friend_id] +\
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
                      max(num_tags_by_photo_id.fields_by_id[photo['id']]['count'] - 3.0, 1.0)
                          if photo['id'] in num_tags_by_photo_id.fields_by_id else 1)

        top_photo_score_by_id[photo['id']] = photo['score'] = score


    ## Calculate top group photos
    group_photos = results['photos_of_me'] \
        .filter(lambda x: x['id'] in num_tags_by_photo_id.fields_by_id) \
        .filter(lambda x: num_tags_by_photo_id.fields_by_id[x['id']]['count'] >= GROUP_PHOTO_IS)

    group_photo_score_by_id = {}
    for photo in group_photos:
        score = GROUP_PHOTO_POINTS_FOR_TOP_FRIENDS * num_top_friends_by_photo_id[photo['id']] +\
                GROUP_PHOTO_POINTS_FOR_COMMENT * photo['comment_count'] +\
                GROUP_PHOTO_POINTS_FOR_LIKE * photo['like_count']
        group_photo_score_by_id[photo['id']] = score

    ## Calculate top albums
    album_score_and_date_by_id = defaultdict(lambda: {'score': 0, 'created': None})
    for photo in results['photos_of_me']:
        album_score_and_date_by_id[photo['album_object_id']]['score'] += photo['score']
        # Also tag with the date
        album_score_and_date_by_id[photo['album_object_id']]['created'] = photo['created']

    # Start pulling album names, photos
    # Can't pickle defaultdict? so just call it here, wouldn't save us much time anyway
#    pull_albums_async = pull_album_photos.delay(user, album_score_and_date_by_id)
#    album_photos_by_score, albums_ranked = pull_albums_async.get()
    album_photos_by_score, albums_ranked = pull_album_photos(user, album_score_and_date_by_id)

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
        birthday_this_year = datetime.datetime(datetime.date.today().year, birthday.month, birthday.day, 0, 0, 0, tzinfo=utc)
        start_time = birthday_this_year - datetime.timedelta(days=1)
        end_time = birthday_this_year + datetime.timedelta(days=3)
        birthday_posts = all_posts_this_year.filter(
            lambda x: start_time < x['created_time'] < end_time and x['message']
        )


    ## Save fields to the PhotoRankings class
    rankings = PhotoRankings(user=user)
#    rankings, created = PhotoRankings.objects.get_or_create(user=user)

    rankings.top_photos = [k for k,v in sorted(top_photo_score_by_id.items(), key=lambda x: x[1], reverse=True)]
    rankings.group_shots = [k for k,v in sorted(group_photo_score_by_id.items(), key=lambda x: x[1], reverse=True)]
    rankings.top_albums_photos = album_photos_by_score
    rankings.top_albums_ranked = albums_ranked

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

    import ipdb
    ipdb.set_trace()

    ## Assign photos to the Yearbook, avoiding duplicates
    #    try:
    #        old_yb = Yearbook.objects.get(rankings=rankings)
    #        old_yb.delete()
    #    except Yearbook.DoesNotExist: pass
    yb = Yearbook(rankings=rankings)
    yb.top_post = results['top_post']
    yb.birthday_posts = birthday_posts


    ## Do this after we assign the top photos and top group photos

    # Store the photos the top 10 friends are tagged in, in order of score
    rankings.top_friends = [k for k,v in sorted(top_friend_score_by_id.items(), key=lambda x: x[1], reverse=True)]

    rankings.save()



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
