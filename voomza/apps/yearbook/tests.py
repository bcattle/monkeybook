"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
from django.contrib.auth.models import User

from django.test import TestCase
from voomza.apps.account.factories import UserProfileFactory, UserFactory, YearbookFacebookUserFactory
from voomza.apps.yearbook.factories import YearbookSignFactory


class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)


def set_up_yearbooksign_models():
    """
    Sets up a variety of models to test the `get_yearbooks_to_sign` view.

    """
    # Chuck Norris
    #   signed Harry's yearbook
    #   Johnny Depp signed his
    #   has one top friend on the site      Sean Connery
    #   has two friends *not* on the site   Pierce Brosnan (top friend)
    #                                       Roger Moore (not top friend)


    # We have to create Users, then modify the UserProfiles
    # that were automatically created by the `post_save` flag
    chuck_fb_id = 111
    chuck = UserFactory(username='cnorris').build()
    chuck.save()
    chuck.profile.facebook_id=chuck_fb_id
    chuck.profile.save()

    harry_fb_id = 222
    harry = UserFactory(username='hpotter')
    harry.profile.facebook_id=harry_fb_id
    harry.profile.save()

    YearbookSignFactory(from_user=chuck, to_id=harry_fb_id)

    johnny_fb_id = 333
    johnny = UserFactory(username='jdepp')
    johnny.profile.facebook_id=johnny_fb_id
    johnny.profile.save()

    YearbookSignFactory(from_user=johnny, to_id=chuck_fb_id)

    sean_fb_id = 444
    sean = UserFactory(username='jdepp')
    sean.profile.facebook_id=sean_fb_id
    sean.profile.save()

    # Top friend of Johnny

    YearbookFacebookUserFactory(
        user=johnny,
        facebook_id=sean_fb_id,
        name='Sean Connery',
        top_friends_order=1
    )

    YearbookFacebookUserFactory(
        user=johnny,
        facebook_id=555,
        name='Pierce Brosnan',
        top_friends_order=2
    )

    YearbookFacebookUserFactory(
        user=johnny,
        facebook_id=666,
        name='Roger Moore',
    )


def set_up_yearbooksign_models_nofactory():
    """
    Sets up a variety of models to test the `get_yearbooks_to_sign` view.

    """
    # Chuck Norris
    #   signed Harry's yearbook
    #   Johnny Depp signed his
    #   has one top friend on the site      Sean Connery
    #   has two friends *not* on the site   Pierce Brosnan (top friend)
    #                                       Roger Moore (not top friend)


    # We have to create Users, then modify the UserProfiles
    # that were automatically created by the `post_save` flag
    chuck_fb_id = 111
    chuck = User.objects.create_user(username='cnorris')
    chuck.profile.facebook_id=chuck_fb_id
    chuck.profile.save()

    timothy_fb_id = 777
    timothy = User.objects.create_user(username='tdalton')
    timothy.profile.facebook_id=timothy_fb_id
    timothy.profile.save()

    YearbookSignFactory(from_user=chuck, to_id=timothy_fb_id)
    YearbookSignFactory(from_user=timothy, to_id=chuck_fb_id)

    harry_fb_id = 222
    harry = User.objects.create_user(username='hpotter')
    harry.profile.facebook_id=harry_fb_id
    harry.profile.save()

    YearbookSignFactory(from_user=chuck, to_id=harry_fb_id)

    johnny_fb_id = 333
    johnny = User.objects.create_user(username='jdepp')
    johnny.profile.facebook_id=johnny_fb_id
    johnny.profile.save()

    YearbookSignFactory(from_user=johnny, to_id=chuck_fb_id)

    sean_fb_id = 444
    sean = User.objects.create_user(username='sconnery')
    sean.profile.facebook_id=sean_fb_id
    sean.profile.save()

    # Top friend of Johnny

    YearbookFacebookUserFactory(
        user=chuck,
        facebook_id=sean_fb_id,
        name='Sean Connery',
        top_friends_order=1
    )

    YearbookFacebookUserFactory(
        user=chuck,
        facebook_id=555,
        name='Pierce Brosnan',
        top_friends_order=2
    )

    YearbookFacebookUserFactory(
        user=chuck,
        facebook_id=666,
        name='Roger Moore',
    )
