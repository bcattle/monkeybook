import logging
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_syncdb
from django.dispatch.dispatcher import receiver
from django.utils import timezone

logger = logging.getLogger(__name__)


class TopFriendStat(models.Model):
    """
    All of the scores we pulled to calculate
    who a user's top friends were
    """
    user = models.ForeignKey('auth.User', related_name='top_friend_stats')
    friend_id = models.BigIntegerField()
    tagged_with = models.PositiveSmallIntegerField(null=True, help_text='How many times you\'re tagged with this person')
    you_posts_to = models.PositiveSmallIntegerField(null=True, help_text='How many times you posted to this person ')
    you_photos_liked = models.PositiveSmallIntegerField(null=True, help_text='How many times you liked a photo from this person')
    you_links_liked = models.PositiveSmallIntegerField(null=True, help_text='How many times you liked a link from this person')
    you_statuses_liked = models.PositiveSmallIntegerField(null=True, help_text='How many times you liked a status from this person')
    them_posts_to = models.PositiveSmallIntegerField(null=True, help_text='How many times they posted to you')
    them_comment_to_photo = models.PositiveSmallIntegerField(null=True, help_text='How many times they commented on your photo')
    them_comment_to_link = models.PositiveSmallIntegerField(null=True, help_text='How many times they commented on your link')
    them_comment_to_status = models.PositiveSmallIntegerField(null=True, help_text='How many times they commented on your status')
    them_like_photo = models.PositiveSmallIntegerField(null=True, help_text='How many times they liked your photo')
    them_like_link = models.PositiveSmallIntegerField(null=True, help_text='How many times they liked your link')
    them_like_status = models.PositiveSmallIntegerField(null=True, help_text='How many times they liked your status')


class InviteRequestSent(models.Model):
    """
    An individual instance of a 'sign my yearbook'
    request sent to a user's facebook friend
    """
    user = models.ForeignKey('auth.User', related_name='invites_sent')
    facebook_id = models.BigIntegerField()
    request_id = models.BigIntegerField()
    sent_at = models.DateTimeField(auto_now_add=True)
    accepted_at = models.DateTimeField(null=True)

    def accepted(self):
        return not self.accepted_at is None


class Badge(models.Model):
    """
    Yearbook "badges" - best smile, most likely to get arrested, etc.
    """
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=200, blank=True)
    icon_small = models.CharField(max_length=200, blank=True)


class BadgeVote(models.Model):
    badge = models.ForeignKey(Badge)
    from_user = models.ForeignKey(User)
    # To a FacebookUser, because the person nominated
    # may or may not be in the app
    to_facebook_user = models.ForeignKey('account.YearbookFacebookUser')
    created_at = models.DateTimeField(auto_now_add=True)


class YearbookSign(models.Model):
    from_user = models.ForeignKey(User)
    text = models.TextField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)


# Make sure we create a UserProfile when creating a User
@receiver(post_syncdb)
def install_badges(sender, **kwargs):
    if not Badge.objects.exists():
        logger.info('Installing badges')
        from voomza.apps.yearbook import factories
        for n in range(factories.NUM_BADGES):
            factories.BadgeFactory.create()
