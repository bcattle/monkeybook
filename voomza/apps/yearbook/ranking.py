from voomza.apps.yearbook.models import YearbookSign

class FriendRanking(object):
    """
    This class is responsible for several types of ranking
    performed with a UserProfile that are relevant to the yearbook
    """
    def __init__(self, profile):
        self.profile = profile

    def get_top_friends(self):
#        return FacebookFriend.objects.filter(owner=self.profile.user).exclude(top_friends_order=0)
        return self.profile.user.friends.exclude(top_friends_order=0)

    def get_non_top_friends(self):
#        return FacebookFriend.objects.filter(owner=self.profile.user).filter(top_friends_order=0)
        return self.profile.user.friends.filter(owner=self.profile.user).filter(top_friends_order=0)

    def not_in_app(self, query):
        return query.filter(facebook_user__profile__isnull=True)

    def in_app(self, query):
        return query.filter(facebook_user__profile__isnull=False)

    def i_havent_signed(self, query):
        return query.exclude(
            facebook_user__yearbook_signs_to__from_facebook_user=self.profile.facebook_user
        )

    def havent_signed_me(self, query):
        return query.exclude(
            facebook_user__yearbook_signs_from__to_facebook_user=self.profile.facebook_user
        )

    def get_people_who_signed_me_i_havent(self):
        return YearbookSign.objects.filter(from_facebook_user=self.profile.facebook_user)\
            .exclude(to_facebook_user__yearbook_signs_from__to_facebook_user=self.profile.facebook_user)

    def get_people_who_signed_me_i_have(self):
        return YearbookSign.objects.filter(from_facebook_user=self.profile.facebook_user,
            to_facebook_user__yearbook_signs_from__to_facebook_user=self.profile.facebook_user)

    def get_yearbooks_to_sign(self):
        """
        Gets yearbooks in the order we think people will want them.
          Starts with people who haven't signed yours,
          starting with top friends *NOT* in the app,
          top friends in the app, regular friends not in the app, regular
          friends in the app.
        """
        ## -- For all of these, exclude anyone who I have already signed

        # Then, top friends who aren't currently using the app
        # APPROX 45
        top_friends_not_in_app = self.i_havent_signed(self.not_in_app(self.get_top_friends()))

        # Then top friends who are
        # APPROX 5
        # exclude ppl who signed me
        top_friends_in_app = self.havent_signed_me(self.i_havent_signed(self.in_app(self.get_top_friends())))

        # Non-top friends who are
        # APPROX 100
        # exclude people who signed me
        friends_in_app = self.havent_signed_me(self.i_havent_signed(self.in_app(self.get_non_top_friends())))

        # Non-top friends who don't use the app
        # APPROX 800
        friends_not_in_app = self.i_havent_signed(self.not_in_app(self.get_non_top_friends()))

        # Pretty small, grand total ~ 1000
        # will get called for pagination infrequently w/ small page sizes
        return top_friends_not_in_app | top_friends_in_app | friends_in_app | friends_not_in_app
