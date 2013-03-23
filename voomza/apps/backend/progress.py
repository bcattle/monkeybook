from celery.result import AsyncResult
from voomza.apps.backend.models import Yearbook

class YearbookProgress(object):
    """
    Small helper class that interprets the process
    ov making a user's yearbook - from session and db

    Because we have two nested tasks that spin off,
    we look at `pull_friends_async` even though we want `run_yearbook`
    """
    user = None
    pull_friends_async = None

    def __init__(self, request=None):
        if request:
            self.user = request.user
            # session can contain 'pull_friends_async',
            # which in turn contains 'run_yearbook_async'
            if 'pull_friends_id' in request.session:
                self.pull_friends_async = AsyncResult(id=request.session['pull_friends_id'])

    def get_status(self):
        if self.pull_friends_async and self.pull_friends_async.successful():
            results = self.pull_friends_async.get()
            if 'run_yearbook_async' in results:
                return results['run_yearbook_async'].status
                # Can return PENDING, STARTED, RETRY, FAILURE, or SUCCESS

        # Otherwise, look for a yearbook for user in db
        if Yearbook.objects.filter(rankings__user=self.user).exists():
            return 'SUCCESS'
        else:
            return 'FAILURE'

    def get_hash(self):
        if self.get_status() == 'SUCCESS':
            yearbooks = Yearbook.objects.filter(rankings__user=self.user)
            return yearbooks[0].hash
        else:
            return ''
