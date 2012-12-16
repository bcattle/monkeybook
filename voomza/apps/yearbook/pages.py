import logging, dateutil.parser
from itertools import chain
from voomza.apps.account.models import FacebookUser
from voomza.apps.backend.models import PhotoRankings, Yearbook, FacebookPhoto
from voomza.apps.backend.settings import *

logger = logging.getLogger(__name__)


class YearbookPage(object):
    def __init__(self, page, template=None):
        self.page = page
        if template:
            self.template = template

    def set_user(self, user):
        self.user = user
        # Get the user's PhotoRankings
        self.yearbook = Yearbook.objects.get(owner=user)

    def get_page_content(self, user):
        self.set_user(user)
        page_content = self.page_content()
        page_content['page_num'] = self.page
        return page_content

    def get_next_content(self, user):
        raise NotImplementedError


class StaticPage(YearbookPage):
    """
    Returns an empty div, the background image is set in CSS
    """
    template = 'full_bleed.html'

    def __init__(self, **kwargs):
        super(StaticPage, self).__init__(**kwargs)

    def page_content(self):
        return { }


class PhotoPage(YearbookPage):
    template = 'full_bleed_editable.html'

    def __init__(self, ranking_name, field_name, force_landscape=False, **kwargs):
        self.ranking_table_name = ranking_name
        self.index_field_name = field_name
        self.force_landscape = force_landscape
        super(PhotoPage, self).__init__(**kwargs)

    def get_photo(self, field_name=None):
        field_name = field_name or self.index_field_name
        photo_id = self.yearbook.get_photo_id_from_field_string(
            self.ranking_table_name, field_name
        )
        if not photo_id:
            photo = None
        else:
#            print '%d: %s' % (self.page, photo_id)
            photo = FacebookPhoto.objects.get(facebook_id=photo_id)
        return photo

    def get_photo_content(self, photo):
        return {
            'photo': photo
        }

    def get_next_image(self, next_index):
        # De-reference the field and get the next unallocated image
        next_photo_index = self.yearbook.get_next_unused_photo(
            self.ranking_table_name, self.index_field_name, unused_index=next_index, force_landscape=self.force_landscape
        )
        next_photo = getattr(self.yearbook.rankings, self.ranking_table_name)[next_photo_index]
        next_photo_db = FacebookPhoto.objects.get(facebook_id=next_photo['id'])
        return self.get_photo_content(next_photo_db)

    def page_content(self):
        # De-reference the field and return pic url
        photo = self.get_photo()
        return self.get_photo_content(photo)



class PhotoPageDoublePort(PhotoPage):
    template='lands_sq_port_dbl_port.html'

    def __init__(self, field_name_2, **kwargs):
        self.index_field_name_2 = field_name_2
        super(PhotoPageDoublePort, self).__init__(**kwargs)

    def page_content(self):
        # De-reference the field and return pic url
        photo = self.get_photo()
        # Pull the second photo, if any
        # (only applies if first photo was portrait)
        photo_2 = self.get_photo(self.index_field_name_2)
        return {
            'photo': photo,
            'photo_2': photo_2
        }


#class SinglePhotoVariableLayout(PhotoPage):
#    template = 'lands_sq_port_dbl_port.html'


#class SinglePhotoVariableFullBleed(PhotoPage):
#    template = 'lands_sq_port_dbl_port_full_bleed.html'


class PhotoWithCommentPage(PhotoPage):
    template = 'photo_w_comment.html'

    def page_content(self):
        """
        Add the top comment, commenter's name and photo
        """
        photo = self.get_photo()
        page_content = self.get_photo_content(photo)
        top_comment = photo.get_top_comment()
        if top_comment:
            page_content['comment'] = top_comment['text']
            page_content['comment_name'] = top_comment['user_name']
            page_content['comment_pic'] = top_comment['user_pic']
        return page_content


class TopFriendNamePage(PhotoPage):
    template = 'top_friend_name.html'

    def __init__(self, ranking_name, field_name, stat_field, **kwargs):
        self.stat_field = stat_field
        super(TopFriendNamePage, self).__init__(ranking_name, field_name, **kwargs)

    def page_content(self):
        # De-reference the field and return
        # the user's first name and stat
        photo_list = self.yearbook.get_photo_from_field_string(
            self.ranking_table_name, self.index_field_name
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
                }
            except FacebookUser.DoesNotExist:
                return { }


