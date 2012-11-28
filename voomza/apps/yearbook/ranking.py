import collections
import itertools
from django.contrib.auth.models import User
from voomza.apps.account.models import YearbookFacebookUser
from voomza.apps.yearbook.models import YearbookSign

class UserProfileRanking(object):
    """
    This class is responsible for several types of ranking
    performed with a UserProfile that are relevant to the yearbook
    """
    def __init__(self, profile):
        self.profile = profile

    def get_top_friends_not_in_app(self):
        """
        User's fb friends with top_friends_order != 0
        who aren't currently users of the app
        """
        # It is MUCH FASTER to do a JOIN here rather than NOT IN,
        # see http://stackoverflow.com/a/1519333/1161906
        return YearbookFacebookUser.objects.raw('''
            SELECT `account_yearbookfacebookuser`.* FROM `account_yearbookfacebookuser`
                LEFT JOIN `account_userprofile`
                ON `account_userprofile`.`facebook_id`=`account_yearbookfacebookuser`.`facebook_id`
            WHERE (`account_yearbookfacebookuser`.`user_id` = %d
                AND `account_userprofile`.`facebook_id` IS NULL
                AND `account_yearbookfacebookuser`.`top_friends_order` != 0)
            ORDER BY `account_yearbookfacebookuser`.`top_friends_order` DESC
        ''' % self.profile.user.id)

        # Would setting primary_key=True on facebook_id get rid of some of this?

    def get_top_friends_in_app(self):
        """
        User's fb friends with top_friends_order != 0
        who ARE currently users of the app
        """
        return YearbookFacebookUser.objects.raw('''
            SELECT `account_yearbookfacebookuser`.* FROM `account_yearbookfacebookuser`
                LEFT JOIN `account_userprofile`
                ON `account_userprofile`.`facebook_id`=`account_yearbookfacebookuser`.`facebook_id`
            WHERE (`account_yearbookfacebookuser`.`user_id` = %d
                AND `account_userprofile`.`facebook_id` IS NOT NULL
                AND `account_yearbookfacebookuser`.`top_friends_order` != 0)
            ORDER BY `account_yearbookfacebookuser`.`top_friends_order` DESC
        ''' % self.profile.user.id)

    def get_friends_not_in_app(self):
        """
        User's fb friends with top_friends_order == 0
        who aren't currently users of the app
        """
        # It is MUCH FASTER to do a JOIN here rather than NOT IN,
        # see http://stackoverflow.com/a/1519333/1161906
        return YearbookFacebookUser.objects.raw('''
            SELECT `account_yearbookfacebookuser`.* FROM `account_yearbookfacebookuser`
                LEFT JOIN `account_userprofile`
                ON `account_userprofile`.`facebook_id`=`account_yearbookfacebookuser`.`facebook_id`
            WHERE (`account_yearbookfacebookuser`.`user_id` = %d
                AND `account_userprofile`.`facebook_id` IS NULL
                AND `account_yearbookfacebookuser`.`top_friends_order` = 0)
            ORDER BY `account_yearbookfacebookuser`.`top_friends_order` DESC
        ''' % self.profile.user.id)

    def get_friends_in_app(self):
        """
        User's fb friends with top_friends_order == 0
        who ARE currently users of the app
        """
        return YearbookFacebookUser.objects.raw('''
            SELECT `account_yearbookfacebookuser`.* FROM `account_yearbookfacebookuser`
                LEFT JOIN `account_userprofile`
                ON `account_userprofile`.`facebook_id`=`account_yearbookfacebookuser`.`facebook_id`
            WHERE (`account_yearbookfacebookuser`.`user_id` = %d
                AND `account_userprofile`.`facebook_id` IS NOT NULL
                AND `account_yearbookfacebookuser`.`top_friends_order` = 0)
            ORDER BY `account_yearbookfacebookuser`.`top_friends_order` DESC
        ''' % self.profile.user.id)

    def get_yearbooks_to_sign(self):
        """
        Gets yearbooks in the order we think people will want them.
          Starts with people who have signed yours,
          then people who haven't starting with top friends *NOT* in the app,
          top friends in the app, regular friends not in the app, regular
          friends in the app.
        """
        ## -- For all of these, exclude anyone who I have already signed

        # Everyone who has signed this person's yearbook
        # APPROX 10
        people_who_signed_me = User.objects.filter(
            yearbook_signs__to_id=self.profile.facebook_id
        )

        # First, they see anyone who has signed
        # *their* yearbook who *they* haven't signed
        # APPROX 10

        # facebook ids I've signed
        #                 ( set comprehension )
        fb_ids_I_signed = {ybs.to_id for ybs in YearbookSign.objects.filter(from_user=self.profile.user)}
        people_who_signed_i_havent = people_who_signed_me.exclude(
            profile__facebook_id__in=fb_ids_I_signed
        )

        # Then, top friends who aren't currently using the app
        # APPROX 45
        top_friends_not_in_app = self.get_top_friends_not_in_app()

        # Then top friends who are
        # APPROX 5
        top_friends_in_app = self.get_top_friends_in_app()

        # Non-top friends who are
        # APPROX 100
        friends_in_app = self.get_friends_in_app()

        # Non-top friends who don't use the app
        # APPROX 800
        friends_not_in_app = self.get_friends_not_in_app()

        # Pretty small, grand total ~ 1000
        # will get called for pagination infrequently w/ small page sizes

        # Do this to avoid having to do a manual JOIN on
        # yearbook_sign.to_id = user_profile.facebook_id
        people_who_signed_me_ids = {u.profile.facebook_id for u in people_who_signed_me}

        # Construct the whole list, excluding everyone who's signed me
        all_who_havent_signed = [x for x in itertools.chain(top_friends_not_in_app, top_friends_in_app,
            friends_in_app, friends_not_in_app)
                if x.facebook_id not in fb_ids_I_signed
                and x.facebook_id not in people_who_signed_me_ids]

        # Prepend the first list
        # deque is a little structure that is good at being prepended to
        # http://docs.python.org/2/library/collections.html#collections.deque
        all_yearbooks = collections.deque(all_who_havent_signed)
        # Reversed since it extends 0->n, reversing the order
        all_yearbooks.extendleft(reversed(people_who_signed_i_havent))
        return all_yearbooks
