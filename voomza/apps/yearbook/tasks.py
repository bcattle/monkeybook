from celery import task
import logging

logger = logging.getLogger(__name__)

@task.task(ignore_result=True)
def pull_quick_top_friends(profile):
    """
    Pulls the user's top friends, using a
    quick algorithm that is designed to work in time
    for the next page load
    """
    facebook = profile.get_offline_graph()
    pass


@task.task(ignore_result=True)
def pull_top_friends(profile):
    """
    Pulls the user's top friends,
    using the full algorithm
    """
    facebook = profile.get_offline_graph()
    pass


@task.task(ignore_result=True)
def pull_optional_fields(profile):
    """
    Pulls the optional fields in the user's profile
    """
    facebook = profile.get_offline_graph()
    pass
