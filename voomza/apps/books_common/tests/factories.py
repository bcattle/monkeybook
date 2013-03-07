import factory
from voomza.apps.books_common.models import YearbookSign
from voomza.apps.account.tests.factories import FacebookUserFactory


class YearbookSignFactory(factory.Factory):
    FACTORY_FOR = YearbookSign

    text = 'Had a great year man, see you in the fall!'
    from_facebook_user = factory.SubFactory(FacebookUserFactory)
    to_facebook_user = factory.SubFactory(FacebookUserFactory)