class AlbumPage(PhotoPage):
    def __init__(self, ranking_name, field_prefix, max_photos, get_album_name=True, **kwargs):
        self.ranking_table_name = ranking_name
        self.field_prefix = field_prefix
        self.max_photos = max_photos
        self.get_album_name = get_album_name
        # Calls *PhotoPage* constructor!
        super(PhotoPage, self).__init__(**kwargs)

    def get_album_photos(self, field_prefix):
        photos = []
        for photo_num in range(self.max_photos):
            photo_id = self.yearbook.get_photo_id_from_field_string(
                self.ranking_table_name, '%s_photo_%d' % (field_prefix, (photo_num + 1))
            )
            try:
                photo = FacebookPhoto.objects.get(facebook_id=photo_id)
                photos.append(self.get_photo_content(photo))
            except FacebookPhoto.DoesNotExist:
                logger.warn('Tried to get fb photo %s, referenced by album but not in db' % photo_id)
        return photos

    def get_next_image(self, next_index, photo_index):
        # De-reference the field and get the next unallocated image
        field_name = '%s_photo_%d' % (self.field_prefix, (photo_index+ 1))
        next_photo_index = self.yearbook.get_next_unused_photo(
            self.ranking_table_name, field_name, unused_index=next_index
        )
        album_num = getattr(self.yearbook, self.field_prefix.split('.')[0])
        next_photo = getattr(self.yearbook.rankings, self.ranking_table_name)[album_num][next_photo_index]
        next_photo_db = FacebookPhoto.objects.get(facebook_id=next_photo['id'])
        return self.get_photo_content(next_photo_db)

    def page_content(self):
        # Return up to `max_photos` photos, dereferenced to `ranking_name`
        photos = self.get_album_photos(self.field_prefix)
        # Sort them according to whether they are portrait or landscape
        photos_portrait = [photo for photo in photos if not photo.is_landscape()]       # includes square
        photos_landscape = [photo for photo in photos if photo.is_landscape()]

        album_name = ''
        if self.get_album_name:
            # Manually get the album index
            # self.field_prefix = 'top_album_1.top_album_1'
            album_index = getattr(self.yearbook, self.field_prefix.split('.')[0])
            album_info = self.yearbook.rankings.top_albums_info[album_index]
            album_name = album_info['name']

        page_content = {
            'photos': photos,
            'photos_portrait': photos_portrait,
            'photos_landscape': photos_landscape,
            'album_name': album_name,
        }
        return page_content


#class TopFriendPhotoPage(AlbumPage):
#    template='lands_sq_port_dbl_port_full_bleed.html'
#
#    def __init__(self, ranking_name, field_name, stat_field, **kwargs):
#        self.stat_field = stat_field
#        super(TopFriendPhotoPage, self).__init__(ranking_name, field_name, **kwargs)
#
#    def page_content(self):
#        pass


