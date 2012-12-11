import logging
from django.db import models
from django.db.models.signals import post_syncdb
from django.dispatch.dispatcher import receiver
from jsonfield.fields import JSONField
from south.signals import post_migrate
from voomza.apps.backend.managers import FacebookPhotoManager

logger = logging.getLogger(__name__)


class FacebookPhoto(models.Model):
    facebook_id = models.BigIntegerField(primary_key=True)
    created = models.DateTimeField(null=True)
    height = models.PositiveIntegerField(default=0)
    width = models.PositiveIntegerField(default=0)
    fb_url = models.CharField(max_length=200)
    local_url = models.CharField(max_length=200, default='')

    def url(self):
        return self.local_url or self.fb_url

    objects = FacebookPhotoManager()


class PhotoRankings(models.Model):
    """
    The photo rankings for a user,
    holds a ranking of all photos for relevance in each category
    """
    user = models.OneToOneField('auth.User', related_name='photo_rankings')
    # Lists of photos for each category
    family_with = JSONField(default=[], max_length=100000)
#    family_alone = JSONField(default=[], max_length=100000)
    gfbf_with = JSONField(default=[], max_length=100000)
#    gfbf_alone = JSONField(default=[], max_length=100000)
    group_shots = JSONField(default=[], max_length=100000)
    top_photos = JSONField(default=[], max_length=100000)
    top_photos_first_half = JSONField(default=[], max_length=100000)
    top_photos_second_half = JSONField(default=[], max_length=100000)
    # This is TBD, will want to see some combination of user and group,
    # some (most?) of these lists may be empty
    you_back_in_time_year_1 = JSONField(default=[], max_length=100000)
    you_back_in_time_year_2 = JSONField(default=[], max_length=100000)
    you_back_in_time_year_3 = JSONField(default=[], max_length=100000)
    you_back_in_time_year_4 = JSONField(default=[], max_length=100000)
    you_back_in_time_year_5 = JSONField(default=[], max_length=100000)
    you_back_in_time_year_6 = JSONField(default=[], max_length=100000)
    you_back_in_time_year_7 = JSONField(default=[], max_length=100000)
#    group_back_in_time_year_1 = JSONField(default=[], max_length=100000)
#    group_back_in_time_year_2 = JSONField(default=[], max_length=100000)
#    group_back_in_time_year_3 = JSONField(default=[], max_length=100000)
#    group_back_in_time_year_4 = JSONField(default=[], max_length=100000)
#    group_back_in_time_year_5 = JSONField(default=[], max_length=100000)
#    group_back_in_time_year_6 = JSONField(default=[], max_length=100000)
#    group_back_in_time_year_7 = JSONField(default=[], max_length=100000)
    # Albums
    top_albums = JSONField(default=[], max_length=100000)
    # Show up to 5 friends (if no family or gfbf)
    top_friends = JSONField(default=[], max_length=100000)
#    top_friend_2 = JSONField(default=[], max_length=100000)
#    top_friend_3 = JSONField(default=[], max_length=100000)
#    top_friend_4 = JSONField(default=[], max_length=100000)
#    top_friend_5 = JSONField(default=[], max_length=100000)
    # Posts
    top_post = JSONField(default=[], max_length=100000)
    birthday_posts = JSONField(default=[], max_length=100000)



