import json
from celery.exceptions import TimeoutError
from dajaxice.decorators import dajaxice_register
from django_facebook.api import require_persistent_graph
from voomza.apps.account.models import YearbookFacebookUser
from voomza.apps.core.utils import flush_transaction
from voomza.apps.yearbook.api import YearbookFacebookUserConverter
from voomza.apps.yearbook.tasks import get_and_store_top_friends_fast

FRIENDS_PER_PAGE = 20

def _get_top_friends_query(user):
    return YearbookFacebookUser.objects.filter(user_id=user.id).order_by('top_friends_order')

def _get_page_of_friend_results(top_friends_query, offset):
    # Already ran, return a set of results based on `offset`
    top_friends = top_friends_query[offset:offset+FRIENDS_PER_PAGE].values('facebook_id', 'name', 'picture', 'top_friends_order')
    # Serialize and return
    return json.dumps(top_friends)

@dajaxice_register
def get_friends(request, offset=0):
    """
    Returns a paginated list of the user's friends,
    in order of "top friends" relevance

    This function should be called repeatedly w/ increasing offset
    """
    # If called with `offset`, assume the caller knows there are users there
    if not offset:
        # Was called with `offset` of zero

        # The user's top friends are stored as a nonzero value
        # in the field YearbookFacebookUser.top_friends_order

        # There could be a couple cases:
        #  - their friends haven't been pulled yet, no values in table
        #  - their friends were pulled but top friends code hasn't run yet
        #  - top friends code has been run

        request.session['top_friends_fast_async']

        # Pull their top friend: order_by `top_friends_order`
        try:
            top_friends_query = _get_top_friends_query(request.user)
            top_friend = top_friends_query[0]
            if top_friend.top_friends_order:
                # Top friends in the db, return the results
                return _get_page_of_friend_results(top_friends_query, offset)
        except YearbookFacebookUser.DoesNotExist: pass
        # Realize we don't care if there are no friends in the table,
        # since the top friends calculation pulls from fb
        # Need to run the top friends calculation
        graph = require_persistent_graph(request)
        facebook = YearbookFacebookUserConverter(graph)
        async = pull_quick_top_friends.delay(request.user, facebook)
        try:
            async.get()
        except TimeoutError:
            return ''
        # Results now in db, repeat the query
        flush_transaction()

    top_friends_query = _get_top_friends_query(request.user)
    return _get_page_of_friend_results(top_friends_query, offset)


