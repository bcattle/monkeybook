import logging
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie
from django_facebook.api import require_persistent_graph
from django_facebook.decorators import facebook_required_lazy
from django_facebook.utils import CanvasRedirect
from voomza.apps.backend.models import Yearbook
from backend.tasks import run_yearbook, top_friends_fast

logger = logging.getLogger(__name__)


def homepage(request):
    """
    If user is logged in,
    send them to the correct page in the flow
    """
    if request.user.is_authenticated():
        # If they haven't completed the invites page, send them there
        if request.user.profile.current_page == 'invite_friends_to_sign':
            return CanvasRedirect(reverse(request.user.profile.current_page))

        # Otherwise show the returning-user homepage
        else:
            return render(request, 'return_home.html', {})

    else:
        return render(request, 'homepage.html', {})


@login_required
@facebook_required_lazy(canvas=True)
@ensure_csrf_cookie
def invite_friends_to_sign(request,
                           template_name='invite_friends.html',
                           next_view='transfer_screen'):
    """
    User invites people to sgn their yearbook
    """
    # Start pulling the user's top friends (fast)
    # ** This also fires off the run_yearbook task **
    run_yearbook = 'run_yearbook_async' not in request.session
    pull_friends_async = top_friends_fast.apply_async(kwargs={'user': request.user, 'run_yearbook': run_yearbook})
    request.session['pull_friends_async'] = pull_friends_async

    context = {
        'next_view': next_view
    }
    return render(request, template_name, context)


@login_required
@facebook_required_lazy(canvas=True)
@ensure_csrf_cookie
def transfer_screen(request,
                    template_name='transfer_screen.html'):
    """
    Page that sends user out of facebook to
    the full site
    """
    return render(request, template_name)


#@login_required
#@facebook_required_lazy(canvas=True)
#@ensure_csrf_cookie
#def sign_friends(request,
#                 template_name='sign_friends.html'):
#    """
#    User signs friends' yearbooks
#    """
#    return render(request, template_name)


# No login required
def yearbook(request, hash, template_name='yearbook.html'):
    """
    The user-shared link to a yearbook
    This view is publically-visible
    """
    # Make sure the hash exists and pass them through
    try:
        yearbook = Yearbook.objects.get(hash=hash)
        is_user_yearbook = request.user == yearbook.rankings.user
        context = {
            'hash': yearbook.hash,
            'owner': yearbook.rankings.user,
            'is_user_yearbook': is_user_yearbook,
        }
        return render(request, template_name, context)

    except Yearbook.DoesNotExist:
        logger.info('Attempt to access a bogus hash %s' % hash)
        return redirect('homepage')


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


# No login required
def sample_yearbook_page(request, filename):
    """
    Just return the file indiciated by `filename`
    """
    return render(request, 'sample_pages/%s' % filename, {})
