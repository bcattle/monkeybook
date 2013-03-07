from __future__ import division, print_function, unicode_literals
from decimal import Decimal

PRICE_FOR_DIGITAL   = Decimal('4.99')
PRICE_FOR_ABRIDGED  = Decimal('39.99')
PRICE_FOR_FULL      = Decimal('79.99')
PRICE_FOR_SHIPPING  = Decimal('8.99')
CA_SALES_TAX        = Decimal('.0875')      # San Francisco
CA_STATE_ABBR       = 'CA'


QUANTITY_CHOICES = [
    ('', 0), ('1', 1), ('2', 2), ('3', 3), ('4', 4), ('5', 5),
]

DIGITAL_QUANTITY_CHOICES = [
    ('', 0), ('1', 1),
]
