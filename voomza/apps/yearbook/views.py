import logging
from django.template.context import RequestContext
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie
from django_facebook.api import require_persistent_graph
from voomza.apps.yearbook.api import YearbookFacebookUserConverter
from account.tasks import get_and_store_optional_profile_fields
from voomza.apps.yearbook.models import InviteRequestSent

logger = logging.getLogger(__name__)


@login_required
@ensure_csrf_cookie
def invite_friends_to_sign(request,
                           template_name='invite_friends.html',
                           next_view='sign_friends'):
    """
    User invites people to sgn their yearbook
    """
    facebook = None

    # If this is our first time here, pull the optional fields
    # This creates a FacebookUser for the person
    if request.user.profile.facebook_user_id is None \
        and 'optional_fields_async' not in request.session:
        graph = require_persistent_graph(request)
        facebook = YearbookFacebookUserConverter(graph)
        async_result = get_and_store_optional_profile_fields.delay(request.user, facebook)
        request.session['optional_fields_async'] = async_result

    # If they came in from a facebook request, delete it
    if 'inbound_request_ids' in request.session:
        if not facebook:
            graph = require_persistent_graph(request)
            facebook = YearbookFacebookUserConverter(graph)
        request_ids = request.session['inbound_request_ids'].split(',')
        for request_id in request_ids:
            try:
                fb_request = InviteRequestSent.objects.get(request_id=request_id,
                    facebook_id=request.user.profile.facebook_id)
                # Delete the request
                facebook.delete_request(fb_request)

            except InviteRequestSent.DoesNotExist:
                logger.warning('Looked in db for a request #%d, user id #%d. Did not exist.' % (request_id, request.user.profile.facebook_id))

    context = {
        'next_view': next_view
    }
    return render_to_response(template_name, context, RequestContext(request))


@login_required
@ensure_csrf_cookie
def sign_friends(request,
                 template_name='sign_friends.html'):
    """
    User signs friends' yearbooks
    """
    context = {}
    return render_to_response(template_name, context, RequestContext(request))


@login_required
@ensure_csrf_cookie
def yearbook_preview(request,
                     template_name='yearbook_preview.html'):
    """
    User sees a preview of their yearbook
    """
    context = {}
    return render_to_response(template_name, context, RequestContext(request))
