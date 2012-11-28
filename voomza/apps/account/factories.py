import factory
from django.contrib.auth.models import User
from voomza.apps.account.models import UserProfile, YearbookFacebookUser

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


class UserProfileFactory(factory.Factory):
    FACTORY_FOR = UserProfile

    facebook_id = factory.Sequence(lambda n: 1000 + n)
    user = factory.SubFactory(UserFactory)



class YearbookFacebookUserFactory(factory.Factory):
    FACTORY_FOR = YearbookFacebookUser

    user = factory.SubFactory(UserFactory)
    facebook_id = factory.Sequence(lambda n: 2000 + n)
    name = ''
    gender = 'M'
    top_friends_order = 0
    pic_square = ''

