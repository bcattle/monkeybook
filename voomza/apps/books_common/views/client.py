from __future__ import division, print_function, unicode_literals
import logging
from django.conf import settings
from django.contrib.auth.models import User
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from voomza.apps.books_common.books import get_book_task
from voomza.apps.books_common.models import GenericBook
from voomza.lib.django_facebook.decorators import facebook_required_lazy

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
def start(request, book_name='yearbook2012', next_view='loading'):
    """
    Spins off the yearbook
    """
    # TODO: find a way to have this effect w/o exposing a public URL?

    # Reject duplicates: look for a task
    # corresponding to that book in the session
    session_async_name = '%s_task_id' % book_name
    if session_async_name not in request.session:
        # Run the specified book
        book_task = get_book_task(book_name)
        book_task_async = book_task.apply_async(kwargs={'user': request.user})
        # Oddly, saving the async_result to session - it disappears.
        # This even though the 'optional_fields_async' survives
        request.session[session_async_name] = book_task_async.id

    # Regardless of book, we need their optional profile fields
    if 'optional_fields_async' not in request.session:
        optional_fields_async = pull_user_profile.apply_async(kwargs={'user': request.user})
        request.session['optional_fields_async'] = optional_fields_async

    return redirect(next_view)


@login_required
@facebook_required_lazy(canvas=True)
def loading(request,
            template_name='loading.html',
            next_view='yearbook_no_hash'):
    context = {
        'next_view': next_view
    }
    return render(request, template_name, context)


def view_book_short_url(request, slug):
    """
    Look up a book by slug
    and show it
    """
    generic_book = get_object_or_404(GenericBook, slug=slug)



# Public, this is the landing page for inbound open graph links
def landing(request):
    pass


# Login required to enforce permissions
# (shortened url is always public)
@login_required
@facebook_required_lazy(canvas=True)
def view_book(request, book_type, username=None, pk=None):
    """
    This is the link a user uses to view their own yearbook
    or where inbound open graph, etc. links land
    """
    # First, make sure the `book_type` exists
    if book_type not in settings.ALL_BOOKS:
        raise Http404
    book = settings.ALL_BOOKS[book_type]

    # Look up the given username
    if username:
        user = get_object_or_404(User, username=username)
    else:
        user = request.user

    # If `pk` supplied, get that book
    # otherwise get the latest


    # Check the user's permissions
    if not book_instance.user_can_see_book(user.profile.facebook_user.id):
        # Return redirect?
        # Raise 404?



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
def book_no_hash(request):
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
