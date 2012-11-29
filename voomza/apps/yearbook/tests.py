"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
from django.contrib.auth.models import User

from django.test import TestCase
from voomza.apps.account.factories import UserProfileFactory, UserFactory, FacebookFriendFactory
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
    harry = UserFactory(username='hpotter')
    YearbookSignFactory(from_user=chuck, to_id=harry.profile.facebook_id)

    johnny = UserFactory(username='jdepp')
    YearbookSignFactory(from_user=johnny, to_id=chuck.profile.facebook_id)

    sean = UserFactory(username='sconnery')

    # Top friend of Johnny
    FacebookFriendFactory(
        owner=johnny,
        facebook_user=sean.profile.facebook_user,
        name='Sean Connery',
        top_friends_order=1
    )

    FacebookFriendFactory(
        owner=johnny,
        name='Pierce Brosnan',
        top_friends_order=2
    )

    FacebookFriendFactory(
        owner=johnny,
        name='Roger Moore',
    )
