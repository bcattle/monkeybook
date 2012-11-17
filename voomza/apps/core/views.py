from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django_facebook.utils import CanvasRedirect


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
        return render_to_response(template_name, {}, RequestContext(request))
