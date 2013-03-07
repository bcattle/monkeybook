from __future__ import division, print_function, unicode_literals
import logging, dateutil.parser
from itertools import chain
from voomza.apps.account.models import FacebookUser
from voomza.apps.books_common.models import FacebookPhoto

logger = logging.getLogger(__name__)


class PageInvalidError(Exception):
    """
    This exception is raised when a page should be omitted,
    for instance if it is lacking some necessary data
    """


class BookPage(object):
    def __init__(self, page, template=None):
        self.page = page
        if template:
            self.template = template

        #    def set_user(self, user):
        #        self.user = user
        #        # Get the user's PhotoRankings
        #        self.yearbook = Yearbook.objects.get(rankings__user=user)

        #    def get_page_content(self, user):
    def get_page_content(self):
        """
        If the page raises an exception, kill it
        Any exception other than PageInvalidError, log
        """
        #        self.set_user(user)
        #        try:
        page_content = self.page_content()
        #        except PageInvalidError:
        # The page is no good, return the empty page
        #            pass
        #        except Exception:
        # Some other error happened, log it
        #            logger.error()
        page_content['page'] = self.page
        return page_content


class StaticPage(BookPage):
    """
    Returns an empty div, the background image is set in CSS
    """
    template = 'full_bleed.html'

    def __init__(self, **kwargs):
        super(StaticPage, self).__init__(**kwargs)

    def page_content(self):
        return { }


class PhotoPage(BookPage):
    template = 'full_bleed_editable.html'

    def __init__(self, ranking_name, field_name, force_landscape=False, **kwargs):
        self.ranking_table_name = ranking_name
        self.index_field_name = field_name
        self.force_landscape = force_landscape
        super(PhotoPage, self).__init__(**kwargs)

    def get_photo(self, field_name=None):
        field_name = field_name or self.index_field_name
        photo_id = self.book.get_photo_id_from_field_string(
            self.ranking_table_name, field_name
        )
        if not photo_id:
            photo = None
        else:
            photo = FacebookPhoto.objects.get(facebook_id=photo_id)
        return photo

    def get_photo_content(self, photo):
        return {
            'photo': photo
        }

    def get_next_image(self, next_index, photo_index=None):
        # De-reference the field and get the next unallocated image
        import ipdb
        ipdb.set_trace()

        next_photo_index = self.book.get_next_unused_photo(
            self.ranking_table_name, self.index_field_name, unused_index=next_index, force_landscape=self.force_landscape
        )
        if not next_photo_index:
            return None
        else:
            next_photo = getattr(self.book.rankings, self.ranking_table_name)[next_photo_index]
            next_photo_db = FacebookPhoto.objects.get(facebook_id=next_photo['id'])
            return next_photo_db

    def get_next_content(self, next_index, photo_index=None):
        photo = self.get_next_image(next_index, photo_index)
        return self.get_photo_content(photo)

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
        album_name = ''
        for photo_num in range(self.max_photos):
            photo = self.book.get_photo_from_field_string(
                self.ranking_table_name, '%s_photo_%d' % (field_prefix, (photo_num + 1))
            )
            if photo:
                if 'album_name' in photo:
                    album_name = photo['album_name']
                else:
                    album_name = ''
                photo_id = self.book._get_id_from_dict_or_int(photo)
                try:
                    photo = FacebookPhoto.objects.get(facebook_id=photo_id)
                    photos.append(photo)
                except FacebookPhoto.DoesNotExist:
                    logger.warn('Tried to get fb photo %s, referenced by album but not in db' % photo_id)
        return photos, album_name

    def get_next_image(self, next_index, photo_index):
        # De-reference the field and get the next unallocated image
        field_name = '%s_photo_%d' % (self.field_prefix, (photo_index+ 1))
        next_photo_index = self.book.get_next_unused_photo(
            self.ranking_table_name, field_name, unused_index=next_index
        )
        album_num = getattr(self.book, self.field_prefix.split('.')[0])
        next_photo = getattr(self.book.rankings, self.ranking_table_name)[album_num][next_photo_index]
        next_photo_db = FacebookPhoto.objects.get(facebook_id=next_photo['id'])
        return self.get_photo_content(next_photo_db)

    def page_content(self):
        # Return up to `max_photos` photos, dereferenced to `ranking_name`
        photos, album_name = self.get_album_photos(self.field_prefix)
        # Sort them according to whether they are portrait or landscape
        photos_portrait = [photo for photo in photos if not photo.is_landscape()]       # includes square
        photos_landscape = [photo for photo in photos if photo.is_landscape()]

#        album_name = ''
#        if self.get_album_name:
#            # Manually get the album index
#            # self.field_prefix = 'top_album_1.top_album_1'
#            album_index = getattr(self.book, self.field_prefix.split('.')[0])
#            album_info = self.book.rankings.top_albums_ranked[album_index]
##            album_name = album_info['name']
#            album_name = ''

        page_content = {
            'photos': photos,
            'photos_portrait': photos_portrait,
            'photos_landscape': photos_landscape,
            'album_name': album_name,
            }
        return page_content


class MultiAlbumPage(AlbumPage):
    def __init__(self, max_albums, **kwargs):
        self.max_albums = max_albums
        super(MultiAlbumPage, self).__init__(**kwargs)

    def get_album_photos(self, field_prefix):
        photos = []
        for photo_num in range(self.max_photos):
            photo_id = self.book.get_photo_id_from_field_string(
                self.ranking_table_name, '%s_photo_%d' % (field_prefix, (photo_num + 1))
            )
            if photo_id is not None:
                photo = FacebookPhoto.objects.get(facebook_id=photo_id)
                photos.append(photo)
        return photos

    def page_content(self):
        # Dereference up to `max_albums` albums, return up to `max_photos` from each
        albums_photos = []
        for album_index in range(1, self.max_albums + 1):
            album_field_prefix = '%s_%d.%s_%d' % (self.field_prefix, album_index, self.field_prefix, album_index)
            album_photos = self.get_album_photos(field_prefix=album_field_prefix)
            albums_photos.append(album_photos)

        # Flatten the list
        photos = list(chain.from_iterable(albums_photos))

        return {
            'photos': photos,
            'photos_reversed': list(reversed(photos)),
            }


class FieldPage(BookPage):
    def __init__(self, field_name, **kwargs):
        self.field_name = field_name
        super(FieldPage, self).__init__(**kwargs)

    def page_content(self):
        if '.' in self.field_name:
            name0, name1 = self.field_name.split('.')
            field0 = getattr(self.book, name0)
            field_value = getattr(field0, name1)
        else:
            field_value = getattr(self.book, self.field_name)
        return {
            self.field_name: field_value
        }

    def get_user_by_id(self, facebook_id):
        """
        Helper that looks up a user by id, where they could be the
        current user or one of the current user's facebook friends
        """
        try:
            fb_user = FacebookUser.objects.get(facebook_id=facebook_id)
            return fb_user
        except FacebookUser.DoesNotExist:
            return None

