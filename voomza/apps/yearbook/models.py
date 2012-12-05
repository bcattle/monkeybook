import logging
from django.db import models
from django.db.models.signals import post_save
from django.dispatch.dispatcher import receiver
from voomza.apps.yearbook.managers import YearbookSignManager, InviteRequestSentManager
from yearbook.tasks import accept_invite_requests

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
    from_user = models.ForeignKey('auth.User', related_name='invites_sent')
    to_facebook_user = models.ForeignKey('account.FacebookUser')
    request_id = models.BigIntegerField()
    sent_at = models.DateTimeField(auto_now_add=True)
    accepted_at = models.DateTimeField(null=True)

    objects = InviteRequestSentManager()


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



@receiver(post_save, sender=YearbookSign, dispatch_uid='yearbook.models')
def post_save_yearbook_sign(instance, **kwargs):
    """
    After we save a YearbookSign,
    we check to make sure the user didn't have an outstanding
    "request" from the user - if they did, delete it.
    Also send a notification to the user who they signed
    """
    # instance.from_facebook_user       in the app
    # instance.to_facebook_user         may/may not be in the app
    pending_request = InviteRequestSent.objects.outstanding_invites().filter(
        from_user__profile__facebook_user=instance.to_facebook_user,
        to_facebook_user=instance.from_facebook_user
    )
    if pending_request.exists():
        logger.info('Found pending invite request')
        # Accept the request
        accept_invite_requests(pending_request)
#        accept_invite_requests.delay(pending_request)

    # Send instance.to_facebook_user a notification
    # that someone signed their yearbook
    # if they are in the app and no wall post was sent
    # TODO: have no way of detecting whether wall post went through or not
    # until the fb x-domain issue is fixed
        pass
