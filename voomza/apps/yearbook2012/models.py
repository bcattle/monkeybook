from __future__ import division, print_function, unicode_literals
import logging, hashlib, time
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models.signals import post_syncdb
from django.dispatch.dispatcher import receiver
from django.conf import settings
from django.utils.encoding import python_2_unicode_compatible
from south.signals import post_migrate
from jsonfield import JSONField
from voomza.apps.books_common.models import BaseBookModel
from voomza.apps.books_common.utils import set_table_row_format

logger = logging.getLogger(__name__)


@python_2_unicode_compatible
class PhotoRankings(models.Model):
    """
    The photo rankings for a user,
    holds a ranking of all photos for relevance in each category
    """
    #    user = models.OneToOneField('auth.User', related_name='photo_rankings')
    user = models.ForeignKey('auth.User', related_name='photo_rankings')
    # Lists of photos for each category
    top_photos = JSONField(default="[]", max_length=100000)
    group_shots = JSONField(default="[]", max_length=100000)
    top_albums_photos = JSONField(default="[]", max_length=100000)
    top_albums_ranked = JSONField(default="[]", max_length=100000)
    back_in_time = JSONField(default="[]", max_length=100000)
    top_friends_ids = JSONField(default="[]", max_length=100000)
    top_friends_photos = JSONField(default="[]", max_length=100000)
    top_posts = JSONField(default="[]", max_length=100000)

    def __str__(self):
        return 'PhotoRankings %s' % self.user.username

    class Meta:
        verbose_name_plural = 'Photo rankings'


