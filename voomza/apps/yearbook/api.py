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
    """
    This class provides a mapping of facebook user objects
    to our Django models. We override here for customization
    """
    def get_friends(self, limit=5000):
        """
        Connects to the facebook api and gets the users friends
        """
        friends = getattr(self, '_friends', None)
        if friends is None:
            friends_response = self.open_facebook.fql('''
                SELECT uid, name, first_name, sex, pic_square FROM user
                    WHERE uid IN (SELECT uid2 FROM friend WHERE uid1 = me())
                LIMIT %s
                ''' % limit)
            friends = []
            for response_dict in friends_response:
                response_dict['id'] = response_dict['uid']
                friends.append(response_dict)

        logger.info('found %s friends', len(friends))
        return friends


    @classmethod
    def _store_friends(cls, user, friends):
        # store the users for later retrieval
        if friends:
            from voomza.apps.account.models import FacebookUser, FacebookFriend

            facebook_friends = []
            facebook_users = []
            # APPROX 50
            current_friend_ids = set(FacebookFriend.objects.filter(owner=user).values_list('facebook_user__facebook_id', flat=True))
            for f in friends:
                if f.get('id') and f['id'] not in current_friend_ids:
                    facebook_users.append(
                        FacebookUser(
                            facebook_id = f['id'],
                            name        = f.get('name', ''),
                            first_name        = f.get('first_name', ''),
                            pic_square  = f.get('pic_square', ''),
                            gender      = gender_map[f.get('sex', '')]
                        )
                    )
                    facebook_friends.append(
                        FacebookFriend(
                            owner            = user,
                            facebook_user_id = f['id']
                        )
                    )
            # Use the "bulk" library rather than the built-in `bulk_create`
            # so we can specify ON DUPLICATE KEY UPDATE
            bulk.insert_or_update_many(FacebookUser, facebook_users)
            bulk.insert_many(FacebookFriend, facebook_friends)

            logger.debug('Pulled all friends, found %s friends', len(friends))

        # fire an event, note that it doesn't have `current_friends` or `inserted_friends`
        facebook_post_store_friends.send(sender=get_profile_class(),
            user=user, friends=friends, current_friends=None,
            inserted_friends=None,
        )
        return friends


    def get_and_store_top_friends_fast(self, user):
        """
        Gets the users friends using the "quick" algorithm
        """
        # If they already have any top friends, skip
        if user.friends.exclude(top_friends_order=0).exists():
            logger.debug('User already has top friends, skipping "fast algorithm"')
            return

        # Who are they in the most photos with?
        results = self.open_facebook.batch_fql({
            'all_friend_ids': 'SELECT uid2 FROM friend WHERE uid1 = me()',

            'tagged_photos': 'SELECT subject FROM photo_tag WHERE object_id IN '
                             '       (SELECT object_id FROM photo_tag WHERE subject=me()) AND subject!=me() '
                             'LIMIT 300',

            'tagged_users': 'SELECT uid, first_name, name, sex, pic_square FROM user WHERE uid IN '
                            '   (SELECT subject FROM photo_tag WHERE object_id IN '
                            '       (SELECT object_id FROM photo_tag WHERE subject=me()) AND subject!=me()) '
                            'LIMIT 300',
        })
        # TODO: re-write this to replace the call in TaggedWithMe
        from voomza.apps.backend.getter import ResultGetter, FreqDistResultGetter

        all_friend_ids = ResultGetter(results['all_friend_ids'], id_field='uid2')
        # Collapse to a count, filter out anyone we're not still friends with
        tagged_ids = FreqDistResultGetter(results['tagged_photos'], id_field='subject')\
            .filter(lambda x: x['id'] in all_friend_ids.ids)
        tagged_users = ResultGetter(
            results['tagged_users'],
            fields=['first_name', 'name', 'pic_square', 'sex'],
            extra_fields={'gender': lambda x: gender_map[x.get('sex')]},
            id_field='uid'
        )

        # Join on how many photos the person is tagged in
        top_friends = tagged_users.join_on_field(tagged_ids).order_by('count')

        # First, create FacebookUser for all pulled users
        # since there is a pk on facebook_id, this will update any existing entries
        # we save facebook_id, name, and pic_square
        from voomza.apps.account.models import FacebookUser, FacebookFriend

        facebook_users = []
        facebook_friends = []
        # Reversing them means the index corresponds to top friends order
        for top_friends_order, u in enumerate(reversed(top_friends)):
            facebook_users.append(
                FacebookUser(
                    facebook_id = u['id'],
                    name        = u['name'],
                    first_name  = u['first_name'],
                    pic_square  = u['pic_square'],
                    gender      = u['gender']
                )
            )
            facebook_friends.append(
                FacebookFriend(
                    owner             = user,
                    facebook_user_id  = u['id'],
                    top_friends_order = top_friends_order
                )
            )
        bulk.insert_or_update_many(FacebookUser, facebook_users)
        bulk.insert_many(FacebookFriend, facebook_friends)

        logger.info('found %s top friends', len(top_friends))

        # Return the queryset of top friends
        return FacebookUser.objects.filter(friend_of__owner=user)


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