class Yearbook(models.Model):
    owner = models.OneToOneField('auth.User', related_name='yearbooks')
    # These indices point to the lists stored in PhotoRanking
    family_photo_1 = models.PositiveSmallIntegerField(default=0)
    family_photo_2 = models.PositiveSmallIntegerField(default=0)
    family_photo_3 = models.PositiveSmallIntegerField(default=0)
    family_photo_4 = models.PositiveSmallIntegerField(default=0)
    gfbf_photo_1 = models.PositiveSmallIntegerField(default=0)
    gfbf_photo_2 = models.PositiveSmallIntegerField(default=0)
    gfbf_photo_3 = models.PositiveSmallIntegerField(default=0)
    gfbf_photo_4 = models.PositiveSmallIntegerField(default=0)
    group_photo_1 = models.PositiveSmallIntegerField(default=0)
    group_photo_2 = models.PositiveSmallIntegerField(default=0)
    group_photo_3 = models.PositiveSmallIntegerField(default=0)
    group_photo_4 = models.PositiveSmallIntegerField(default=0)

    top_photo = models.PositiveSmallIntegerField(default=0)
    first_half_photo_1 = models.PositiveSmallIntegerField(default=0)
    first_half_photo_2 = models.PositiveSmallIntegerField(default=0)
    first_half_photo_3 = models.PositiveSmallIntegerField(default=0)
    second_half_photo_1 = models.PositiveSmallIntegerField(default=0)
    second_half_photo_2 = models.PositiveSmallIntegerField(default=0)
    second_half_photo_3 = models.PositiveSmallIntegerField(default=0)

    # Could correspond to more than one table
    back_in_time_photo_1 = models.PositiveSmallIntegerField(default=0)
    back_in_time_photo_2 = models.PositiveSmallIntegerField(default=0)
    back_in_time_photo_3 = models.PositiveSmallIntegerField(default=0)
    back_in_time_photo_4 = models.PositiveSmallIntegerField(default=0)
    back_in_time_photo_5 = models.PositiveSmallIntegerField(default=0)
    back_in_time_photo_6 = models.PositiveSmallIntegerField(default=0)
    back_in_time_photo_7 = models.PositiveSmallIntegerField(default=0)
    back_in_time_photo_8 = models.PositiveSmallIntegerField(default=0)

    top_album_1_id = models.BigIntegerField(default=0)
    top_album_1_photo_1 = models.PositiveSmallIntegerField(default=0)
    top_album_1_photo_2 = models.PositiveSmallIntegerField(default=0)
    top_album_1_photo_3 = models.PositiveSmallIntegerField(default=0)
    top_album_1_photo_4 = models.PositiveSmallIntegerField(default=0)
    top_album_2_id = models.BigIntegerField(default=0)
    top_album_2_photo_1 = models.PositiveSmallIntegerField(default=0)
    top_album_2_photo_2 = models.PositiveSmallIntegerField(default=0)
    top_album_2_photo_3 = models.PositiveSmallIntegerField(default=0)
    top_album_2_photo_4 = models.PositiveSmallIntegerField(default=0)
    top_album_3_id = models.BigIntegerField(default=0)
    top_album_3_photo_1 = models.PositiveSmallIntegerField(default=0)
    top_album_3_photo_2 = models.PositiveSmallIntegerField(default=0)
    top_album_3_photo_3 = models.PositiveSmallIntegerField(default=0)
    top_album_3_photo_4 = models.PositiveSmallIntegerField(default=0)

    top_friend_1 = models.PositiveSmallIntegerField(default=0)
    top_friend_1_photo_1 = models.PositiveSmallIntegerField(default=0)
    top_friend_1_photo_2 = models.PositiveSmallIntegerField(default=0)
    top_friend_1_photo_3 = models.PositiveSmallIntegerField(default=0)
    top_friend_2 = models.PositiveSmallIntegerField(default=0)
    top_friend_2 = models.PositiveSmallIntegerField(default=0)
    top_friend_2_photo_2 = models.PositiveSmallIntegerField(default=0)
    top_friend_2_photo_3 = models.PositiveSmallIntegerField(default=0)
    top_friend_3 = models.PositiveSmallIntegerField(default=0)
    top_friend_3_photo_1 = models.PositiveSmallIntegerField(default=0)
    top_friend_3_photo_2 = models.PositiveSmallIntegerField(default=0)
    top_friend_3_photo_3 = models.PositiveSmallIntegerField(default=0)
    top_friend_4 = models.PositiveSmallIntegerField(default=0)
    top_friend_4_photo_1 = models.PositiveSmallIntegerField(default=0)
    top_friend_4_photo_2 = models.PositiveSmallIntegerField(default=0)
    top_friend_4_photo_3 = models.PositiveSmallIntegerField(default=0)
    top_friend_5 = models.PositiveSmallIntegerField(default=0)
    top_friend_5_photo_1 = models.PositiveSmallIntegerField(default=0)
    top_friend_5_photo_2 = models.PositiveSmallIntegerField(default=0)
    top_friend_5_photo_3 = models.PositiveSmallIntegerField(default=0)



class Minibook(models.Model):
    owner = models.ForeignKey('auth.User', related_name='minibooks_from')
    target = models.ForeignKey('account.FacebookUser', related_name='minibooks_to')
    # Could correspond to more than one table
    photo_1 = models.PositiveSmallIntegerField(default=0)
    photo_2 = models.PositiveSmallIntegerField(default=0)
    photo_3 = models.PositiveSmallIntegerField(default=0)
    photo_4 = models.PositiveSmallIntegerField(default=0)


class MinibookRankings(models.Model):
    minibook = models.OneToOneField(Minibook, related_name='photo_rankings')
    with_target = JSONField(default=[], max_length=100000)
    # These could be photos of just you, you with your friends, or group shots
    your_photos = JSONField(default=[], max_length=100000)
    # Should both of these be in the same table?




@receiver(post_syncdb, dispatch_uid='backend.models')
@receiver(post_migrate, dispatch_uid='backend.models')
def set_table_row_format(**kwargs):
    from django.conf import settings
    if settings.DATABASES['default']['ENGINE'] == 'django.db.backends.mysql':
        # Set ROW_FORMAT=DYNAMIC to allow longer rows
        from django.db import connection, transaction
        cursor = connection.cursor()
        cursor.execute('ALTER TABLE `%s` ROW_FORMAT=DYNAMIC' % PhotoRankings._meta.db_table)
        transaction.commit_unless_managed()
