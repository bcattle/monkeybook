#from __future__ import division, print_function, unicode_literals
#from django.utils.encoding import python_2_unicode_compatible
import logging
from django.core.urlresolvers import reverse
from django.db import models
from django.dispatch.dispatcher import receiver
from jsonfield.fields import JSONField
from south.signals import post_migrate
from monkeybook.apps.account.models import FacebookUser
from monkeybook.apps.backend import short_url
from monkeybook.apps.backend.managers import FacebookPhotoManager, YearbookManager
from monkeybook.apps.backend.settings import *

logger = logging.getLogger(__name__)


#@python_2_unicode_compatible
class FacebookPhoto(models.Model):
    facebook_id = models.BigIntegerField(primary_key=True)
    created = models.DateTimeField(null=True)
    people_in_photo = models.PositiveSmallIntegerField(default=0, help_text='Total, i.e. including me')

    height = models.PositiveIntegerField(default=0)
    width = models.PositiveIntegerField(default=0)
    fb_url = models.CharField(max_length=200)
    all_sizes = JSONField(default="[]", max_length=100000)

    local_url = models.CharField(max_length=200, default='')
    caption = models.CharField(max_length=1000, default='')
    comments = JSONField(default="[]", max_length=100000)

    def url(self):
        return self.local_url or self.fb_url

#    def __str__(self):
#        return 'FacebookPhoto <%d>' % self.facebook_id 

    @property
    def aspect_ratio(self):
        return float(self.width) / float(self.height)

    def is_square(self):
        return LOWEST_SQUARE_ASPECT_RATIO < self.aspect_ratio < HIGHEST_SQUARE_ASPECT_RATIO

    def is_portrait(self):
        return self.aspect_ratio < LOWEST_SQUARE_ASPECT_RATIO

    def is_landscape(self):
        return self.aspect_ratio > HIGHEST_SQUARE_ASPECT_RATIO

    def _comment_score(self, comment):
        score = \
            COMMENT_POINTS_I_LIKE * comment['likes'] + \
            COMMENT_POINTS_FOR_LIKE * (1 if comment['user_likes'] else 0)
        return score

    def get_top_comment(self):
        if self.comments:

            # Assign a score
            for comment in self.comments:
                comment['score'] = self._comment_score(comment)

            # Sort by score, then by date
            # Take the highest-scoring, earliest
            comments_sorted = sorted(self.comments,
                                     key=lambda comment: (-comment['score'], comment['time']))

            top_comment, top_comment_name, top_comment_pic = '', '', ''
            for comment in comments_sorted:
                # Get user's name and photo
                try:
                    fb_user = FacebookUser.objects.get(facebook_id=comment['fromid'])
                except FacebookUser.DoesNotExist:
                    continue
                # If the user exists
                if fb_user.name and fb_user.pic_square:
                    top_comment_name = fb_user.name
                    top_comment_pic = fb_user.pic_square
                    top_comment = comment

            return {
                'text': top_comment,
                'user_name': top_comment_name,
                'user_pic': top_comment_pic,
            }

    objects = FacebookPhotoManager()


#@python_2_unicode_compatible
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

#    def __str__(self):         
    def __unicode__(self):
        return 'PhotoRankings %s' % self.user.username

    class Meta:
        verbose_name_plural = 'Photo rankings'


#@python_2_unicode_compatible
class Yearbook(models.Model):
#    rankings = models.OneToOneField(PhotoRankings, related_name='yearbook')
    rankings = models.ForeignKey(PhotoRankings, related_name='yearbook')
    hash = models.CharField(max_length=20, unique=True, blank=True)       # Not a db index, since we have a deterministic hash fxn
    created = models.DateTimeField(auto_now_add=True)
    run_time = models.FloatField(null=True)

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
    friends_in_book = JSONField(default="[]", max_length=100000)

    _all_used_ids = None

    def save(self, *args, **kwargs):
        """
        If needed, generates a short url for this book
        """
        if self.id is None:
            # Save the book to get the pk
            super(Yearbook, self).save(*args, **kwargs)
            # Generate a short url
            self.hash = short_url.encode_url(self.id)
            # Re-save
        super(Yearbook, self).save(*args, **kwargs)


    objects = YearbookManager()

