import logging
from celery.exceptions import TimeoutError
from django.db import models
from django_facebook.model_managers import FacebookUserManager as fb_FacebookUserManager
from django_facebook.api import require_persistent_graph
from voomza.apps.core.utils import flush_transaction
from voomza.apps.yearbook.api import YearbookFacebookUserConverter
from yearbook.tasks import get_and_store_top_friends_fast

logger = logging.getLogger(__name__)


class FacebookUserManager(models.Manager):
    def using_app(self):
        """
        Returns facebook users we know about who are using the app
        """
        pass

    def not_using_app(self):
        """
        Returns facebook users we know about who are using the app
        """
        pass


class FacebookUserManager(fb_FacebookUserManager):
    """
    This is a manager that also acts as a factory
    to pull the user's friends from facebook if they
    haven't been yet.
    """
    def get_friends_for_user(self, request):
        """
        Pull the FacebookUsers that a user is connected to,
        from facebook if necessary
        """
        from voomza.apps.account.models import FacebookUser
        # If we have a pending async request, let it finish
        async_result = request.session.get('pull_friends_async', None)
        if not async_result:
            friends = request.user.friends
            # Do we need to pull top friends?
            pull_top_friends = not friends.exclude(top_friends_order=0).exists()
            if pull_top_friends:
                # Pull top friends, then all other friends
                logger.info('In get_for_user(), pulling top friends')
                graph = require_persistent_graph(request)
                facebook = YearbookFacebookUserConverter(graph)
                async_result = get_and_store_top_friends_fast.delay(request.user, facebook,
                    pull_all_friends_when_done=True)

                request.session['pull_friends_async'] = async_result

        if async_result:
            # There was an async in session, or we just created one
            try:
                # Commit the transaction so we can pull the new results
                flush_transaction()
#                # Pull results
#                top_friends_qs = async_result.get(timeout=5)
                async_result.get(timeout=5)
            except TimeoutError:
                # Let the exception go and handle the error in js
                raise
            del request.session['pull_friends_async']
#            return top_friends_qs

        return FacebookUser.objects.filter(friend_of__owner=request.user)
