from django.db.models.signals import post_save
from voomza.apps.account.models import UserProfile
from voomza.apps.yearbook.tasks import pull_quick_top_friends, pull_optional_fields


# Every time a new UserProfile is created,
# fire off a task to pull most-tagged-with friends, and
# schedule one to pull optional fields

def post_user_profile_save(sender, instance, created, **kwargs):
    if created:
        # Pull quick top friends in anticipation of the next page
        pull_quick_top_friends.delay(instance)
        # Schedule pulling the optional fields for 15 mins from now
        pull_optional_fields.apply_async(args=[instance], countdown=15*60)

post_save.connect(post_user_profile_save, sender=UserProfile)
