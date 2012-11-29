"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
from django.contrib.auth.models import User

from django.test import TestCase
from voomza.apps.account.factories import UserProfileFactory, UserFactory, FacebookFriendFactory, FacebookUserFactory
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
    chuck = UserFactory(username='cnorris')
    chuck.profile.delete()
    chuck.profile = UserProfileFactory(user=chuck)
    harry = UserFactory(username='hpotter')
    harry.profile.delete()
    harry.profile = UserProfileFactory(user=harry)
    YearbookSignFactory(from_facebook_user=chuck.profile.facebook_user,
                        to_facebook_user=harry.profile.facebook_user)

    johnny = UserFactory(username='jdepp')
    johnny.profile.delete()
    johnny.profile = UserProfileFactory(user=johnny)
    YearbookSignFactory(from_facebook_user=johnny.profile.facebook_user,
                        to_facebook_user=chuck.profile.facebook_user)

    sean = UserFactory(username='sconnery')
    sean.profile.delete()
    sean.profile = UserProfileFactory(user=sean)

    # Top friend of Johnny
    FacebookFriendFactory(
        owner=chuck,
        facebook_user=sean.profile.facebook_user,
        top_friends_order=1
    )

    pierce = FacebookUserFactory(name='Pierce Brosnan')
    FacebookFriendFactory(
        facebook_user=pierce,
        owner=chuck,
        top_friends_order=2
    )

    roger= FacebookUserFactory(name='Roger Moore')
    FacebookFriendFactory(
        facebook_user=roger,
        owner=chuck,
    )

    timothy = UserFactory(username='tdalton')
    timothy.profile.delete()
    timothy.profile = UserProfileFactory(user=timothy)
    YearbookSignFactory(from_facebook_user=timothy.profile.facebook_user,
                        to_facebook_user=chuck.profile.facebook_user)
    YearbookSignFactory(from_facebook_user=chuck.profile.facebook_user,
                        to_facebook_user=timothy.profile.facebook_user)