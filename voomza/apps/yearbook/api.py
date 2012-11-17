import logging, timeit
from collections import OrderedDict
from django_facebook.api import FacebookUserConverter
from django_facebook.signals import facebook_post_store_friends
from django_facebook.utils import get_profile_class, mass_get_or_create
from voomza.apps.account.models import YearbookFacebookUser
from voomza.apps.yearbook import settings as yearbook_settings
from voomza.apps.yearbook.models import TopFriendStat

logger = logging.getLogger(__name__)

gender_map = dict(female='F', male='M')

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
            friends_response = self.open_facebook.fql(
                "SELECT uid, name, sex, pic_small FROM user WHERE uid IN (SELECT uid2 "
                "FROM friend WHERE uid1 = me()) LIMIT %s" % limit)
            friends = []
            for response_dict in friends_response:
                response_dict['id'] = response_dict['uid']
                friends.append(response_dict)

        logger.info('found %s friends', len(friends))
        return friends


    @classmethod
    def _store_friends(cls, user, friends):
        current_friends = inserted_friends = None

        #store the users for later retrieval
        if friends:
            #see which ids this user already stored
            base_queryset = YearbookFacebookUser.objects.filter(user_id=user.id)
            #if none if your friend have a gender clean the old data
            genders = YearbookFacebookUser.objects.filter(
                user_id=user.id, gender__in=('M', 'F')).count()
            if not genders:
                YearbookFacebookUser.objects.filter(user_id=user.id).delete()

            global_defaults = dict(user_id=user.id)
            default_dict = {}
            for f in friends:
                name = f.get('name')
                pic_small = f.get('pic_small')
                gender = None
                if f.get('sex'):
                    gender = gender_map[f.get('sex')]
                default_dict[str(f['id'])] = dict(name=name, gender=gender, pic_small=pic_small)
            id_field = 'facebook_id'

            current_friends, inserted_friends = mass_get_or_create(
                YearbookFacebookUser, base_queryset, id_field, default_dict,
                global_defaults)
            logger.debug('found %s friends and inserted %s new ones',
                len(current_friends), len(inserted_friends))

        #fire an event, so u can do things like personalizing suggested users
        #to follow
        facebook_post_store_friends.send(sender=get_profile_class(),
            user=user, friends=friends, current_friends=current_friends,
            inserted_friends=inserted_friends,
        )

        return friends


    def get_and_store_top_friends_fast(self, user):
        """
        Gets the users friends using the "quick" algorithm
        """
        # If they already have any top friends, skip
        if YearbookFacebookUser.objects.filter(user=user).exclude(top_friends_order=0).exists():
            logger.debug('User already has top friends, skipping "fast algorithm"')
            return

        # Who are they in the most photos with?
        results = self.open_facebook.batch_fql({
            'tagged_photos': 'SELECT subject FROM photo_tag WHERE object_id IN '
                             '       (SELECT object_id FROM photo_tag WHERE subject=me()) AND subject!=me() '
                             'LIMIT 100',

            'tagged_users': 'SELECT uid, name, sex, pic_small FROM user WHERE uid IN '
                            '   (SELECT subject FROM photo_tag WHERE object_id IN '
                            '       (SELECT object_id FROM photo_tag WHERE subject=me()) AND subject!=me()) '
                            'LIMIT 100'
        })
        tagged_photos = results['tagged_photos']
        tagged_users = results['tagged_users']

        # Collapse to a frequencies and user_ids
        all_ids = []
        for photo in tagged_photos:
            try:
                all_ids.append(int(photo['subject']))
            # Skip anything that's not an integer
            except ValueError: pass

        all_users = {}
        for u in tagged_users:
            try:
                all_users[int(u['uid'])] = u
            # Skip anything that's not an integer
            except ValueError: pass

        counted = [(id, all_ids.count(id)) for id in all_ids]
        counted_in_order = OrderedDict(sorted(counted, key=lambda t: t[1]))

        # Holds {user_id: rank="topness index", other fields... }
        friends_ranked = {}
        for index,id in enumerate(counted_in_order):
            try:
                f = dict(top_friends_order=index+1, **all_users[id])
                f.pop('uid')
                if f.get('sex'):
                    f['gender'] = gender_map[f.get('sex')]
                    f.pop('sex')
                friends_ranked[str(id)] = f
            except KeyError: pass

        # Only updates if they don't already exist
        # i.e. this shouldn't overwrite the "non-fast" algorithm
        current, created = mass_get_or_create(
            model_class=YearbookFacebookUser,
            base_queryset=YearbookFacebookUser.objects.filter(user_id=user.id),
            id_field='facebook_id',
            default_dict=friends_ranked,
            global_defaults=dict(user_id=user.id),
        )

        # Save the counts for debugging?
        if yearbook_settings.STORE_TOP_FRIEND_STATS:
            counts_for_db = {str(id): dict(tagged_with=count) for id,count in counted_in_order.items()}
            # We don't overwrite existing entries
            mass_get_or_create(
                model_class=TopFriendStat,
                base_queryset=TopFriendStat.objects.filter(user=user),
                id_field='friend_id',
                default_dict=counts_for_db,
                global_defaults=dict(user=user),
            )

        logger.info('found %s top friends', len(all_users))

