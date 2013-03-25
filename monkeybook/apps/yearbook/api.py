import logging
from collections import defaultdict
from django.utils import timezone
from django_facebook.api import FacebookUserConverter

logger = logging.getLogger(__name__)

gender_map = defaultdict(lambda: '', female='F', male='M', )

class YearbookFacebookUserConverter(FacebookUserConverter):
    def delete_request(self, request):
        """
        Deletes an app request, e.g. after a user
        accepts an invitiation they were sent by another user
        """
        # DELETE https://graph.facebook.com/[<REQUEST_OBJECT_ID>_<USER_ID>]?
        #   access_token=[USER or APP ACCESS TOKEN]
        delete_id = '%s_%s' % (request.request_id, request.to_facebook_user_id)
        resp = self.open_facebook.delete(delete_id)
        if resp:
            request.accepted_at = timezone.now()
            request.save()
        else:
            logger.warning('Tried to delete invite request id %s, facebook returned False' % delete_id)