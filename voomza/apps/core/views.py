import logging
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django_facebook.utils import CanvasRedirect

logger = logging.getLogger(name=__name__)


def homepage(request,
             template_name='homepage.html'):
    """
    If user is logged in,
    send them to the correct page in the flow
    """
    if request.user.is_authenticated():
        # Redirect them to their curr_page
        return CanvasRedirect(reverse(request.user.profile.current_page))
    else:
        # If they came in via a request, we need to delete it
        # GET will contain one or more `request_ids`
        if 'request_ids' in request.GET:
            # Store the request in the session, if they sign up successfully
            # we will delete it on the other side
            request.session['inbound_request_ids'] = request.GET['request_ids']

        # They also may have recieved a request to sign someone's yearbook
        # store that in session as well
        if 'please_sign' in request.GET:
            request.session['please_sign'] = request.GET['please_sign']

        return render_to_response(template_name, {}, RequestContext(request))
