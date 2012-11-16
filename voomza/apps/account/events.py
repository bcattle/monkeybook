from django.db.models.signals import post_save
from django.contrib.auth.models import User
from voomza.apps.account.models import UserProfile


# Every time a new User is created, create a UserProfile

def create_facebook_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

post_save.connect(create_facebook_profile, sender=User)
