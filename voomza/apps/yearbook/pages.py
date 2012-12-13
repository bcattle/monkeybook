import logging
from itertools import chain
import dateutil.parser
from voomza.apps.account.models import FacebookUser
from voomza.apps.backend.models import PhotoRankings, Yearbook, FacebookPhoto
from voomza.apps.backend.settings import *

logger = logging.getLogger(__name__)


class YearbookPage(object):
    def __init__(self, page):
        self.page = page

    def set_user(self, user):
        self.user = user
        # Get the user's PhotoRankings and Yearbook
        self.rankings = PhotoRankings.objects.get(user=user)
        self.yearbook = Yearbook.objects.get(owner=user)

    def get_page_content(self, user):
        self.set_user(user)
        return self.page_content()

    def get_next_content(self, user):
        raise NotImplementedError


class PhotoPage(YearbookPage):
    def __init__(self, page, ranking_name, field_name):
        self.ranking_table_name = ranking_name
        self.index_field_name = field_name
        self.field_name = '.'.join([self.ranking_table_name, self.index_field_name]),
        super(PhotoPage, self).__init__(page)

    def get_photo(self):
        photo_id = self.yearbook.get_photo_id_from_field_string(
            self.rankings, self.ranking_table_name, self.index_field_name
        )
        if not photo_id:
            photo = None
        else:
#            print '%d: %s' % (self.page, photo_id)
            photo = FacebookPhoto.objects.get(facebook_id=photo_id)
        return photo

    def get_photo_content(self, photo):
        if photo:
            return {
                'url': photo.url(),
                'is_landscape': photo.is_landscape(),
            }
        else:
            return {}

    def page_content(self):
        # De-reference the field and return pic url
        photo = self.get_photo()
        page_content = self.get_photo_content(photo)
        page_content['field'] = self.field_name
        return page_content


class PhotoWithCommentPage(PhotoPage):
    def page_content(self):
        """
        Add the top comment, commenter's name and photo
        """
        photo = self.get_photo()
        top_comment = photo.get_top_comment()

        page_content = super(PhotoWithCommentPage, self).page_content()
        if top_comment:
            page_content['top_comment'] = top_comment['text']
            page_content['top_comment_name'] = top_comment['user_name']
            page_content['top_comment_pic'] = top_comment['user_pic']
        return page_content


class TopFriendNamePage(PhotoPage):
    def __init__(self, page, ranking_name, field_name, stat_field):
        self.stat_field = stat_field
        super(TopFriendNamePage, self).__init__(page, ranking_name, field_name)

    def page_content(self):
        # De-reference the field and return
        # the user's first name and stat
        photo_list = self.yearbook.get_photo_from_field_string(
            self.rankings, self.ranking_table_name, self.index_field_name
        )
        if photo_list:
            friend_id = photo_list[0]['subject']
            try:
                friend = FacebookUser.objects.get(facebook_id=friend_id)
                friend_stat = getattr(self.yearbook, self.stat_field)
                return {
                    'name': friend.name,
                    'pic': friend.pic_square,
                    'friend_stat': friend_stat,
                    'field': self.field_name,
                }
            except FacebookUser.DoesNotExist:
                return {
                    'field': self.field_name,
                }


class AlbumPage(PhotoPage):
    def __init__(self, page, ranking_name, field_prefix, max_photos):
        self.ranking_table_name = ranking_name
        self.field_prefix = field_prefix
        self.max_photos = max_photos
        # Calls *PhotoPage* constructor!
        super(PhotoPage, self).__init__(page)

    def get_album_photos(self, field_prefix):
        photos = []
        for photo_num in range(self.max_photos):
            photo_id = self.yearbook.get_photo_id_from_field_string(
                self.rankings, self.ranking_table_name, '%s_photo_%d' % (field_prefix, (photo_num + 1))
            )
            try:
                photo = FacebookPhoto.objects.get(facebook_id=photo_id)
                photos.append(self.get_photo_content(photo))
            except FacebookPhoto.DoesNotExist:
                logger.warn('Tried to get fb photo %s, referenced by album but not in db' % photo_id)
        return photos

    def page_content(self):
        # Return up to `max_photos` photos, dereferenced to `ranking_name`
        photos = self.get_album_photos(self.field_prefix)

        # Manually get the album index
        # self.field_prefix = 'top_album_1.top_album_1'
        album_index = getattr(self.yearbook, self.field_prefix.split('.')[0])
        album_info = self.rankings.top_albums_info[album_index]
        album_name = album_info['name']

        page_content = {
            'photos': photos,
            'album_name': album_name,
            'field': '.'.join([self.ranking_table_name, self.field_prefix])
        }
        return page_content


class BackInTimePhotosPage(AlbumPage):
    """
    Note, this doesn't get the album names
    """
    def __init__(self, page, ranking_name, field_prefix, max_photos, max_albums):
        self.max_albums = max_albums
        super(BackInTimePhotosPage, self).__init__(page, ranking_name, field_prefix, max_photos)

    def get_album_photos(self, field_prefix):
        photos = []
        for photo_num in range(self.max_photos):
            photo = self.yearbook.get_photo_from_field_string(
                self.rankings, self.ranking_table_name, '%s_photo_%d' % (field_prefix, (photo_num + 1))
            )
            photos.append(photo)
        return photos

    def get_photo_content(self, photo):
        if photo:
            # photo['created'] is a string
            created = dateutil.parser.parse(photo['created'])
            return {
                'year': created.year,
                'url': photo['fb_url'],
                'is_landscape': photo['width'] > photo['height'],
            }
        else:
            return {}

    def page_content(self):
        # Dereference up to `max_albums` albums, return up to `max_photos` from each
        albums_photos = []
        for album_index in range(1, self.max_albums + 1):
            album_field_prefix = '%s_%d.%s_%d' % (self.field_prefix, album_index, self.field_prefix, album_index)
            album_photos = self.get_album_photos(field_prefix=album_field_prefix)
            albums_photos.append(album_photos)

        # Flatten the list
        photos = list(chain.from_iterable(albums_photos))
        # Get the fields we want
        photos = map(self.get_photo_content, photos)

        import ipdb
        ipdb.set_trace()

        return {
            'photos': photos,
        }


class FieldPage(YearbookPage):
    def __init__(self, page, field_name):
        self.field_name = field_name
        super(FieldPage, self).__init__(page)

    def page_content(self):
        if '.' in self.field_name:
            name0, name1 = self.field_name.split('.')
            field0 = getattr(self.yearbook, name0)
            field_value = getattr(field0, name1)
        else:
            field_value = getattr(self.yearbook, self.field_name)
        return {
            self.field_name: field_value
        }


class FriendsCollagePage(YearbookPage):
    def page_content(self):
        facepile_friend_pics = self.user.friends.all()[:NUM_FRIENDS_IN_FACEPILE]\
            .values_list('facebook_user.pic_square', flat=True)

        return {
            'facepile_friend_pics': facepile_friend_pics
        }
