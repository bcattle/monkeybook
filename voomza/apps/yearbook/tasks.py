import logging
from celery import task
from django_facebook.tasks import get_and_store_friends

logger = logging.getLogger(__name__)


# we can't ignore_results here,
# because we need to know whether the task completed or not
@task.task()
#@profileit(name='top-friends-%s.profile' % datetime.datetime.now())
#@profileit(name='top-friends-%s.profile' % datetime.datetime.now())
def get_and_store_top_friends_fast(user, facebook, pull_all_friends_when_done=False):
    """
    Pulls the user's top friends, using a
    quick algorithm that is designed to work in time
    for the next page load

    pull_all_friends_when_done: fire off a task to pull all friends
                                after this function completes
    """
    facebook.get_and_store_top_friends_fast(user)

    if pull_all_friends_when_done:
        # Fire off the task that pulls *all* friends
        get_and_store_friends.delay(user, facebook)


@task.task(ignore_result=True)
def get_and_store_top_friends(user, facebook):
    """
    Pulls the user's top friends,
    using the full algorithm
    """
    pass


