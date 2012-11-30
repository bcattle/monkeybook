from django.template.context import RequestContext
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie
from django_facebook.api import require_persistent_graph
from voomza.apps.yearbook.api import YearbookFacebookUserConverter
from voomza.apps.yearbook.models import Badge
from account.tasks import get_and_store_optional_profile_fields


@login_required
@ensure_csrf_cookie
def invite_friends_to_sign(request,
                           template_name='invite_friends_to_sign.html',
                           next_view='vote_badges'):
    """
    User invites their friends to sign their yb
    This is sent with the request dialog from javascript

    The page pull top friends, then the rest via AJAX
    UI elements:
        Skip button -> href to next page
        Select all
        Send invites    sent to fb via JS and logged from AJAX
    """
    # If this is our first time here, pull the optional fields
    # This creates a FacebookUser for the person
    if request.user.profile.facebook_user_id is None \
        and 'optional_fields_async' not in request.session:
        graph = require_persistent_graph(request)
        facebook = YearbookFacebookUserConverter(graph)
        async_result = get_and_store_optional_profile_fields.delay(request.user, facebook)
        request.session['optional_fields_async'] = async_result

    context = {
        'next_view': next_view
    }
    return render_to_response(template_name, context, RequestContext(request))


@login_required
def vote_badges(request,
                template_name='vote_badges.html',
                next_view='sign_friends'):
    """
    User nominates their friends to be significant other,
    family, and the various badges
    """
    badges = Badge.objects.all()
    context = {
        'badges': badges,
        'next_view': next_view,
    }
    return render_to_response(template_name, context, RequestContext(request))


@login_required
def sign_friends(request,
                 template_name='sign_friends.html',
                 next_view='teaser'):

    context = {
        'next_view': next_view,
    }
    return render_to_response(template_name, context, RequestContext(request))


@login_required
def teaser(request, template_name='teaser.html'):
    context = {

    }
    return render_to_response(template_name, context, RequestContext(request))

