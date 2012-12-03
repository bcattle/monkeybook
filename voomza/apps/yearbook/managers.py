from django.db import models


class YearbookSignManager(models.Manager):
    def get_in_sign_order(self, user):
        """
        Returns yearbook signs in proper order
        for presentation on the sign yearbooks view.
        (1) people who signed me, I haven't signed
        (2) people who signed me, I have signed
        """
        return self.get_people_who_signed_me_i_havent(user) | \
            self.get_people_who_signed_me_i_have(user)


    def get_people_who_signed_me_i_havent(self, user):
        from voomza.apps.yearbook.models import YearbookSign
        return YearbookSign.objects.filter(from_facebook_user=user.profile.facebook_user)\
            .exclude(to_facebook_user__yearbook_signs_from__to_facebook_user=user.profile.facebook_user)


    def get_people_who_signed_me_i_have(self, user):
        from voomza.apps.yearbook.models import YearbookSign
        return YearbookSign.objects.filter(from_facebook_user=user.profile.facebook_user,
            to_facebook_user__yearbook_signs_from__to_facebook_user=user.profile.facebook_user)

