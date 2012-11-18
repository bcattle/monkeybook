import json, logging
from dajaxice.decorators import dajaxice_register
from django.core.urlresolvers import reverse
from django.http import HttpResponseForbidden
from django_facebook.api import require_persistent_graph
from django_facebook.tasks import get_and_store_friends
from voomza.apps.account.models import YearbookFacebookUser
from voomza.apps.yearbook.api import YearbookFacebookUserConverter
from yearbook.tasks import get_and_store_top_friends_fast, get_optional_profile_fields


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

    graph = require_persistent_graph(request)
    facebook = YearbookFacebookUserConverter(graph)

    if not offset:
        # Did we already start to pull?
        async_result = request.session.get('pull_friends_async', None)
        if not async_result:
            friends = YearbookFacebookUser.objects.filter(user=request.user)
            # Do we need to pull top friends?
            pull_top_friends = not friends.exclude(top_friends_order=0).exists()
            if pull_top_friends:
                # Pull top friends, then all other friends
                logger.info('In get_friends(), pulling top friends')
                async_result = get_and_store_top_friends_fast.delay(request.user, facebook,
                                                                    pull_all_friends_when_done=True)
                request.session['pull_friends_async'] = async_result
        if async_result:
            # Give it 5 seconds to return
            async_result.get(timeout=5)

    top_friends_query = YearbookFacebookUser.objects.filter(user=request.user).order_by('-top_friends_order')
    # Return a set of results based on `offset`
    friends = top_friends_query[offset:offset+FRIENDS_PER_PAGE].values('facebook_id', 'name', 'pic_square', 'top_friends_order')
    if not friends and not offset:
        logger.warning('get_friends returned no results with offset=0, means friends didn\'t get pulled')
    # Serialize and return
    # Return the offset so the caller can reject duplicates
    return json.dumps({
        'friends': list(friends),
        'offset': offset,
        })


@dajaxice_register
def invites_sent(request, friend_ids, next_view='vote_badges'):
    """
    Log that the user sent invites
    OR actually send them if we do it client side
    """
    if not request.user.is_authenticated():
        return HttpResponseForbidden

    # TODO: log the friend_ids
    pass

    #  Update the user's current view
    request.user.profile.curr_signup_page = next_view
    request.user.profile.save()
    # If it worked, return redurect
    return reverse(next_view)
