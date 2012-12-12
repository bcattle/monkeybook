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
    comments = JSONField(default=0, max_length=100000)

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
    top_photos = JSONField(default=0, max_length=100000)
    top_photos_first_half = JSONField(default=0, max_length=100000)
    top_photos_second_half = JSONField(default=0, max_length=100000)
    group_shots = JSONField(default=0, max_length=100000)
    # Top few will be gf/bf or family, if any
    top_friends = JSONField(default=0, max_length=100000)
    top_albums = JSONField(default=0, max_length=100000)
    back_in_time = JSONField(default=0, max_length=100000)


class Yearbook(models.Model):
    owner = models.OneToOneField('auth.User', related_name='yearbooks')
    # These indices point to the lists stored in PhotoRanking
    top_photo_1 = models.PositiveSmallIntegerField(null=True)
    top_photo_2 = models.PositiveSmallIntegerField(null=True)
    top_photo_3 = models.PositiveSmallIntegerField(null=True)

    first_half_photo_1 = models.PositiveSmallIntegerField(null=True)
    first_half_photo_2 = models.PositiveSmallIntegerField(null=True)
    first_half_photo_3 = models.PositiveSmallIntegerField(null=True)
    second_half_photo_1 = models.PositiveSmallIntegerField(null=True)
    second_half_photo_2 = models.PositiveSmallIntegerField(null=True)
    second_half_photo_3 = models.PositiveSmallIntegerField(null=True)

    group_photo_1 = models.PositiveSmallIntegerField(null=True)
    group_photo_2 = models.PositiveSmallIntegerField(null=True)
    group_photo_3 = models.PositiveSmallIntegerField(null=True)

    top_friend_1 = models.PositiveSmallIntegerField(null=True)
    top_friend_1_stat = models.CharField(max_length=100, blank=True)
    top_friend_1_photo_1 = models.PositiveSmallIntegerField(null=True)

    top_friend_2 = models.PositiveSmallIntegerField(null=True)
    top_friend_2_stat = models.CharField(max_length=100, blank=True)
    top_friend_2_photo_1 = models.PositiveSmallIntegerField(null=True)

    top_friend_3 = models.PositiveSmallIntegerField(null=True)
    top_friend_3_stat = models.CharField(max_length=100, blank=True)
    top_friend_3_photo_1 = models.PositiveSmallIntegerField(null=True)

    top_friend_4 = models.PositiveSmallIntegerField(null=True)
    top_friend_4_stat = models.CharField(max_length=100, blank=True)
    top_friend_4_photo_1 = models.PositiveSmallIntegerField(null=True)

    top_friend_5 = models.PositiveSmallIntegerField(null=True)
    top_friend_5_stat = models.CharField(max_length=100, blank=True)
    top_friend_5_photo_1 = models.PositiveSmallIntegerField(null=True)

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
    top_post = JSONField(default=0, max_length=100000)
    birthday_posts = JSONField(default=0, max_length=100000)


    # Really, should use this data structure to autogenerate the model
    lists_to_fields = {
        'top_photos': ['top_photo_1', 'top_photo_2', 'top_photo_3'],
        'top_photos_first_half': [
            'first_half_photo_1', 'first_half_photo_2', 'first_half_photo_3'
        ],
        'top_photos_second_half': [
            'second_half_photo_1', 'second_half_photo_2', 'second_half_photo_3'
        ],
        'group_shots': ['group_photo_1', 'group_photo_2', 'group_photo_3'],
        'top_friends': [
            'top_friend_1.top_friend_1_photo_1', 'top_friend_2.top_friend_2_photo_1',
            'top_friend_3.top_friend_3_photo_1', 'top_friend_4.top_friend_4_photo_1',
            'top_friend_5.top_friend_5_photo_1',
        ],
        'top_albums': [
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

    def get_n_unused_photos(self, list_of_photos, n):
        unused_photos = []
        used_ids = []
        while len(unused_photos) < n:
            # Need the counter here since the photos we pick up aren't in the Yearbook yet
            unused_photo = self.get_first_unused_photo(list_of_photos, used_ids)
            if unused_photo is None:
                # List ran out, return what we had
                return unused_photos
            else:
                unused_photos.append(unused_photo)
                used_ids.append(_get_id_from_dict_or_int(list_of_photos[unused_photo]))
        return unused_photos


    def get_first_unused_photo(self, list_of_photos, used_ids=None):
        """
        Loops through photos in `list_of_photos`,
        running `yearbook.photo_is_used()` until it returns False
        If no photo unused, return None
        """
        for index, photo in enumerate(list_of_photos):
            if not self.photo_is_used(photo, used_ids):
                return index
        return None


    def get_first_unused_photo_landscape(self, list_of_photos, used_ids=None):
        """
        Loops through photos in `list_of_photos`,
        running `yearbook.photo_is_used()` until it returns False
        *and* photo width is greater than its height.
        If no photo unused, return None
        """
        for index, photo in enumerate(list_of_photos):
            if not self.photo_is_used(photo, used_ids) and photo:
                # Is the photo landscape?
                if hasattr(photo, 'keys'):
                    if photo['width'] < photo['height']:
                        continue
                else:
                    # Bummer, just an id - look it up in the database
                    try:
                        photo_db = FacebookPhoto.objects.get(id=photo)
                        if photo_db.width < photo.height:
                            continue
                    except FacebookPhoto.DoesNotExist:
                        logger.warn('Attempted to look up fb photo %d, doesn\'t exist in db.' % photo)
                return index
        return None


    def photo_is_used(self, photo, used_ids=None):
        """
        Iterates through all image index fields on the model,
        verifying that the images they refer to are not "claimed"
        """
        if not used_ids:
            used_ids = []
        # `photo` could either be a struct or an integer id
        photo_id = _get_id_from_dict_or_int(photo)
        if photo_id in used_ids:
            return True
        ranking = PhotoRankings.objects.get(user=self.owner)
        # Iterate through the above fields
        for ranked_list_name, yb_fields in self.lists_to_fields.items():
            for yb_field in yb_fields:
#                if self.get_photo_from_field_string(ranking, ranked_list_name, yb_field, id_field) == photo_id:
                if self.get_photo_from_field_string(ranking, ranked_list_name, yb_field) == photo_id:
#                    print 'photo is used: %d' % photo_id
                    return True
        return False


    def get_photo_from_field_string(self, ranking, ranked_list_name, yb_field):
        """
        De-references and returns the id of the photo referred
        to by a field in the PhotoRankings and a field in the Yearbook.
        Examples:       'family_with', 'family_photo_1'
                        'top_friends', 'top_friend_1.top_friend_1_photo_1'
        Returns None if photo list or index is empty
        """
        ranked_list = getattr(ranking, ranked_list_name)
        if ranked_list:
            if '.' in yb_field:
                # Double-indirection
                photo_list_index_field, photo_index_field = yb_field.split('.')
                photo_list_index = getattr(self, photo_list_index_field)
                photo_index = getattr(self, photo_index_field)
                if (not photo_list_index is None) and (not photo_index is None):
                    photo_list = ranked_list[photo_list_index]
                    # `photo_list` could be a list of structs, or integers
                    return  _get_id_from_dict_or_int(photo_list[photo_index])
            else:
                # Dereference the field back to the original facebook id
                list_index = getattr(self, yb_field)
                if not list_index is None:
                    # `ranked_list` is either a list of structs, or integers
                    return _get_id_from_dict_or_int(ranked_list[list_index])
        return None


def _get_id_from_dict_or_int(photo):
    # If it's a dict, try the key 'object_id', then try 'id'
    if hasattr(photo, 'keys'):
        if 'object_id' in photo:
            return photo['object_id']
        else:
            return photo['id']
    else:
        return photo


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
    with_target = JSONField(default=0, max_length=100000)
    # These could be photos of just you, you with your friends, or group shots
    your_photos = JSONField(default=0, max_length=100000)
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

