from __future__ import division, print_function, unicode_literals
from django.db import models
from voomza.apps.core.models import QuerySetSequence
from voomza.apps.core import bulk


class FacebookPhotoManager(models.Manager):
    def from_getter(self, getter):
        """
        Saves photo results to FacebookPhoto models
        """
        facebook_photos = []
        for photo in getter.fields:
            photo_obj = self.model(
                facebook_id  = photo['id'],
                created      = photo['created'],
                height       = photo['height'],
                width        = photo['width'],
                fb_url       = photo['fb_url'],
                caption      = photo.get('caption', '')
            )
            facebook_photos.append(photo_obj)
        bulk.insert_or_update_many(self.model, facebook_photos, exclude_fields=['comments'])
        return self


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

