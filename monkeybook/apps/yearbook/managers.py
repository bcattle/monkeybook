from django.db import models
from voomza.apps.core.models import QuerySetSequence


class YearbookSignManager(models.Manager):
    def get_in_sign_order(self, user):
        """
        Returns yearbook signs in proper order
        for presentation on the sign yearbooks view.
        (1) people who signed me, I haven't signed
        (2) people who signed me, I have signed
        """
#        return self.get_people_who_signed_me_i_havent(user) | \
#            self.get_people_who_signed_me_i_have(user)
#        return self.get_people_who_signed_me_i_havent(user)
        return QuerySetSequence(
            self.get_people_who_signed_me_i_havent(user).extra(select={'can_sign': 'SELECT 1'}),
            self.get_people_who_signed_me_i_have(user).extra(select={'can_sign': 'SELECT 0'})
        )

    def get_my_yearbook_signs(self, user):
        from voomza.apps.yearbook.models import YearbookSign
        return YearbookSign.objects.filter(to_facebook_user=user.profile.facebook_user)

    def get_people_who_signed_me_i_havent(self, user):
        from voomza.apps.yearbook.models import YearbookSign
        return YearbookSign.objects.filter(to_facebook_user=user.profile.facebook_user) \
            .exclude(from_facebook_user__yearbook_signs_to__from_facebook_user=user.profile.facebook_user)


    def get_people_who_signed_me_i_have(self, user):
        from voomza.apps.yearbook.models import YearbookSign
        return YearbookSign.objects.filter(to_facebook_user=user.profile.facebook_user,
            from_facebook_user__yearbook_signs_to__from_facebook_user=user.profile.facebook_user)


class InviteRequestSentManager(models.Manager):
    def outstanding_invites(self):
        return self.filter(accepted_at__isnull=True)