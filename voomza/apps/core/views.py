import logging
from django.core.urlresolvers import reverse
from django.shortcuts import render
from django_facebook.utils import CanvasRedirect

logger = logging.getLogger(name=__name__)


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
