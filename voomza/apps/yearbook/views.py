import logging
from django.template.context import RequestContext
from django.shortcuts import render_to_response, render
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie
from django_facebook.api import require_persistent_graph
from django_facebook.decorators import facebook_required_lazy
from voomza.apps.account.models import FacebookUser
from voomza.apps.backend.models import Yearbook
from voomza.apps.yearbook.api import YearbookFacebookUserConverter
from account.tasks import get_and_store_optional_profile_fields
from backend.tasks import run_yearbook

logger = logging.getLogger(__name__)


@login_required
@facebook_required_lazy(canvas=True)
@ensure_csrf_cookie
def invite_friends_to_sign(request,
                           template_name='invite_friends.html',
                           next_view='sign_friends'):
    """
    User invites people to sgn their yearbook
    """
    # Start pulling the user's top friends (fast)
    FacebookUser.objects.get_friends_for_user(request, return_async=True)

    # If this is our first time here, pull the optional fields
    # This creates a FacebookUser for the person
    if request.user.profile.facebook_user_id is None \
        and 'optional_fields_async' not in request.session:
        graph = require_persistent_graph(request)
        facebook = YearbookFacebookUserConverter(graph)
        async_result = get_and_store_optional_profile_fields.delay(request.user, facebook)
        request.session['optional_fields_async'] = async_result

    # If the user doesn't have a yearbook,
    # and there isn't one progress, build it.
    if 'run_yearbook_async' not in request.session:
#        try:
#            yearbook = Yearbook(owner=request.user)
#        except Yearbook.DoesNotExist:
        yearbook_async = run_yearbook.delay(request.user)
        request.session['run_yearbook_async'] = yearbook_async
        logger.info('Starting yearbook for user %s' % request.user.username)

    context = {
        'next_view': next_view
    }
#    return render_to_response(template_name, context, RequestContext(request))
    return render(request, template_name, context)


@login_required
@facebook_required_lazy(canvas=True)
@ensure_csrf_cookie
def sign_friends(request,
                 template_name='sign_friends.html'):
    """
    User signs friends' yearbooks
    """
    context = {}
    return render_to_response(template_name, context, RequestContext(request))


@login_required
@facebook_required_lazy(canvas=True)
@ensure_csrf_cookie
def yearbook(request,
             template_name='yearbook.html'):
    """
    User's yearbook
    """
    context = {}
    return render_to_response(template_name, context, RequestContext(request))

