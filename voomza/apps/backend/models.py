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
    family_photo_1 = models.PositiveSmallIntegerField(null=True)
    family_photo_2 = models.PositiveSmallIntegerField(null=True)
    family_photo_3 = models.PositiveSmallIntegerField(null=True)
    family_photo_4 = models.PositiveSmallIntegerField(null=True)
    gfbf_photo_1 = models.PositiveSmallIntegerField(null=True)
    gfbf_photo_2 = models.PositiveSmallIntegerField(null=True)
    gfbf_photo_3 = models.PositiveSmallIntegerField(null=True)
    gfbf_photo_4 = models.PositiveSmallIntegerField(null=True)
    group_photo_1 = models.PositiveSmallIntegerField(null=True)
    group_photo_2 = models.PositiveSmallIntegerField(null=True)
    group_photo_3 = models.PositiveSmallIntegerField(null=True)
    group_photo_4 = models.PositiveSmallIntegerField(null=True)

    top_photo = models.PositiveSmallIntegerField(null=True)
    first_half_photo_1 = models.PositiveSmallIntegerField(null=True)
    first_half_photo_2 = models.PositiveSmallIntegerField(null=True)
    first_half_photo_3 = models.PositiveSmallIntegerField(null=True)
    second_half_photo_1 = models.PositiveSmallIntegerField(null=True)
    second_half_photo_2 = models.PositiveSmallIntegerField(null=True)
    second_half_photo_3 = models.PositiveSmallIntegerField(null=True)

    # Could correspond to more than one table
    back_in_time_photo_1 = models.PositiveSmallIntegerField(null=True)
    back_in_time_photo_2 = models.PositiveSmallIntegerField(null=True)
    back_in_time_photo_3 = models.PositiveSmallIntegerField(null=True)
    back_in_time_photo_4 = models.PositiveSmallIntegerField(null=True)
    back_in_time_photo_5 = models.PositiveSmallIntegerField(null=True)
    back_in_time_photo_6 = models.PositiveSmallIntegerField(null=True)
    back_in_time_photo_7 = models.PositiveSmallIntegerField(null=True)
    back_in_time_photo_8 = models.PositiveSmallIntegerField(null=True)

    top_album_1_index = models.BigIntegerField(null=True)
    top_album_1_photo_1 = models.PositiveSmallIntegerField(null=True)
    top_album_1_photo_2 = models.PositiveSmallIntegerField(null=True)
    top_album_1_photo_3 = models.PositiveSmallIntegerField(null=True)
    top_album_1_photo_4 = models.PositiveSmallIntegerField(null=True)
    top_album_2_index = models.BigIntegerField(null=True)
    top_album_2_photo_1 = models.PositiveSmallIntegerField(null=True)
    top_album_2_photo_2 = models.PositiveSmallIntegerField(null=True)
    top_album_2_photo_3 = models.PositiveSmallIntegerField(null=True)
    top_album_2_photo_4 = models.PositiveSmallIntegerField(null=True)
    top_album_3_index = models.BigIntegerField(null=True)
    top_album_3_photo_1 = models.PositiveSmallIntegerField(null=True)
    top_album_3_photo_2 = models.PositiveSmallIntegerField(null=True)
    top_album_3_photo_3 = models.PositiveSmallIntegerField(null=True)
    top_album_3_photo_4 = models.PositiveSmallIntegerField(null=True)

    top_friend_1 = models.PositiveSmallIntegerField(null=True)
    top_friend_1_photo_1 = models.PositiveSmallIntegerField(null=True)
    top_friend_1_photo_2 = models.PositiveSmallIntegerField(null=True)
    top_friend_1_photo_3 = models.PositiveSmallIntegerField(null=True)
    top_friend_2 = models.PositiveSmallIntegerField(null=True)
    top_friend_2_photo_1 = models.PositiveSmallIntegerField(null=True)
    top_friend_2_photo_2 = models.PositiveSmallIntegerField(null=True)
    top_friend_2_photo_3 = models.PositiveSmallIntegerField(null=True)
    top_friend_3 = models.PositiveSmallIntegerField(null=True)
    top_friend_3_photo_1 = models.PositiveSmallIntegerField(null=True)
    top_friend_3_photo_2 = models.PositiveSmallIntegerField(null=True)
    top_friend_3_photo_3 = models.PositiveSmallIntegerField(null=True)
    top_friend_4 = models.PositiveSmallIntegerField(null=True)
    top_friend_4_photo_1 = models.PositiveSmallIntegerField(null=True)
    top_friend_4_photo_2 = models.PositiveSmallIntegerField(null=True)
    top_friend_4_photo_3 = models.PositiveSmallIntegerField(null=True)
    top_friend_5 = models.PositiveSmallIntegerField(null=True)
    top_friend_5_photo_1 = models.PositiveSmallIntegerField(null=True)
    top_friend_5_photo_2 = models.PositiveSmallIntegerField(null=True)
    top_friend_5_photo_3 = models.PositiveSmallIntegerField(null=True)


    # Really, should use this data structure to autogenerate the model
    lists_to_fields = {
        'family_with': [
            'family_photo_1', 'family_photo_2', 'family_photo_3', 'family_photo_4'
        ],
        'gfbf_with': ['gfbf_photo_1', 'gfbf_photo_2', 'gfbf_photo_3', 'gfbf_photo_4',],
        'group_shots': ['group_photo_1', 'group_photo_2', 'group_photo_3', 'group_photo_4'],
        'top_photos': ['top_photo'],
        'top_photos_first_half': ['first_half_photo_1', 'first_half_photo_2', 'first_half_photo_3'],
        'top_photos_second_half': ['second_half_photo_1', 'second_half_photo_2', 'second_half_photo_3'],
        'you_back_in_time_year_1': ['back_in_time_photo_1'],
        'you_back_in_time_year_2': ['back_in_time_photo_2'],
        'you_back_in_time_year_3': ['back_in_time_photo_3'],
        'you_back_in_time_year_4': ['back_in_time_photo_4'],
        'you_back_in_time_year_5': ['back_in_time_photo_5'],
        'you_back_in_time_year_6': ['back_in_time_photo_6'],
        'you_back_in_time_year_7': ['back_in_time_photo_7'],
        'top_albums': [
            'top_album_1_index.top_album_1_photo_1', 'top_album_1_index.top_album_1_photo_2',
            'top_album_1_index.top_album_1_photo_3', 'top_album_1_index.top_album_1_photo_4',
            'top_album_2_index.top_album_2_photo_1', 'top_album_2_index.top_album_2_photo_2',
            'top_album_2_index.top_album_2_photo_3', 'top_album_2_index.top_album_2_photo_4',
            'top_album_3_index.top_album_3_photo_1', 'top_album_3_index.top_album_3_photo_2',
            'top_album_3_index.top_album_3_photo_3', 'top_album_3_index.top_album_3_photo_4',
            'top_album_4_index.top_album_4_photo_1', 'top_album_4_index.top_album_4_photo_2',
            'top_album_4_index.top_album_4_photo_3', 'top_album_4_index.top_album_4_photo_4',
        ],
        'top_friends': [
            'top_friend_1.top_friend_1_photo_1', 'top_friend_1.top_friend_1_photo_2',
            'top_friend_1.top_friend_1_photo_3',
            'top_friend_2.top_friend_2_photo_1', 'top_friend_2.top_friend_2_photo_2',
            'top_friend_2.top_friend_2_photo_3',
            'top_friend_3.top_friend_3_photo_1', 'top_friend_3.top_friend_3_photo_2',
            'top_friend_3.top_friend_3_photo_3',
            # They may or may not have these - doesn't matter, they'll just be empty
            'top_friend_4.top_friend_4_photo_1', 'top_friend_4.top_friend_4_photo_2',
            'top_friend_4.top_friend_4_photo_3',
            'top_friend_5.top_friend_5_photo_1', 'top_friend_5.top_friend_5_photo_2',
            'top_friend_5.top_friend_5_photo_3',
        ]
    }

    def get_n_unused_photos(self, list_of_photos, n):
        unused_photos = []
        while len(unused_photos) < n:
            unused_photo = self.get_first_unused_photo(list_of_photos)
            if not unused_photo:
                # List ran out, return what we had
                return unused_photos
            else:
                unused_photos.append(unused_photo)
        return unused_photos


    def get_first_unused_photo(self, list_of_photos):
        """
        Loops through photos in `list_of_photos`,
        running `yearbook.photo_is_used()` until it returns False
        If no photo unused, return None
        """
        for photo in list_of_photos:
            if not self.photo_is_used(photo):
                return photo
        return None


    def photo_is_used(self, photo):
        """
        Iterates through all image index fields on the model,
        verifying that the images they refer to are not "claimed"
        """
        photo_id = photo['id']
        ranking = PhotoRankings.objects.get(user=self.owner)
        # Iterate through the above fields
        for ranked_list_name, yb_fields in self.lists_to_fields.items():
            ranked_list = getattr(ranking, ranked_list_name)
            if ranked_list:
                for yb_field in yb_fields:
                    if '.' in yb_field:
                        # Double-indirection
                        photo_list_index_field, photo_index_field = yb_field.split('.')
                        photo_list_index = getattr(self, photo_list_index_field)
                        photo_index = getattr(self, photo_index_field)
                        if (not photo_list_index is None) and (not photo_index is None):
                            if ranked_list[photo_list_index][photo_index]['id'] == photo_id:
                                return True
                    else:
                        # Dereference the field back to the original facebook id
                        list_index = getattr(self, yb_field)
                        if not list_index is None:
                            # If the index is not None and the list is not empty
                            if ranked_list[list_index]['id'] == photo_id:
                                return True

        return False


class Minibook(models.Model):
    owner = models.ForeignKey('auth.User', related_name='minibooks_from')
    target = models.ForeignKey('account.FacebookUser', related_name='minibooks_to')
    # Could correspond to more than one table
    photo_1 = models.PositiveSmallIntegerField(null=True)
    photo_2 = models.PositiveSmallIntegerField(null=True)
    photo_3 = models.PositiveSmallIntegerField(null=True)
    photo_4 = models.PositiveSmallIntegerField(null=True)


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
