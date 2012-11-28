import json, logging
from dajaxice.decorators import dajaxice_register
from django.core.urlresolvers import reverse
from django.http import HttpResponseForbidden, HttpResponseNotFound
from django_facebook.api import require_persistent_graph
from voomza.apps.account.models import YearbookFacebookUser
from voomza.apps.yearbook.api import YearbookFacebookUserConverter
from yearbook.tasks import get_and_store_top_friends_fast, get_optional_profile_fields
from voomza.apps.yearbook.models import InviteRequestSent, Badge, BadgeVote, YearbookSign
from voomza.apps.yearbook.ranking import UserProfileRanking


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
#                get_and_store_top_friends_fast(request.user, facebook, pull_all_friends_when_done=True)

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


def send_to_next_page(user, next_view):
    #  Update the user's current view
    user.profile.curr_signup_page = next_view
    user.profile.save()
    # Return redirect
    return json.dumps({ 'next_url': reverse(next_view) })


@dajaxice_register
def invites_sent(request, request_id, friend_ids, next_view='vote_badges'):
    """
    Log that the user sent invites
    """
    if not request.user.is_authenticated():
        return HttpResponseForbidden

    try:
        request_id_int = int(request_id)
    except ValueError:
        logger.error('invites_sent called with non-int ID back from facebook, skipping')
        return send_to_next_page(request.user, next_view)

    for friend_id in friend_ids:
        try:
            friend_id_int = int(friend_id)
            req = InviteRequestSent(user=request.user, facebook_id=friend_id_int, request_id=request_id_int)
            req.save()
        except ValueError:
            logger.error('invites_sent called with non-int friend ID "%s" back from facebook, skipping' % friend_id)

    return send_to_next_page(request.user, next_view)


@dajaxice_register
def save_badge_votes(request, selected_friends, next_view='sign_friends'):
    """
    Saves the friends this user has indicated
    are family, friends, etc.
    """
    if not request.user.is_authenticated():
        return HttpResponseForbidden

    # If for some reason they have some in the db, clear them
    old_votes = BadgeVote.objects.filter(from_user=request.user)
    old_votes.delete()

    badges = Badge.objects.all()
    for badge, badge_friends in zip(badges, selected_friends):
        if badge_friends:
            for friend_id in badge_friends:
                bv = BadgeVote(badge=badge, from_user=request.user, to_facebook_id=friend_id)
                bv.save()
    return send_to_next_page(request.user, next_view)


YEARBOOKS_PER_PAGE = 6

@dajaxice_register
def get_yearbooks_to_sign(request, offset=0):
    """
    Returns a list of users that we suggest this
    user should sign.
    """
    if not request.user.is_authenticated():
        return HttpResponseForbidden

    if 'all_yearbooks' in request.session:
        all_yearbooks = request.session['all_yearbooks']
    else:
        profile_ranking = UserProfileRanking(request.user.profile)
        all_yearbooks = profile_ranking.get_yearbooks_to_sign()
        request.session['all_yearbooks'] = all_yearbooks

    # Stuff in the list is either User or YearbookFacebookUser
    # we need fields name, pic and facebook_id
    return json.dumps([{
        #   | YearbookFacebookUser ||         User         |
        'name': getattr(x, 'name') or x.profile.facebook_name,
        'pic':  getattr(x, 'pic_square') or x.profile.pic_square,
        'id': getattr(x, 'facebook_id') or x.profile.facebook_id,
    } for x in all_yearbooks[offset:offset+YEARBOOKS_PER_PAGE]])


@dajaxice_register
def save_yearbook_sign(request, text, to_id):
    """
    Saves a user's message, note that
    the person being signed may or may not be
    signed up for the app
    """
    if not request.user.is_authenticated():
        return HttpResponseForbidden
    sign = YearbookSign(from_user = request.user, to_id=to_id, text=text)
    sign.save()
    return json.dumps('ok')


SIGNS_PER_PAGE = 10

@dajaxice_register
def get_yearbook_signs(request, offset=0):
    """
    Returns the list of users who have already
    signed this person's yearbook
    """
    if not request.user.is_authenticated():
        return HttpResponseForbidden

    signs_query = YearbookSign.objects.filter(to_id=request.user.profile.facebook_id)
    signs = signs_query[offset:offset+SIGNS_PER_PAGE].values(
        'id', 'from_user__profile__name', 'from_user__profile__pic_square'
    )

    import ipdb
    ipdb.set_trace()

    # Serialize and return
    # Return the offset so the caller can reject duplicates
    return json.dumps({
        'signs': list(signs),
        'offset': offset,
    })


@dajaxice_register
def get_yearbook_sign_message(request, sign_id):
    """
    Returns the list of users who have already
    signed this yearbook
    """
    if not request.user.is_authenticated():
        return HttpResponseForbidden

    try:
        sign = YearbookSign.objects.get(id=sign_id).values('text')
        return json.dumps(sign)
    except YearbookSign.DoesNotExist:
        return HttpResponseNotFound
