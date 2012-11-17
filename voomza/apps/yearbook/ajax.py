import json, logging
from dajaxice.decorators import dajaxice_register
from voomza.apps.account.models import YearbookFacebookUser

logger = logging.getLogger(name=__name__)


FRIENDS_PER_PAGE = 20

# login_required?
@dajaxice_register
def get_friends(request, offset=0):
    """
    Returns a paginated list of the user's friends,
    in order of "top friends" relevance

    This function should be called repeatedly w/ increasing offset
    """
    # If called with `offset`, assume the caller knows there are users there
#    if not offset:

        ## NEED TO MAKE THIS WORK

        ## transaction issues with checking the async status, fuck it for now
        # otherwise, if top friends currently running, give it 10 seconds to finish
#        top_friends_async = request.session.get('fast_friends_async')
#        if top_friends_async and not top_friends_async.ready():
#            top_friends_async.get(timeout=10)

    top_friends_query = YearbookFacebookUser.objects.filter(user=request.user).order_by('-top_friends_order')
    # Return a set of results based on `offset`
    friends = top_friends_query[offset:offset+FRIENDS_PER_PAGE].values('facebook_id', 'name', 'pic_small', 'top_friends_order')
    if not friends and not offset:
        logger.warning('get_friends returned no results with offset=0, means friends didn\'t get pulled')
    # Serialize and return
    return json.dumps(list(friends))