class BackInTimePhotosPage(AlbumPage):
    def __init__(self, ranking_name, field_prefix, max_photos, max_albums, **kwargs):
        self.max_albums = max_albums
        super(BackInTimePhotosPage, self).__init__(ranking_name, field_prefix, max_photos, **kwargs)

    def get_album_photos(self, field_prefix):
        photos = []
        for photo_num in range(self.max_photos):
            photo = self.yearbook.get_photo_from_field_string(
                self.ranking_table_name, '%s_photo_%d' % (field_prefix, (photo_num + 1))
            )
            photos.append(photo)
        return photos

    def get_photo_content(self, photo):
        if photo:
            # photo['created'] is a string
            created = dateutil.parser.parse(photo['created'])
            return {
                'year': created.year,
                'photo': photo,
#                'url': photo['fb_url'],
#                'is_landscape': photo['width'] > photo['height'],
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

        return {
            'photos': photos,
        }


class FieldPage(YearbookPage):
    def __init__(self, field_name, **kwargs):
        self.field_name = field_name
        super(FieldPage, self).__init__(**kwargs)

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
    # Pull the facepile from the existing (invites) API
    def page_content(self):
        facepile_friend_pics = self.user.friends.all()[:NUM_FRIENDS_IN_FACEPILE]\
            .values_list('facebook_user__pic_square', flat=True)

        return {
            'facepile_friend_pics': facepile_friend_pics
        }


class YearbookPageFactory(object):
    _pages = [
#        FieldPage(            page=3,  field_name='owner.first_name'),
        StaticPage(           page=3),
        # Top photos
        StaticPage(           page=4),
        PhotoPage(            page=5,  ranking_name='top_photos',             field_name='top_photo_1',         force_landscape=True),
        PhotoWithCommentPage( page=6,  ranking_name='top_photos',             field_name='top_photo_2'),
        PhotoWithCommentPage( page=7,  ranking_name='top_photos',             field_name='top_photo_3'),
        StaticPage(           page=8),
        PhotoPage(            page=9,  ranking_name='top_photos_first_half',  field_name='first_half_photo_1',  force_landscape=True),
        PhotoPageDoublePort(  page=10, ranking_name='top_photos_first_half',  field_name='first_half_photo_2',  field_name_2='first_half_photo_4'),
        PhotoPageDoublePort(  page=11, ranking_name='top_photos_first_half',  field_name='first_half_photo_3',  field_name_2='first_half_photo_5'),
        StaticPage(           page=12),
        PhotoPage(            page=13, ranking_name='top_photos_second_half', field_name='second_half_photo_1', force_landscape=True),
        PhotoPageDoublePort(  page=14, ranking_name='top_photos_second_half', field_name='second_half_photo_2', field_name_2='second_half_photo_4'),
        PhotoPageDoublePort(  page=15, ranking_name='top_photos_second_half', field_name='second_half_photo_3', field_name_2='second_half_photo_5'),
        # Group photos
        StaticPage(           page=16),
        PhotoPage(            page=17, ranking_name='group_shots',            field_name='group_photo_1',       force_landscape=True),
        PhotoWithCommentPage( page=18, ranking_name='group_shots',            field_name='group_photo_2'),
        PhotoWithCommentPage( page=19, ranking_name='group_shots',            field_name='group_photo_3'),
        StaticPage(           page=20),
        AlbumPage(            page=21, ranking_name='top_albums',    field_prefix='top_album_1.top_album_1', max_photos=ALBUM_PHOTOS_TO_SHOW, template='album_page_1.html'),
        AlbumPage(            page=22, ranking_name='top_albums',    field_prefix='top_album_2.top_album_2', max_photos=ALBUM_PHOTOS_TO_SHOW, template='album_page_2.html'),
        AlbumPage(            page=23, ranking_name='top_albums',    field_prefix='top_album_3.top_album_3', max_photos=ALBUM_PHOTOS_TO_SHOW, template='album_page_3.html'),
        StaticPage(           page=24),
        StaticPage(           page=25),
        StaticPage(           page=26),
        # Top status message
        FieldPage(            page=27, field_name='top_post',           template='top_status.html'),

        # Birthday comments
        # really a two-page spread
        FieldPage(            page=28, field_name='birthday_posts',     template='birthday_left.html'),
        FieldPage(            page=29, field_name='birthday_posts',     template='birthday_right.html'),

        # Top photos back in time
        # really a two-page spread
        BackInTimePhotosPage( page=30, ranking_name='back_in_time', field_prefix='back_in_time', max_photos=1, max_albums=NUM_PREV_YEARS,   template='back_in_time_left.html'),
        BackInTimePhotosPage( page=31, ranking_name='back_in_time', field_prefix='back_in_time', max_photos=1, max_albums=NUM_PREV_YEARS,   template='back_in_time_right.html'),
        StaticPage(           page=32),
        StaticPage(           page=33),
        TopFriendNamePage(    page=34, ranking_name='top_friends', field_name='top_friend_1',      stat_field='top_friend_1_stat'),
        AlbumPage(            page=35, ranking_name='top_friends', field_prefix='top_friend_1.top_friend_1', max_photos=TOP_FRIEND_PHOTOS_TO_SHOW,  template='lands_sq_port_dbl_port_full_bleed.html', get_album_name=False),
        TopFriendNamePage(    page=36, ranking_name='top_friends', field_name='top_friend_2',      stat_field='top_friend_2_stat'),
        AlbumPage(            page=37, ranking_name='top_friends', field_prefix='top_friend_1.top_friend_1', max_photos=TOP_FRIEND_PHOTOS_TO_SHOW,  template='lands_sq_port_dbl_port_full_bleed.html', get_album_name=False),
        TopFriendNamePage(    page=38, ranking_name='top_friends', field_name='top_friend_3',      stat_field='top_friend_3_stat'),
        AlbumPage(            page=39, ranking_name='top_friends', field_prefix='top_friend_1.top_friend_1', max_photos=TOP_FRIEND_PHOTOS_TO_SHOW,  template='lands_sq_port_dbl_port_full_bleed.html', get_album_name=False),
        TopFriendNamePage(    page=40, ranking_name='top_friends', field_name='top_friend_4',      stat_field='top_friend_4_stat'),
        AlbumPage(            page=41, ranking_name='top_friends', field_prefix='top_friend_1.top_friend_1', max_photos=TOP_FRIEND_PHOTOS_TO_SHOW,  template='lands_sq_port_dbl_port_full_bleed.html', get_album_name=False),
        TopFriendNamePage(    page=42, ranking_name='top_friends', field_name='top_friend_5',      stat_field='top_friend_5_stat'),
        AlbumPage(            page=43, ranking_name='top_friends', field_prefix='top_friend_1.top_friend_1', max_photos=TOP_FRIEND_PHOTOS_TO_SHOW,  template='lands_sq_port_dbl_port_full_bleed.html', get_album_name=False),

        # Friends collage
        # really a two-page spread
        FriendsCollagePage(   page=44),
        FriendsCollagePage(   page=45),
    ]

    def __init__(self):
        """
        Set page numbers of all child pages
        """
        for num, page_class in enumerate(self._pages):
            page_class.page = num

    def pages(self):
        return self._pages

    def get_page(self, page):
        if 0 < page < len(self._pages):
            return self._pages[page]
        return None
