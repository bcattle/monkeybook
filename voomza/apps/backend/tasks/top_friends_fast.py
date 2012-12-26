from celery import task
from voomza.apps.core import bulk
from voomza.apps.core.utils import timeit, flush_transaction
from voomza.apps.account.models import FacebookUser, FacebookFriend
from voomza.apps.backend.fql.top_friends_fast import TopFriendsFastPipeline
from voomza.apps.backend.getter import FreqDistResultGetter


@task.task()
@timeit
def top_friends_fast(user, request=None):
    """
    Pulls all friends and all tags,
    combines them to get `top_friends_score`
    and saves `FacebookUser` and `FacebookFriend` models
    """
    pipeline = TopFriendsFastPipeline(user)
    results = pipeline.run()

    all_friends = results['get_friends']
    tagged_with_me = results['tagged_with_me']

    # Get the most-tagged
    most_tagged = FreqDistResultGetter(tagged_with_me, id_field='subject')
    # Reversing them means the index corresponds to top friends order
    top_friends_order_by_id = {}
    for top_friends_order, u in enumerate(most_tagged.order_by('count')):
        top_friends_order_by_id[u['id']] = top_friends_order

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

    # Check request for pending job
    if request and 'run_yearbook_async' in request.session:
        return results
    # See if user has a yearbook
#    try:
#        yearbook = Yearbook(owner=request.user)
#    except Yearbook.DoesNotExist:
    from backend.tasks import run_yearbook
    yearbook_async = run_yearbook.delay(user, results)
    if request:
        request.session['run_yearbook_async'] = yearbook_async
    results['run_yearbook_async'] = yearbook_async

    return results