#    def __str__(self):    
    def __unicode__(self):
        return 'Yearbook %d <%s, %s>' % (self.id, self.rankings.username, self.hash)

    class Meta:
        ordering = ['-created']
        get_latest_by = 'created'

    def get_absolute_url(self):
        return reverse('yearbook', kwargs={'hash': self.hash})

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

    def num_unused_photos(self, photos):
        """
        Returns the number of photos in a list
        that are unused
        """
        unused = 0
        for photo in photos:
            if not self.photo_is_used(photo):
                unused += 1
        return unused

    def photo_is_used(self, photo, used_ids=None):
        """
        Iterates through all image index fields on the model,
        verifying that the images they refer to are not "claimed"
        """
        used_ids = used_ids or []
        photo_id = self._get_id_from_dict_or_int(photo)
        if photo_id in used_ids:
            return True
        all_used_ids = self._get_all_used_ids()
        return photo_id in all_used_ids

    def _get_all_used_ids(self):
        all_ids = []
        for ranked_list_name, yb_fields in self.lists_to_fields.items():
            for yb_field in yb_fields:
                photo_id = self.get_photo_id_from_field_string(ranked_list_name, yb_field)
                if not photo_id is None:
                    all_ids.append(photo_id)
        return all_ids

    def get_n_unused_photos(self, list_of_photos, n, force_landscape=False, start_index=0):
        unused_photos = []
        used_ids = []
        while len(unused_photos) < n:
            if force_landscape:
                unused_photo = self.get_first_unused_photo_landscape(list_of_photos, used_ids, start_index)
            else:
                unused_photo = self.get_first_unused_photo(list_of_photos, used_ids, start_index)
            if unused_photo is None:
                # List ran out, return what we had
                return unused_photos
            else:
                unused_photos.append(unused_photo)
                used_ids.append(self._get_id_from_dict_or_int(list_of_photos[unused_photo]))
        return unused_photos

    def get_first_unused_photo(self, list_of_photos, used_ids=None, used_indices=None, start_index=0, return_id=False):
        """
        Loops through photos in `list_of_photos`,
        If no photo unused, return None
        """
        used_indices = used_indices or []
        for index, photo in enumerate(list_of_photos[start_index:]):
            if index in used_indices:
                continue
            if not self.photo_is_used(photo, used_ids):
                if return_id:
                    return index + start_index, self._get_id_from_dict_or_int(photo)
                return index + start_index
        if return_id:
            return None, None
        return None

    def get_first_unused_photo_landscape(self, list_of_photos, used_ids=None, start_index=0, return_id=False):
        """
        Loops through photos in `list_of_photos`,
        running `yearbook.photo_is_used()` until it returns False
        *and* photo width is greater than its height.
        If no photo unused, return None
        """
        for index, photo in enumerate(list_of_photos[start_index:]):
            if not self.photo_is_used(photo, used_ids) and photo:
                # Is the photo landscape?
                if hasattr(photo, 'keys'):
                    if photo['width'] < photo['height']:
                        continue
                    if return_id:
                        return index + start_index, self._get_id_from_dict_or_int(photo)
                    return index + start_index
                else:
                    # Bummer, just an id - look it up in the database
                    try:
                        photo_db = FacebookPhoto.objects.get(facebook_id=photo)
                        if not photo_db.is_landscape():
                            continue
                    except FacebookPhoto.DoesNotExist:
                        logger.warn('Attempted to look up fb photo %d, doesn\'t exist in db.' % photo)
                        continue
                    if return_id:
                        return index + start_index, photo_db.facebook_id
                    return index + start_index
        if return_id:
            return None, None
        return None

    def get_first_unused_photo_portrait(self, list_of_photos, used_ids=None, start_index=0):
        """
        Loops through photos in `list_of_photos`,
        running `yearbook.photo_is_used()` until it returns False
        *and* photo height is greater than its width.
        If no photo unused, return None
        """
        for index, photo in enumerate(list_of_photos[start_index:]):
            if not self.photo_is_used(photo, used_ids) and photo:
                # Is the photo landscape?
                if hasattr(photo, 'keys'):
                    if photo['width'] > photo['height']:
                        continue
                else:
                    # Bummer, just an id - look it up in the database
                    try:
                        photo_db = FacebookPhoto.objects.get(facebook_id=photo)
                        if not photo_db.is_portrait():
                            continue
                    except FacebookPhoto.DoesNotExist:
                        logger.warn('Attempted to look up fb photo %d, doesn\'t exist in db.' % photo)
                        continue
                return index + start_index
        return None


    def get_next_unused_photo(self, ranked_list_name, yb_field, unused_index=0, force_landscape=False):
        """
        Get the next unused photo in a list referred to by field name
        `unused_index` : returns the nth unused photo
        """
        photo_list = getattr(self.rankings, ranked_list_name)
        # Dereference the field, get the current index of the image being used
        curr_photo_index = self.get_photo_index_from_field_string(yb_field)
        # Get `unused_index` unused photos after that
        unused_photos = self.get_n_unused_photos(
            photo_list, unused_index + 1, force_landscape=force_landscape, start_index=curr_photo_index
        )
        # Return the last of these
        if unused_photos:
            return unused_photos[-1]
        else:
            return None

    def get_photo_index_from_field_string(self, yb_field):
        """
        Returns the index of the image being referred to by `yb_field`
        """
        if '.' in yb_field:
            # Double-indirection
            photo_list_index_field, photo_index_field = yb_field.split('.')
            photo_index = getattr(self, photo_index_field)
        else:
            photo_index = getattr(self, yb_field)
        return photo_index

    def get_photo_from_field_string(self, ranked_list_name, yb_field):
        """
        De-references and returns the photo struct of a photo referred
        to by a field in the PhotoRankings and a field in the Yearbook.
        Examples:       'family_with', 'family_photo_1'
                        'top_friends', 'top_friend_1.top_friend_1_photo_1'
        Returns None if photo list or index is empty
        """
        ranked_list = getattr(self.rankings, ranked_list_name)
        if ranked_list:
            if '.' in yb_field:
                # Double-indirection
                photo_list_index_field, photo_index_field = yb_field.split('.')
                photo_list_index = getattr(self, photo_list_index_field)
                photo_index = getattr(self, photo_index_field)
                if (not photo_list_index is None) and (not photo_index is None):
                    photo_list = ranked_list[photo_list_index]
                    # `photo_list` could be a list of structs, or integers
                    return  photo_list[photo_index]
            else:
                # Dereference the field back to the original facebook id
                list_index = getattr(self, yb_field)
                if not list_index is None:
                    # `ranked_list` is either a list of structs, or integers
                    return ranked_list[list_index]
        return None

    def get_photo_id_from_field_string(self, ranked_list_name, yb_field):
        """
        De-references and returns the *id* of the photo referred
        to by a field in the PhotoRankings and a field in the Yearbook.
        Examples:       'family_with', 'family_photo_1'
                        'top_friends', 'top_friend_1.top_friend_1_photo_1'
        Returns None if photo list or index is empty
        """
        photo = self.get_photo_from_field_string(ranked_list_name, yb_field)
        return self._get_id_from_dict_or_int(photo)

    def dump_to_console(self):
        """
            top_photos    (45 photos)
            -------------------
                            1120392001 (U)
            top_photo_1 --> 1120392001 (U)
                            1120392001
        """
        print('Yearbook for user <%s>\n' % self.rankings.user.username)
        single_indirect = [item for item in self.lists_to_fields.items() if '.' not in item[1][0]]
        dbl_indirect = [item for item in self.lists_to_fields.items() if '.' in item[1][0]]

        # Do single indirection first
        for ranked_list_name, yb_fields in single_indirect:
            ranked_list = getattr(self.rankings, ranked_list_name)
            self.dump_list(ranked_list_name, ranked_list, yb_fields)

        for ranked_list_name, yb_fields in dbl_indirect:
            ranked_list = getattr(self.rankings, ranked_list_name)
            fields_by_index_field = {}
            for yb_field in yb_fields:
                list_index_field_name, photo_field_name = yb_field.split('.')
                if list_index_field_name in fields_by_index_field:
                    fields_by_index_field[list_index_field_name].append(photo_field_name)
                else:
                    fields_by_index_field[list_index_field_name] = [photo_field_name]

            # Now have a list of photo fields by field index,
            # dump these
            for list_name, fields in fields_by_index_field.items():
                sub_list_index = getattr(self, list_name)
                sub_list_name_str = '%s : %s --> %d' % (ranked_list_name, list_name, sub_list_index)
                self.dump_list(sub_list_name_str, ranked_list[sub_list_index], fields)
        print('\n')


    def dump_list(self, list_name, photo_list, list_fields):
        """
        `list_fields` -> the fields that point into the list
        """
        MAX_PHOTOS_PER_LIST = 25
        # Print the name of the ranking table
        print('%s\t(%d photos)\n%s' % (list_name, len(photo_list), '-'*(len(list_name) + 20)))
        # For each entry in the list, print
        # (1) whether it is pointed to by a field in `yb_fields`
        # (2) the ID, and (3) whether the ID is in use elsewhere
        longest_field = max([len(field) for field in list_fields])
        for index, photo in enumerate(photo_list):
            field_str = ' '*(longest_field + 4)
            # Is it pointed to from `yb_fields`?
            for field in list_fields:
                if self.get_photo_index_from_field_string(field) == index:
                    field_str = '%s -->' % field
                    break
                # Is it in use in the yearbook?
            in_use_str = ''
            if self.photo_is_used(photo):
                in_use_str = '(U)'
            score_str = portrait_str = ''
            if hasattr(photo, 'keys'):
                if 'score' in photo:
                    score_str = photo['score']
                if 'width' in photo and 'height' in photo:
                    if photo['width'] < photo['height']:
                        portrait_str = 'Portrait'
            photo_str = '%s %s %s %s %s' % (field_str, str(self._get_id_from_dict_or_int(photo)).ljust(18), str(score_str).ljust(3), in_use_str, portrait_str)
            print(photo_str)

            if index >= MAX_PHOTOS_PER_LIST:
                print(' '*(longest_field + 4) + '  ...')
                break
        print('\n')


    def _get_id_from_dict_or_int(self, photo):
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
    with_target = JSONField(default="[]", max_length=100000)
    # These could be photos of just you, you with your friends, or group shots
    your_photos = JSONField(default="[]", max_length=100000)
    # Should both of these be in the same table?



#@receiver(post_syncdb, dispatch_uid='backend.models')
@receiver(post_migrate, dispatch_uid='backend.models')
def set_table_row_format(app, **kwargs):
    # post_syncdb, `app` is a Module. post_migrate `app` is a string
    if app == 'backend':
        from django.conf import settings
        if settings.DATABASES['default']['ENGINE'] == 'django.db.backends.mysql':
            # Set ROW_FORMAT=DYNAMIC to allow longer rows
            from django.db import connection, transaction
            cursor = connection.cursor()
            cursor.execute('ALTER TABLE `%s` ROW_FORMAT=DYNAMIC' % PhotoRankings._meta.db_table)
            transaction.commit_unless_managed()

