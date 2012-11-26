import logging
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django_facebook.api import require_persistent_graph
from django_facebook.utils import CanvasRedirect
from voomza.apps.yearbook.api import YearbookFacebookUserConverter
from voomza.apps.yearbook.models import InviteRequestSent

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
            graph = require_persistent_graph(request)
            facebook = YearbookFacebookUserConverter(graph)

            request_ids = request.GET['request_ids'].split(',')
            for request_id in request_ids:
                try:
                    fb_request = InviteRequestSent.objects.get(request_id=request_id,
                        facebook_id=request.user.profile.facebook_id)
                    # Delete the request
                    facebook.delete_request(fb_request)

                except InviteRequestSent.DoesNotExist:
                    logger.warning('Looked in db for a request #%d, user id #%d. Did not exist.' % (request_id, request.user.profile.facebook_id))


        return render_to_response(template_name, {}, RequestContext(request))
