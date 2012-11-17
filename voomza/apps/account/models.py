import logging
from django.db import models
from django.db.models.signals import post_save
from django.dispatch.dispatcher import receiver
from django.contrib.auth.models import User
from django_facebook.model_managers import FacebookUserManager
from django_facebook.models import BaseFacebookProfileModel

logger = logging.getLogger(name=__name__)


class UserProfile(BaseFacebookProfileModel):
    """
    Created by a hook into the post_save signal on User
    """
    user = models.OneToOneField('auth.User', related_name='profile')
    first_name = models.CharField(max_length=40, blank=True)
    locale = models.CharField(max_length=10, blank=True)
#    location
#    friends_invited_to_sign = models.ForeignKey(FacebookUserWithPic)           # <-- prob want to make this FK to a model like OpenGraphPost
    family = models.ManyToManyField('YearbookFacebookUser', related_name='+', null=True)
    significant_other = models.ForeignKey('YearbookFacebookUser', related_name='+', null=True)
    current_page = models.CharField(max_length=40, default='invite_friends_to_sign')

    def friends(self):
        friends = YearbookFacebookUser.objects.filter(user_id=self.user_id)
        return friends


class YearbookFacebookUser(models.Model):
    """
    Model for storing a user's friends,
    also store their picture URL for speed
    """
    user = models.ForeignKey('auth.User')
    facebook_id = models.BigIntegerField()
    name = models.TextField(blank=True, null=True)
    gender = models.CharField(choices=(('F', 'female'), ('M', 'male')), blank=True, null=True, max_length=1)
    pic_small = models.CharField(max_length=200, blank=True)
    top_friends_order = models.PositiveSmallIntegerField(default=0, help_text='Higher the better',
                                                         db_index=True)
    objects = FacebookUserManager()

    class Meta:
        unique_together = ['user', 'facebook_id']

    def __unicode__(self):
        return u'Facebook user %s' % self.name


# Make sure we create a UserProfile when creating a User
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created and instance.username != 'admin':
        print 'UserProfile create called()'
        UserProfile.objects.create(user=instance)

