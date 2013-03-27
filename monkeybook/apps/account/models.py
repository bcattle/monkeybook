from __future__ import division, print_function, unicode_literals
from django.utils.encoding import python_2_unicode_compatible
import logging
from django.db import models
from django.db.models.signals import post_save
from django.dispatch.dispatcher import receiver
from django.contrib.auth.models import User
from django_facebook.models import BaseFacebookProfileModel
from django.shortcuts import redirect
from monkeybook.apps.account.managers import FacebookUserManager

logger = logging.getLogger(name=__name__)


class UserProfile(BaseFacebookProfileModel):
    """
    Created by a hook into the post_save signal on User
    """
    user = models.OneToOneField('auth.User', related_name='profile')
    facebook_user = models.OneToOneField('FacebookUser', null=True, related_name='profile')
    locale = models.CharField(max_length=10, blank=True)
    relationship_status = models.CharField(max_length=40, blank=True)
    significant_other_id = models.BigIntegerField(null=True)

    current_page = models.CharField(max_length=40, default='invite_friends_to_sign')

    def post_facebook_registration(self, request):
        """
        Behavior after registering with facebook
        """
#        return redirect(self.current_page)
        return redirect('start')


class FamilyConnection(models.Model):
    owner = models.ForeignKey('auth.User', related_name='family')
    facebook_id = models.BigIntegerField()
    relationship = models.CharField(max_length=40, blank=True)


### Add an index to the facebook_id field
## Done here because it lives in abstract base model
UserProfile._meta.get_field('facebook_id').db_index = True

class FacebookUser(models.Model):
    """
    Central repo of facebook users we know about
    these people may or may not be users of the app
    """
    # This needs to have a pk on facebook_id so any updates from
    # new users won't break existing links
    facebook_id = models.BigIntegerField(primary_key=True, db_index=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    first_name = models.CharField(max_length=50, blank=True, null=True)
    gender = models.CharField(choices=(('F', 'female'), ('M', 'male')), blank=True, null=True, max_length=1)
    pic_square = models.CharField(max_length=200, blank=True)

    objects = FacebookUserManager()

    def __str__(self):
        return 'Facebook User %s' % self.name

    class Meta:
        ordering = ['-friend_of__top_friends_order']


class FacebookFriend(models.Model):
    """
    Through model for a M2M (app) User -> FacebookUser
    """
    facebook_user = models.ForeignKey(FacebookUser, related_name='friend_of')
    owner = models.ForeignKey('auth.User',
                              db_index=True,
                              related_name='friends',
                              help_text='App user this person is a friend of')
    top_friends_order = models.PositiveSmallIntegerField(default=0,
                                                         help_text='Higher the better',
                                                         db_index=True)

    class Meta:
        unique_together = ['owner', 'facebook_user']
        ordering = ['-top_friends_order']           # Don't change this! Used to recommend top friends first

    def __str__(self):
        return u'Facebook user %s' % self.facebook_user.name


# Make sure we create a UserProfile when creating a User
@receiver(post_save, sender=User, dispatch_uid='account.models')
def create_user_profile(sender, instance, created, **kwargs):
    if created and instance.username != 'admin':
        UserProfile.objects.create(user=instance)
