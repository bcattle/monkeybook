import logging
from celery import task

logger = logging.getLogger(__name__)

@task.task(ignore_result=True)
def get_and_store_top_friends_fast(user, facebook):
    """
    Pulls the user's top friends, using a
    quick algorithm that is designed to work in time
    for the next page load
    """
    facebook.get_and_store_top_friends_fast(user)


@task.task(ignore_result=True)
def get_and_store_top_friends(user, facebook):
    """
    Pulls the user's top friends,
    using the full algorithm
    """
    pass


@task.task(ignore_result=True)
def get_optional_profile_fields(user, facebook):
    """
    Pulls the optional fields in the user's profile
    """
    pass
