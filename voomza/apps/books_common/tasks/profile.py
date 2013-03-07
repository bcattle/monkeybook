from celery import task
from voomza.apps.books_common.fql.profile import ProfileFieldsTask


@task.task(ignore_result=True)
def pull_user_profile(user):
    profile_task = ProfileFieldsTask()
    results = profile_task.run(user)
    profile_task.save_profile_fields(user, results['profile_fields'])
