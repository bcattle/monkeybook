import factory
from models import Badge
from voomza.apps.account.factories import FacebookUserFactory
from voomza.apps.yearbook.models import YearbookSign

BADGE_NAMES = (
    'The family I love',
    'That special somebody',
    'Best friends for life',
#    'Most likely to make me laugh',
#    'Last one at the party!',
#    'Hottest friends',
#    'Most likely to own an island',
)

MESSAGES = (
    'Choose up to 5 family members',
    'Do you have a significant other? Choose them',
    'Choose up to 5 friends you can\'t live without',
)

MAX_TAGS = (5, 1, 5)

NUM_BADGES = len(BADGE_NAMES)

class BadgeFactory(factory.Factory):
    FACTORY_FOR = Badge

    name = factory.Sequence(lambda n: BADGE_NAMES[int(n) % NUM_BADGES])
    max_tags = factory.Sequence(lambda n: MAX_TAGS[int(n) % NUM_BADGES])
    message = factory.Sequence(lambda n: MESSAGES[int(n) % NUM_BADGES])
    icon = 'img/star-64.png'
    icon_small = 'img/star-32.png'



class YearbookSignFactory(factory.Factory):
    FACTORY_FOR = YearbookSign

    text = 'Had a great year man, see you in the fall!'
    from_facebook_user = factory.SubFactory(FacebookUserFactory)
    to_facebook_user = factory.SubFactory(FacebookUserFactory)
