from __future__ import division, print_function, unicode_literals
import logging
from django.db import models
from django.utils import timezone
from voomza.apps.viral.managers import InviteRequestSentManager
from voomza.lib.django_facebook.api import FacebookUserConverter

logger = logging.getLogger(__name__)


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

    class Meta:
        verbose_name_plural = 'Invite requests sent'

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
