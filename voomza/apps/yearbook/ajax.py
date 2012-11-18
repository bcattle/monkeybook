import json, logging
from dajaxice.decorators import dajaxice_register
from celery.result import AsyncResult
from django.core.urlresolvers import reverse
from django.http import HttpResponseForbidden
from voomza.apps.account.models import YearbookFacebookUser

logger = logging.getLogger(name=__name__)


FRIENDS_PER_PAGE = 20

@dajaxice_register
def get_friends(request, offset=0):
    """
    Returns a paginated list of the user's friends,
    in order of "top friends" relevance

    This function should be called repeatedly w/ increasing offset
    """
    if not request.user.is_authenticated():
        return HttpResponseForbidden

    if not offset:
        # If no offset, check for the top friends task
        # if running, give it 10 seconds to finish
        task_id = request.session.get('fast_friends_task_id')
        if task_id:
            async_result = AsyncResult(task_id)
            if not async_result.ready():
                async_result.get(timeout=10)

    top_friends_query = YearbookFacebookUser.objects.filter(user=request.user).order_by('-top_friends_order')
    # Return a set of results based on `offset`
    friends = top_friends_query[offset:offset+FRIENDS_PER_PAGE].values('facebook_id', 'name', 'pic_square', 'top_friends_order')
    if not friends and not offset:
        logger.warning('get_friends returned no results with offset=0, means friends didn\'t get pulled')
    # Serialize and return
    return json.dumps(list(friends))


@dajaxice_register
def invites_sent(request, friend_ids):
    """
    Log that the user sent invites
    OR actually send them if we do it client side
    """

    pass

    # If it worked, return redurect
    return reverse('vote_badges')
