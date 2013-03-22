from __future__ import division, print_function, unicode_literals
import logging
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from voomza.apps.viral.managers import SentInviteManager
from voomza.apps.viral.tasks import accept_invite_requests
from voomza.lib.django_facebook.api import FacebookUserConverter

logger = logging.getLogger(__name__)


class SentInvite(models.Model):
    """
    An individual instance of a 'sign my yearbook'
    request sent to a user's facebook friend
    """
    from_user = models.ForeignKey('auth.User', related_name='invites_sent')
    to_facebook_user = models.ForeignKey('account.FacebookUser')
    request_id = models.BigIntegerField()
    sent_at = models.DateTimeField(auto_now_add=True)
    accepted_at = models.DateTimeField(null=True)

    objects = SentInviteManager()

    class Meta:
        verbose_name_plural = 'Invites sent'

    def delete_request(self, user):
        """
        Deletes an app request, e.g. after a user
        accepts an invitation they were sent by another user
        """
        graph = user.profile.get_offline_graph()
        facebook = FacebookUserConverter(graph)

        # DELETE https://graph.facebook.com/[<REQUEST_OBJECT_ID>_<USER_ID>]?
        #   access_token=[USER or APP ACCESS TOKEN]
        delete_id = '%s_%s' % (self.request_id, self.to_facebook_user_id)
        resp = facebook.open_facebook.delete(delete_id)
        if resp:
            self.accepted_at = timezone.now()
            self.save()
        else:
            logger.warning('Tried to delete invite request id %s, facebook returned False' % delete_id)


class YearbookSign(models.Model):
#    from_user = models.ForeignKey(User, related_name='yearbook_signs')
    from_facebook_user = models.ForeignKey('account.FacebookUser', related_name='yearbook_signs_from')
    to_facebook_user = models.ForeignKey('account.FacebookUser', related_name='yearbook_signs_to')
    text = models.TextField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    objects = SentInviteManager()

    class Meta:
        ordering = ['-created_at']


@receiver(post_save, sender=YearbookSign, dispatch_uid='viral.models')
def post_save_yearbook_sign(instance, **kwargs):
    """
    After we save a YearbookSign,
    we check to make sure the user didn't have an outstanding
    "request" from the user - if they did, delete it.
    Also send a notification to the user who they signed
    """
    # instance.from_facebook_user       in the app
    # instance.to_facebook_user         may/may not be in the app
    pending_request = SentInvite.objects.outstanding_invites().filter(
        from_user__profile__facebook_user=instance.to_facebook_user,
        to_facebook_user=instance.from_facebook_user
    )
    if pending_request.exists():
        logger.info('Found pending invite request')
        # Accept the request
        accept_invite_requests.delay(pending_request)

    # If we signed someone's yearbook, and they signed ours,
    # post the "signed yearbooks" open graph event with both users tagged
    if YearbookSign.objects.filter(
            from_facebook_user=instance.to_facebook_user,
            to_facebook_user=instance.from_facebook_user
    ).exists():
        # Share the open graph action
        pass

        # Send instance.to_facebook_user a notification
        # that someone signed their yearbook
        # if they are in the app and no wall post was sent
        # TODO: have no way of detecting whether wall post went through or not
        # until the fb x-domain issue is fixed
        pass
