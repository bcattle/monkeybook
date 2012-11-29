import logging
from django.db import models
from django.db.models.signals import post_save
from django.dispatch.dispatcher import receiver
from django.contrib.auth.models import User
from django_facebook.models import BaseFacebookProfileModel
from voomza.apps.account.managers import FacebookFriendManager

logger = logging.getLogger(name=__name__)


class UserProfile(BaseFacebookProfileModel):
    """
    Created by a hook into the post_save signal on User
    """
    user = models.OneToOneField('auth.User', related_name='profile')
    facebook_user = models.ForeignKey('FacebookUser', null=True, related_name='profile')
    first_name = models.CharField(max_length=40, blank=True)
    locale = models.CharField(max_length=10, blank=True)
    pic_square = models.CharField(max_length=200, blank=True)

    current_page = models.CharField(max_length=40, default='invite_friends_to_sign')


### Add an index to the facebook_id field
## Done here because it lives in abstract base model
UserProfile._meta.get_field('facebook_id').db_index = True

class FacebookUser(models.Model):
    """
    Central repo of facebook users we know about
    these people may or may not be users of the app
    """
    facebook_id = models.BigIntegerField(primary_key=True, db_index=True)
    name = models.TextField(blank=True, null=True)
    gender = models.CharField(choices=(('F', 'female'), ('M', 'male')), blank=True, null=True, max_length=1)
    pic_square = models.CharField(max_length=200, blank=True)


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
    objects = FacebookFriendManager()

    class Meta:
        unique_together = ['owner', 'facebook_user']
        ordering = ['-top_friends_order']           # Don't change this! Used to recommend top friends first

    def __unicode__(self):
        return u'Facebook user %s' % self.facebook_user.name


# Make sure we create a UserProfile when creating a User
@receiver(post_save, sender=User, dispatch_uid='account.models')
def create_user_profile(sender, instance, created, **kwargs):
    if created and instance.username != 'admin':
        UserProfile.objects.create(user=instance)

#        # Getting called twice due to bogus imports somewhere else
#        try:
#            profile = instance.profile
#        except UserProfile.DoesNotExist:
#            print 'UserProfile create called()'
#            UserProfile.objects.create(user=instance)

