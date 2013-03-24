import random
from django.test import TestCase
from voomza.apps.account.factories import UserProfileFactory, UserFactory, FacebookFriendFactory, FacebookUserFactory
from voomza.apps.yearbook.factories import YearbookSignFactory
from voomza.apps.yearbook.pages import assign_signs_to_pages

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


class YearbookSignPaginationTestCase(TestCase):
    short_sign = "Remember when we snuck into the pastry shop on 23rd street??? " \
                 "I wont' forget the epic nights out in 2012."
    long_sign = "Remember when we snuck into the pastry shop on 23rd street??? " \
                "I won't forget the epic nights out in 2012. I won't forget " \
                "the epic nights out in 2012.  To many more in 2013!!"

    def get_signs(self, short=0, long=0):
        signs = []
        [signs.append(self.short_sign) for n in range(short)]
        [signs.append(self.long_sign) for n in range(long)]
        random.shuffle(signs)
        return signs

    def test_all_short(self):
        import ipdb
        ipdb.set_trace()

        signs = self.get_signs(short=8)
        pages = assign_signs_to_pages(signs)
        # 2 pages: 6 on the first, 2 on the second
        self.assertEqual(len(pages), 2)
        self.assertEqual(len(pages[0]), 6)
        self.assertEqual(len(pages[1]), 2)


    def test_all_long(self):
        self.assertEqual(1 + 1, 2)

    def test_1_long(self):
        self.assertEqual(1 + 1, 2)

    def test_2_long(self):
        self.assertEqual(1 + 1, 2)

    def test_5_long(self):
        self.assertEqual(1 + 1, 2)

