import logging, datetime, time
from celery.exceptions import TimeoutError
from pytz import utc
from celery import task, group
from voomza.apps.core.utils import merge_dicts, profileit
from voomza.apps.core import bulk
from voomza.apps.backend.getter import FreqDistResultGetter
from voomza.apps.backend.models import PhotoRankings, Yearbook, FacebookPhoto
from voomza.apps.backend.pipeline.yearbook import *
from voomza.apps.backend.settings import *
from backend.pipeline import run_task as rt

logger = logging.getLogger(__name__)


@task.task()
def get_photo_comments(user):
    """
    Pulls comments for all photos `user` is in
    and adds them to photo objects we assume are
    already in the db.
    """
    comments_task = CommentsOnPhotosOfMeTask()
    results = comments_task.run(user)
    # Assemble into list indexed by object_id
    comments_by_id = {}
    for comment in results['comments_on_photos_of_me'].fields:
        if comment['object_id'] in comments_by_id:
            comments_by_id[comment['object_id']].append(comment)
        else:
            comments_by_id[comment['object_id']] = [comment]

    # Serialize and save
    comments_db = [FacebookPhoto(
        facebook_id = photo_id,
        comments = sorted(comments_by_id[photo_id], key=lambda x: x['time'])
    ) for photo_id in comments_by_id]

    bulk.insert_or_update_many(FacebookPhoto, comments_db, update_fields=['comments'])

    return results



@task.task()
def get_photos_by_year(results, user):
    # Bucket the photos by year
    max_year, photos_of_me_by_year = results['photos_of_me'].bucket_by_year()
    photos_of_me_this_year = photos_of_me_by_year[max_year]

    # Get the top photos, both halves of the year
    half_way = datetime.datetime(datetime.datetime.now().year, 6, 29, tzinfo=utc)
    top_photos_of_me_first_half = photos_of_me_this_year.filter(lambda x: x['created'] < half_way)
    top_photos_of_me_second_half = photos_of_me_this_year.filter(lambda x: x['created'] >= half_way)

    # Back in time
    years = list(sorted(photos_of_me_by_year.keys(), reverse=True))
    by_year_list = []
    for index, year in enumerate(years[1:NUM_PREV_YEARS + 1]):
        by_year_list.append(photos_of_me_by_year[year].order_by('score'))

    results['photos_of_me_this_year'] = photos_of_me_this_year.order_by('score')
    results['top_photos_of_me_first_half'] = top_photos_of_me_first_half.order_by('score')
    results['top_photos_of_me_second_half'] = top_photos_of_me_second_half.order_by('score')
    results['back_in_time'] = by_year_list
    results['photos_of_me_by_year'] = photos_of_me_by_year
    return results




@task.task()
def get_most_tagged(results):
    assert 'tagged_with_me' in results
    recent_cutoff = datetime.datetime(datetime.datetime.now().year - RECENT_IS_YEARS, 1, 1, tzinfo=utc)
    tagged_recently = results['tagged_with_me']['tagged_with_me'].filter(
        lambda x: x['created'] > recent_cutoff
    )
    results['most_tagged_recently'] = FreqDistResultGetter(
        tagged_recently.fields, id_field='subject'
    )
    results['most_tagged'] = FreqDistResultGetter(
        results['tagged_with_me']['tagged_with_me'].fields,
        id_field='subject'
    )
    return results


@task.task()
def get_top_post_of_year(results, user):
    assert 'posts_from_year' in results
    top_post = results['posts_from_year'].order_by('score')[0]
    get_post_task = GetPostTask(top_post['id'])
    top_post = get_post_task.run(user)
    # Return JSON of top post
    results['top_post'] = top_post['get_post'][0]
    # If a timestamp, convert to datetime
    if 'created_time' in results['top_post']:
        timestamp = results['top_post']['created_time']
        created_datetime = datetime.datetime.utcfromtimestamp(timestamp).replace(tzinfo=utc)
        results['top_post']['created_time'] = created_datetime
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
        results['top_posters_from_year'],
        map_fxn=lambda x, y: x['count'] + y['count'],
        new_field_name='count',
        discard_orphans=False
    )

    # Get ids of gf/bf and immediate family
    family_ids = []
    for family_member in user.family.all():
        if family_member.relationship in IMMEDIATE_FAMILY:
            family_ids.append(family_member.facebook_id)

    # For each top friend, pull the photos they are tagged in
    # Gf/bf and immediate family to the front, the rest in top friends order
    top_friend_photos = []
    pulled_gfbf = False
    pulled_gfbf_family = 0
    for friend in top_friends.order_by('count'):
        friend_tags = results['tagged_with_me']['tagged_with_me'].filter(lambda x: x['subject']==friend['id'])
        if len(friend_tags) > TOP_FRIEND_MIN_PHOTOS:
            # Perform a join on `photos_of_me` to get the photo scores,
            # and sort by year, then score
            friend_photos = friend_tags.join_on_field(results['photos_of_me'], join_field_1='object_id')\
                .get_in_decending_year_score_order()
            if len(friend_tags) != len(friend_photos):
                logger.warn('Received a top friend photo that wasn\'t in \'photos_of_me\'. Odd.')
            # Bring photos of gf/bf and immediate family to the front
            if user.profile.significant_other_id and friend['id'] == user.profile.significant_other_id:
                top_friend_photos.insert(0, friend_photos)
                pulled_gfbf_family += 1
                pulled_gfbf = True
            elif friend['id'] in family_ids and pulled_gfbf_family < NUM_GFBF_FAMILY_FIRST:
                if pulled_gfbf:
                    # Insert behind their gfbf
                    top_friend_photos.insert(1, friend_photos)
                else:
                    top_friend_photos.insert(0, friend_photos)
                pulled_gfbf_family += 1
            else:
                top_friend_photos.append(friend_photos)

    # For each group photo, grab its score from 'photos_of_me'
    # and filter to photos from this year
    group_photos = []
    for group_photo in results['tagged_with_me']['group_photos'].fields:
        group_photo_id = group_photo['id']
        if group_photo_id in results['photos_of_me'].fields_by_id:
            group_photos.append(results['photos_of_me'].fields_by_id[group_photo_id])
        else:
            logger.warn('Received a group photo %s that wasn\'t in \'photos_of_me\'. Odd.' % group_photo_id )

    # Sort by year, score
    group_photos_getter = ResultGetter.from_fields(group_photos)
    group_shots = group_photos_getter.get_in_decending_year_score_order()

    # Return the lists and the subtask
    results['top_friends'] = top_friend_photos
    results['group_shots'] = group_shots
    results['on_photos_of_me_async'] = on_photos_of_me_async
    return results


