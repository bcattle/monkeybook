import logging
from celery import task

logger = logging.getLogger(__name__)


@task.task(ignore_result=True)
def get_and_store_optional_profile_fields(user, facebook):
    """
    Pulls the optional fields in the user's profile
    """
    facebook.get_and_store_optional_fields(user)
