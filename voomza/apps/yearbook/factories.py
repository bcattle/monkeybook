import factory
from models import Badge

BADGE_NAMES = [
    'Most likely to be president',
    'Most Likely to be famous',
    'Most likely to become a millionaire',
    'Most likely to win a Nobel Prize',
    'Most likely to win an Oscar',
    'Most likely to take over the world',
    'Most likely to marry for money',
    'Most likely to win the lottery but lose the ticket',
    'Best smile',
    'Best looking girl',
    'Best looking guy',
    'Best dancer',
    'Best singer',
    'Worst driver',
    'Most sarcastic',
    'Most creative',
    'Most hardworking',
    'Most competitive',
    'Biggest flirt',
    'Biggest party animal',
    ]
NUM_BADGES = len(BADGE_NAMES)

class BadgeFactory(factory.Factory):
    FACTORY_FOR = Badge

    name = factory.Sequence(lambda n: BADGE_NAMES[int(n) % 20])
    icon = 'img/star-64.png'
    icon_small = 'img/star-32.png'
