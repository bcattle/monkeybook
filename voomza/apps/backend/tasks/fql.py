import logging
from celery import task
from django.contrib.auth.models import User

logger = logging.getLogger(__name__)

@task.task()
def run_task(results=None, task_cls=None, user_id=None, init_args=None):
    """
    Runs the task passed in as `task_cls`
      args and kwargs are passed to the __init__() method
      user is passed to the run() method
    """
    assert task_cls
    assert user_id

    init_args = init_args or {}
    results = results or {}

    logger.info('Running task %s' % task_cls.__name__)
    user = User.objects.get(id=user_id)

    task = task_cls(**init_args)
    return task.run(user, **results)