class Yearbook(BaseBookModel):
#    rankings = models.OneToOneField(PhotoRankings, related_name='yearbook')
    rankings = models.ForeignKey(PhotoRankings, related_name='yearbook')

    def get_absolute_url(self):
        return reverse('yearbook', kwargs={'hash': self.hash})

    def save(self, *args, **kwargs):
        if not self.hash:
            # Generate a unique hash to use as the "shareable" url
            while True:
                hash = hashlib.md5(str(time.time())).hexdigest()[:settings.BOOK_HASH_LENGTH]
                try:
                    existing = Yearbook.objects.get(hash=hash)
                except self.DoesNotExist:
                    break
            self.hash = hash
        super(BaseBookModel, self).save(*args, **kwargs)

    # These indices point to the lists stored in PhotoRanking
    top_photo_1 = models.PositiveSmallIntegerField(null=True)
    top_photo_2 = models.PositiveSmallIntegerField(null=True)
    top_photo_3 = models.PositiveSmallIntegerField(null=True)
    top_photo_4 = models.PositiveSmallIntegerField(null=True)
    top_photo_5 = models.PositiveSmallIntegerField(null=True)

    group_photo_1 = models.PositiveSmallIntegerField(null=True)
    group_photo_2 = models.PositiveSmallIntegerField(null=True)
    group_photo_3 = models.PositiveSmallIntegerField(null=True)

    year_photo_1 = models.PositiveSmallIntegerField(null=True)
    year_photo_2 = models.PositiveSmallIntegerField(null=True)
    year_photo_3 = models.PositiveSmallIntegerField(null=True)
    year_photo_4 = models.PositiveSmallIntegerField(null=True)
    year_photo_5 = models.PositiveSmallIntegerField(null=True)
    # If 2, 3, 4 or 5 were portrait, respectively
    year_photo_6 = models.PositiveSmallIntegerField(null=True)
    year_photo_7 = models.PositiveSmallIntegerField(null=True)
    year_photo_8 = models.PositiveSmallIntegerField(null=True)
    year_photo_9 = models.PositiveSmallIntegerField(null=True)

    top_friend_1 = models.PositiveSmallIntegerField(null=True)
    top_friend_1_stat = models.CharField(max_length=100, blank=True)
    top_friend_1_photo_1 = models.PositiveSmallIntegerField(null=True)
    top_friend_1_photo_2 = models.PositiveSmallIntegerField(null=True)

    top_friend_2 = models.PositiveSmallIntegerField(null=True)
    top_friend_2_stat = models.CharField(max_length=100, blank=True)
    top_friend_2_photo_1 = models.PositiveSmallIntegerField(null=True)
    top_friend_2_photo_2 = models.PositiveSmallIntegerField(null=True)

    top_friend_3 = models.PositiveSmallIntegerField(null=True)
    top_friend_3_stat = models.CharField(max_length=100, blank=True)
    top_friend_3_photo_1 = models.PositiveSmallIntegerField(null=True)
    top_friend_3_photo_2 = models.PositiveSmallIntegerField(null=True)

    top_friend_4 = models.PositiveSmallIntegerField(null=True)
    top_friend_4_stat = models.CharField(max_length=100, blank=True)
    top_friend_4_photo_1 = models.PositiveSmallIntegerField(null=True)
    top_friend_4_photo_2 = models.PositiveSmallIntegerField(null=True)

    top_friend_5 = models.PositiveSmallIntegerField(null=True)
    top_friend_5_stat = models.CharField(max_length=100, blank=True)
    top_friend_5_photo_1 = models.PositiveSmallIntegerField(null=True)
    top_friend_5_photo_2 = models.PositiveSmallIntegerField(null=True)

    top_album_1 = models.BigIntegerField(null=True)
    top_album_1_photo_1 = models.PositiveSmallIntegerField(null=True)
    top_album_1_photo_2 = models.PositiveSmallIntegerField(null=True)
    top_album_1_photo_3 = models.PositiveSmallIntegerField(null=True)
    top_album_1_photo_4 = models.PositiveSmallIntegerField(null=True)

    top_album_2 = models.BigIntegerField(null=True)
    top_album_2_photo_1 = models.PositiveSmallIntegerField(null=True)
    top_album_2_photo_2 = models.PositiveSmallIntegerField(null=True)
    top_album_2_photo_3 = models.PositiveSmallIntegerField(null=True)
    top_album_2_photo_4 = models.PositiveSmallIntegerField(null=True)

    top_album_3 = models.BigIntegerField(null=True)
    top_album_3_photo_1 = models.PositiveSmallIntegerField(null=True)
    top_album_3_photo_2 = models.PositiveSmallIntegerField(null=True)
    top_album_3_photo_3 = models.PositiveSmallIntegerField(null=True)
    top_album_3_photo_4 = models.PositiveSmallIntegerField(null=True)

    # The first field is an index to the year, the second an index to the photo
    back_in_time_1          = models.PositiveSmallIntegerField(null=True)
    back_in_time_1_photo_1  = models.PositiveSmallIntegerField(null=True)
    back_in_time_2          = models.PositiveSmallIntegerField(null=True)
    back_in_time_2_photo_1  = models.PositiveSmallIntegerField(null=True)
    back_in_time_3          = models.PositiveSmallIntegerField(null=True)
    back_in_time_3_photo_1  = models.PositiveSmallIntegerField(null=True)
    back_in_time_4          = models.PositiveSmallIntegerField(null=True)
    back_in_time_4_photo_1  = models.PositiveSmallIntegerField(null=True)
    back_in_time_5          = models.PositiveSmallIntegerField(null=True)
    back_in_time_5_photo_1  = models.PositiveSmallIntegerField(null=True)
    back_in_time_6          = models.PositiveSmallIntegerField(null=True)
    back_in_time_6_photo_1  = models.PositiveSmallIntegerField(null=True)
    back_in_time_7          = models.PositiveSmallIntegerField(null=True)
    back_in_time_7_photo_1  = models.PositiveSmallIntegerField(null=True)

    # Posts
    top_post = models.PositiveSmallIntegerField(null=True)
    birthday_posts = JSONField(default="[]", max_length=100000)

    # Really, should use this data structure to autogenerate the model
    lists_to_fields = {
        'top_photos': [
            'top_photo_1', 'top_photo_2', 'top_photo_3', 'top_photo_4', 'top_photo_5',
            'year_photo_1', 'year_photo_2', 'year_photo_3', 'year_photo_4', 'year_photo_5',
            'year_photo_6', 'year_photo_7', 'year_photo_8', 'year_photo_9',
            ],
        'group_shots': ['group_photo_1', 'group_photo_2', 'group_photo_3',],
        'top_friends_photos': [
            'top_friend_1.top_friend_1_photo_1', 'top_friend_1.top_friend_1_photo_2',
            'top_friend_2.top_friend_2_photo_1', 'top_friend_2.top_friend_2_photo_2',
            'top_friend_3.top_friend_3_photo_1', 'top_friend_3.top_friend_3_photo_2',
            'top_friend_4.top_friend_4_photo_1', 'top_friend_4.top_friend_4_photo_2',
            'top_friend_5.top_friend_5_photo_1', 'top_friend_5.top_friend_5_photo_2'
        ],
        'top_albums_photos': [
            'top_album_1.top_album_1_photo_1', 'top_album_1.top_album_1_photo_2',
            'top_album_1.top_album_1_photo_3', 'top_album_1.top_album_1_photo_4',

            'top_album_2.top_album_2_photo_1', 'top_album_2.top_album_2_photo_2',
            'top_album_2.top_album_2_photo_3', 'top_album_2.top_album_2_photo_4',

            'top_album_3.top_album_3_photo_1', 'top_album_3.top_album_3_photo_2',
            'top_album_3.top_album_3_photo_3', 'top_album_3.top_album_3_photo_4',
            ],
        'back_in_time': [
            'back_in_time_1.back_in_time_1_photo_1',
            'back_in_time_2.back_in_time_2_photo_1',
            'back_in_time_3.back_in_time_3_photo_1',
            'back_in_time_4.back_in_time_4_photo_1',
            'back_in_time_5.back_in_time_5_photo_1',
            'back_in_time_6.back_in_time_6_photo_1',
            'back_in_time_7.back_in_time_7_photo_1',
            ]
    }


@receiver((post_syncdb, post_migrate,), dispatch_uid='yearbook2012.models')
def set_ranking_table_row_format(app, **kwargs):
    # post_syncdb, `app` is a Module. post_migrate `app` is a string
    if app == 'yearbook2012':
        set_table_row_format(PhotoRankings)
