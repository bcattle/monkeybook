from django.template.context import RequestContext
from django.shortcuts import redirect, render_to_response
from django.contrib.auth.decorators import login_required


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
    context = {}
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

