import logging
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie
from django_facebook.api import require_persistent_graph
from django_facebook.decorators import facebook_required_lazy
from django_facebook.utils import CanvasRedirect
from monkeybook.apps.backend.models import Yearbook
from backend.tasks import top_friends_fast, pull_user_profile

logger = logging.getLogger(__name__)


def homepage(request):
    """
    If user is logged in,
    send them to the correct page in the flow
    """
    if request.user.is_authenticated():
        # If they haven't completed the invites page, send them there
#        if request.user.profile.current_page == 'invite_friends_to_sign':
#            return CanvasRedirect(reverse(request.user.profile.current_page))

        # Otherwise show the returning-user homepage
#        else:
        context = {
            'show_confirm_modal': request.GET.get('c') == 'order'
        }
        return render(request, 'return_home.html', context)

    else:
        return render(request, 'homepage.html', {})


@login_required
@facebook_required_lazy(canvas=True)
def start(request, next_view='loading'):
    """
    Spins off the yearbook
    """
    # Start pulling the user's top friends (fast)
    # ** This also fires off the run_yearbook task **
    run_yearbook = 'run_yearbook_async' not in request.session
    if 'pull_friends_async' not in request.session:
        pull_friends_async = top_friends_fast.apply_async(kwargs={'user': request.user, 'run_yearbook': run_yearbook})
        # Oddly, saving the async_result to session - it disappears
        # this even though the 'optional_fields_async' survives
        request.session['pull_friends_id'] = pull_friends_async.id
    #        request.session['pull_friends_async'] = pull_friends_async

    # We also need their optional profile fields,
    # fire that off as well
    if 'optional_fields_async' not in request.session:
        optional_fields_async = pull_user_profile.apply_async(kwargs={'user': request.user})
        request.session['optional_fields_async'] = optional_fields_async

    return redirect(next_view)


@login_required
@facebook_required_lazy(canvas=True)
@ensure_csrf_cookie
def invite_friends_to_sign(request,
                           template_name='invite_friends.html',
                           next_view='homepage'):
    """
    User invites people to sgn their yearbook
    """
    context = {
        'next_view': next_view
    }
    return render(request, template_name, context)


@login_required
@facebook_required_lazy(canvas=True)
def loading(request,
            template_name='loading.html',
            next_view='yearbook_no_hash'):
    context = {
        'next_view': next_view
    }
    return render(request, template_name, context)


@login_required
@facebook_required_lazy(canvas=True)
def not_enough_photos(request,
            template_name='not_enough_photos.html'):
    context = { }
    return render(request, template_name, context)


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
