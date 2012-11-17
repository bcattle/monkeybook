from django.template.context import RequestContext
from django.shortcuts import redirect, render_to_response
from django.contrib.auth.decorators import login_required
from django_facebook.api import require_persistent_graph
from voomza.apps.yearbook.api import YearbookFacebookUserConverter
from yearbook.tasks import get_and_store_top_friends_fast, get_optional_profile_fields


# This view has no URL
def begin_signup(request):
    """
    Utility view that spins off some tasks that we want later in the flow
    """
    graph = require_persistent_graph(request)
    facebook = YearbookFacebookUserConverter(graph)

    # Pull top friends
    fast_friends_async = get_and_store_top_friends_fast.delay(request.user, facebook, pull_all_friends_when_done=True)
    request.session['fast_friends_task_id'] = fast_friends_async.task_id

    # Pull the optional fields in 5 minutes
    get_optional_profile_fields.apply_async(args=[request.user, facebook], countdown=60*5)


@login_required
def invite_friends_to_sign(request,
                           template_name='invite_friends_to_sign.html',
                           next_view='vote_badges'):
    """
    User invites their friends to sign their yb
    This is sent with the request dialog from javascript

    The template loads top friends, then the rest via AJAX
    UI elements:
        Skip button -> href to next page
        Select all
        Send invites    POST back to this view
    """
    begin_signup(request)

    context = {
        'next_view': next_view
    }
    return render_to_response(template_name, context, RequestContext(request))


@login_required
def vote_badges(request,
                template_name='vote_badges.html',
                next_view='sign_friends'):
    if request.method == 'POST':


        # Update the curr step in the flow
        request.user.profile.curr_signup_page = next_view
        request.user.profile.save()
        return redirect(next_view)

    context = {}
    return render_to_response(template_name, context, RequestContext(request))


@login_required
def sign_friends(request,
                 template_name='sign_friends.html',
                 next_view='teaser'):
    if request.method == 'POST':


        # Update the curr step in the flow
        request.user.profile.curr_signup_page = next_view
        request.user.profile.save()
        return redirect(next_view)

    context = {}
    return render_to_response(template_name, context, RequestContext(request))


@login_required
def teaser(request, template_name='teaser.html'):
    context = {

    }
    return render_to_response(template_name, context, RequestContext(request))

