import logging
from celery import task

logger = logging.getLogger(__name__)

@task.task(ignore_result=True)
def pull_quick_top_friends(user, facebook):
    """
    Pulls the user's top friends, using a
    quick algorithm that is designed to work in time
    for the next page load
    """
    pass
    # If the user somehow has no top friends,
    # one of them needs to have top_friends_order = 1
    # to indicate that the function ran

    # This needs to run whether or not they already have friend entries in the database


@task.task(ignore_result=True)
def pull_top_friends(user, facebook):
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
