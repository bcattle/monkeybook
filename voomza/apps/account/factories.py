import factory
from django.contrib.auth.models import User
from voomza.apps.account.models import UserProfile, FacebookUser, FacebookFriend

class UserFactory(factory.Factory):
    FACTORY_FOR = User
#    username = 'cnorris'

    @classmethod
    def _prepare(cls, create, **kwargs):
        password = kwargs.pop('password', None)
        user = super(UserFactory, cls)._prepare(create, **kwargs)
        if password:
            user.set_password(password)
            if create:
                user.save()
        return user


class FacebookUserFactory(factory.Factory):
    FACTORY_FOR = FacebookUser
    facebook_id = factory.Sequence(lambda n: 1000 + n)
    name = ''
    gender = 'M'
    pic_square = ''


class UserProfileFactory(factory.Factory):
    FACTORY_FOR = UserProfile
    facebook_user = factory.SubFactory(FacebookUserFactory)
    facebook_id = factory.Sequence(lambda n: 1000 + n)
    user = factory.SubFactory(UserFactory)


class FacebookFriendFactory(factory.Factory):
    FACTORY_FOR = FacebookFriend
    facebook_user = factory.SubFactory(FacebookUserFactory)
    owner = factory.SubFactory(UserFactory)
    top_friends_order = 0

