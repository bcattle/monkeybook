import factory
from models import Badge
from voomza.apps.account.factories import UserFactory
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

#BADGE_NAMES = [
#    'Most likely to be president',
#    'Most Likely to be famous',
#    'Most likely to become a millionaire',
#    'Most likely to win a Nobel Prize',
#    'Most likely to win an Oscar',
#    'Most likely to take over the world',
#    'Most likely to marry for money',
#    'Most likely to win the lottery but lose the ticket',
#    'Best smile',
#    'Best looking girl',
#    'Best looking guy',
#    'Best dancer',
#    'Best singer',
#    'Worst driver',
#    'Most sarcastic',
#    'Most creative',
#    'Most hardworking',
#    'Most competitive',
#    'Biggest flirt',
#    'Biggest party animal',
#    ]
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

    from_user = factory.SubFactory(UserFactory)
    to_id = 3000123
    text = 'Had a great year man, see you in the fall!'

