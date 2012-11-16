import logging
from django.db.models.signals import post_save
#from django_facebook.signals import facebook_post_store_friends
from django_facebook.tasks import get_and_store_friends
from voomza.apps.account.models import UserProfile
from voomza.apps.yearbook.api import YearbookFacebookUserConverter
from voomza.apps.yearbook.tasks import pull_quick_top_friends, get_optional_profile_fields

logger = logging.getLogger(name=__name__)

# Every time a new UserProfile is created,
# fire off a task to pull most-tagged-with friends, and
# schedule one to pull optional fields
def post_user_profile_save(sender, instance, created, **kwargs):
    if created:
        graph = instance.get_offline_graph()
        facebook = YearbookFacebookUserConverter(graph)
        # Pull their quick top friends, needed for the next page
        pull_quick_top_friends.delay(instance.user, facebook)
        # Store their friends
        # This runs a separate query than the previous task, so run it at the same time
        get_and_store_friends.delay(instance.user, facebook)
        # Pull the optional fields in 5 minutes
        get_optional_profile_fields.apply_async(args=[instance.user, facebook], countdown=60*5)

post_save.connect(post_user_profile_save, sender=UserProfile)


## Every time a user's friends are saved,
## spin off the top friend calculations
#def post_store_friends(sender, user, friends, **kwargs):
#    # Pull quick top friends in anticipation of the next page
#    pull_quick_top_friends.delay(user, friends=friends)
#
#facebook_post_store_friends.connect(post_store_friends)
