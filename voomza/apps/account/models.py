from django.db import models
from django_facebook.models import FacebookProfileModel, FacebookUser


class UserProfile(FacebookProfileModel):
    """
    Created by a hook into the post_save signal on User
    """
    user = models.OneToOneField('auth.User')
    first_name = models.CharField(max_length=40, blank=True)
    locale = models.CharField(max_length=10, blank=True)
#    location
#    friends_invited_to_sign = models.ForeignKey(FacebookUserWithPic)    # <-- prob want to make this FK to a model like OpenGraphPost
    family = models.ManyToManyField('FacebookUserWithPic', related_name='+')
    significant_other = models.ForeignKey('FacebookUserWithPic', related_name='+')


class FacebookUserWithPic(FacebookUser):
    """
    Model for storing a user's friends,
    also store their picture URL for speed
    """
    picture = models.CharField(max_length=200, blank=True)

