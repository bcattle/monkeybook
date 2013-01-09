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

    def __init__(self, request):
        self.user = request.user
        # session can contain 'pull_friends_async',
        # which in turn contains 'run_yearbook_async'
        self.pull_friends_async = request.session.get('pull_friends_async', None)

    def get_status(self):
        if self.pull_friends_async and self.pull_friends_async.successful():
            results = self.pull_friends_async.get()
            if 'run_yearbook_async' in results:
                return results['run_yearbook_async'].status
                # Can return PENDING, STARTED, RETRY, FAILURE, or SUCCESS

        # Otherwise, look for a yearbook for user in db
        try:
            yb = Yearbook(rankings__user=self.user)
            return 'SUCCESS'
        except Yearbook.DoesNotExist:
            return 'FAILURE'

