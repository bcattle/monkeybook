import logging
from django.db import models
from voomza.apps.yearbook.managers import YearbookSignManager

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
    facebook_user = models.ForeignKey('account.FacebookUser')
    request_id = models.BigIntegerField()
    sent_at = models.DateTimeField(auto_now_add=True)
    accepted_at = models.DateTimeField(null=True)

    def accepted(self):
        return not self.accepted_at is None


class YearbookSign(models.Model):
#    from_user = models.ForeignKey(User, related_name='yearbook_signs')
    from_facebook_user = models.ForeignKey('account.FacebookUser', related_name='yearbook_signs_from')
    to_facebook_user = models.ForeignKey('account.FacebookUser', related_name='yearbook_signs_to')
    text = models.TextField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    objects = YearbookSignManager()

    class Meta:
        ordering = ['-created_at']

