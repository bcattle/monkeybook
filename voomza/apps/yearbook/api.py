import logging
from collections import defaultdict
from django.utils import timezone
from django_facebook.api import FacebookUserConverter
from django_facebook.signals import facebook_post_store_friends
from django_facebook.utils import get_profile_class
from voomza.apps.core import bulk

logger = logging.getLogger(__name__)

gender_map = defaultdict(lambda: '', female='F', male='M', )

class YearbookFacebookUserConverter(FacebookUserConverter):
    def get_and_store_optional_fields(self, user):
        """
        Pulls any additional fields we want for the user's profile
        right now these are locale, family and significant other
        """
        from voomza.apps.account.models import FamilyConnection, FacebookUser

        me_response = self.open_facebook.get('me', fields=[
            'id', 'name', 'first_name', 'picture', 'gender', 'locale', 'relationship_status',
            'significant_other'
        ])
        family_response = self.open_facebook.get('me/family')

        # Store the info in their profile
        user.profile.locale = me_response.get('locale', '')
        user.profile.relationship_status = me_response.get('relationship_status', '')
        if 'significant_other' in me_response:
            if 'id' in me_response['significant_other']:
                user.profile.significant_other_id = me_response['significant_other']['id']

        pic_square = ''
        if 'picture' in me_response:
            if 'data' in me_response['picture']:
                if 'url' in me_response['picture']['data']:
                    pic_square = me_response['picture']['data']['url']

        # Store a FacebookUser
        if 'id' in me_response:
            # facebook_id is pk, so this should just update db if it already exists
            fu = FacebookUser(
                facebook_id=me_response['id'],
                name=me_response.get('name', ''),
                first_name=me_response.get('first_name', ''),
                pic_square=pic_square,
                gender=gender_map[me_response.get('gender')]
            )
            fu.save()
            user.profile.facebook_user = fu

        user.profile.save()

        # Store the family data, if any
        for person in family_response.get('data'):
            if 'id' in person:
                fc = FamilyConnection(owner=user,
                                      relationship=person.get('relationship', ''),
                                      facebook_id=person['id'])
                fc.save()


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