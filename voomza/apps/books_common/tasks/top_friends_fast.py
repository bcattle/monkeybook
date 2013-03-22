import datetime
from collections import defaultdict
from celery import task, group
from voomza.apps.books_common.fql import GetFriendsTask, TaggedWithMeTask
from voomza.apps.core import bulk
from voomza.apps.core.utils import flush_transaction, unix_date_from_datetime
from voomza.apps.account.models import FacebookUser, FacebookFriend
from voomza.apps.books_common.tasks.fql import run_task as rt


@task.task()
def top_friends_fast(user, friend_tag_end_time):
    """
    Pulls all friends and all tags,
    combines them to get `top_friends_score`
    and saves `FacebookUser` and `FacebookFriend` models
    """
    unix_friend_tag_end_time = unix_date_from_datetime(friend_tag_end_time)
    fql_job = group([
        rt.subtask(kwargs={'task_cls': GetFriendsTask,   'user_id': user.id, }),
        rt.subtask(kwargs={'task_cls': TaggedWithMeTask, 'user_id': user.id, 'end_time': unix_friend_tag_end_time }),
    ])
    job_async = fql_job.apply_async()
    results = job_async.get()

    all_friends = results['get_friends']
    tagged_with_me = results['tagged_with_me']

    # Collapse the tags by user_id, discount by age
    tag_score_by_user_id = defaultdict(lambda: 0.0)
    for tag in tagged_with_me.fields:
        tag_age = datetime.date.today().year - tag['created'].year + 1.0
        tag_score_by_user_id[tag['subject']] += 1 / tag_age

    # Sort
    user_ids_in_order = sorted(tag_score_by_user_id.iteritems(), key=lambda x: x[1])

    # Reversing them means the index corresponds to top friends order
    top_friends_order_by_id = {}
    for top_friends_order, u in enumerate(user_ids_in_order):
        top_friends_order_by_id[u[0]] = top_friends_order + 1   # 0 is not a valid value

    facebook_users = []
    facebook_friends = []
    for friend in all_friends:
        facebook_users.append(
            FacebookUser(
                facebook_id       = friend['id'],
                name              = friend['name'],
                first_name        = friend['first_name'],
                pic_square        = friend['pic_square'],
            )
        )
        facebook_friends.append(
            FacebookFriend(
                owner             = user,
                facebook_user_id  = friend['id'],
                top_friends_order = top_friends_order_by_id.get(friend['id'], 0)
            )
        )

    # Use the "bulk" library rather than the built-in
    # `bulk_create` so we can specify ON DUPLICATE KEY UPDATE
    #  -- getter guarantees that all fields are filled
    bulk.insert_or_update_many(FacebookUser, facebook_users)
    flush_transaction()

    # Insert is faster, we don't care about preserving other fields
    bulk.insert_or_update_many(FacebookFriend, facebook_friends, keys=['owner', 'facebook_user'])
    flush_transaction()

    return results
