import random
from django.test import TestCase


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

