import logging
from celery import task
from django_facebook.tasks import get_and_store_friends

logger = logging.getLogger(__name__)


@task.task(ignore_result=True)
def accept_invite_requests(invite_requests):
    """
    Send a request to facebook to DELETE the request,
    and update the entry in our db
    """
    from monkeybook.apps.yearbook.api import YearbookFacebookUserConverter

    for invite_request in invite_requests:
        accepting_user = invite_request.to_facebook_user.profile.user
        graph = accepting_user.profile.get_offline_graph()
        facebook = YearbookFacebookUserConverter(graph)
        # Delete the request
        facebook.delete_request(invite_request)
        logger.info('Invite request deleted')
