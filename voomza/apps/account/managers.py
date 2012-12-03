import logging
from celery.exceptions import TimeoutError
from django.db import models
from django_facebook.model_managers import FacebookUserManager as fb_FacebookUserManager
from django_facebook.api import require_persistent_graph
from voomza.apps.core.utils import flush_transaction
from voomza.apps.yearbook.api import YearbookFacebookUserConverter
from yearbook.tasks import get_and_store_top_friends_fast

logger = logging.getLogger(__name__)


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
#                get_and_store_top_friends_fast(request.user, facebook, pull_all_friends_when_done=True)

            request.session['pull_friends_async'] = async_result

        if async_result:
            # There was an async in session, or we just created one
            # Commit the transaction so we can pull new results
            flush_transaction()
            try:
                # Wait for results
                async_result.get(timeout=5)
            except TimeoutError:
                # Let the exception go and handle the error in js
                raise
            del request.session['pull_friends_async']

        return FacebookUser.objects.filter(friend_of__owner=request.user)


class FacebookFriendManager(models.Manager):
    def get_top_friends(self, user):
        return user.friends.exclude(top_friends_order=0)

    def get_non_top_friends(self, user):
        return user.friends.filter(owner=user).filter(top_friends_order=0)

    def not_in_app(self, query):
        return query.filter(facebook_user__profile__isnull=True)

    def in_app(self, query):
        return query.filter(facebook_user__profile__isnull=False)

    def i_havent_signed(self, query, user):
        return query.exclude(
            facebook_user__yearbook_signs_to__from_facebook_user=user.profile.facebook_user
        )

    def havent_signed_me(self, query, user):
        return query.exclude(
            facebook_user__yearbook_signs_from__to_facebook_user=user.profile.facebook_user
        )

    def get_yearbooks_to_sign(self, user):
        """
        Gets yearbooks in the order we think people will want them.
          Starts with people who haven't signed yours,
          starting with top friends *NOT* in the app,
          top friends in the app, regular friends not in the app, regular
          friends in the app.
        """
        ## -- For all of these, exclude anyone who I have already signed

        # Then, top friends who aren't currently using the app
        # APPROX 45
        top_friends_not_in_app = self.i_havent_signed(self.not_in_app(self.get_top_friends(user)), user)

        # Then top friends who are
        # APPROX 5
        # exclude ppl who signed me
        top_friends_in_app = self.havent_signed_me(self.i_havent_signed(self.in_app(self.get_top_friends(user)), user), user)

        # Non-top friends who are
        # APPROX 100
        # exclude people who signed me
        friends_in_app = self.havent_signed_me(self.i_havent_signed(self.in_app(self.get_non_top_friends(user)), user), user)

        # Non-top friends who don't use the app
        # APPROX 800
        friends_not_in_app = self.i_havent_signed(self.not_in_app(self.get_non_top_friends(user)), user)

        # Pretty small, grand total ~ 1000
        # will get called for pagination infrequently w/ small page sizes
        return top_friends_not_in_app | top_friends_in_app | friends_in_app | friends_not_in_app
