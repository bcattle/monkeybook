import logging
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie
from django_facebook.api import require_persistent_graph
from django_facebook.decorators import facebook_required_lazy
from voomza.apps.backend.models import Yearbook
from backend.tasks import run_yearbook, top_friends_fast

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
    # ** This also fires off the run_yearbook task **
    pull_friends_async = top_friends_fast.delay((request, ))
    request.session['pull_friends_async'] = pull_friends_async

    context = {
        'next_view': next_view
    }
    return render(request, template_name, context)


@login_required
@facebook_required_lazy(canvas=True)
@ensure_csrf_cookie
def sign_friends(request,
                 template_name='sign_friends.html'):
    """
    User signs friends' yearbooks
    """
    return render(request, template_name)


# No login required
def yearbook(request, hash, template_name='yearbook.html'):
    """
    The user-shared link to a yearbook
    This view is publically-visible
    """
    # Make sure the hash exists and pass them through
    try:
#        import ipdb
#        ipdb.set_trace()

        yearbook = Yearbook.objects.get(hash=hash)
    except Yearbook.DoesNotExist:
        logger.info('Attempt to access a bogus hash %s' % hash)
        return redirect('homepage')
    context = {
        'hash': yearbook.hash
    }
    return render(request, template_name, context)


@login_required
@facebook_required_lazy(canvas=True)
#@ensure_csrf_cookie
def yearbook_no_hash(request):
    """
    If the user has a yearbook, redirect to it
    """
    yearbooks = Yearbook.objects.filter(rankings__user=request.user)
    if yearbooks:
        return redirect(yearbooks[0].get_absolute_url())
    else:
        return redirect('homepage')
