from voomza.apps.backend.models import PhotoRankings, Yearbook, FacebookPhoto


class YearbookPage(object):
    def __init__(self, page):
        self.page = page

    def set_user(self, user):
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
        super(PhotoPage, self).__init__(page)

    def page_content(self):
        # De-reference the field and return pic url
        photo_id = self.yearbook.get_photo_from_field_string(
            self.rankings, self.ranking_table_name, self.index_field_name
        )
        if not photo_id:
            url = ''
        else:
            photo = FacebookPhoto.objects.get(facebook_id=photo_id)
            url = photo.url()

        return {
            'url': url,
            'field': '.'.join([self.ranking_table_name, self.index_field_name]),
        }


class PhotoWithCommentPage(PhotoPage):
    def page_content(self):
        return {

        }


class TopFriendNamePage(PhotoPage):
    def page_content(self):
        # De-reference the field and return the user's first name
        photo_id = self.yearbook.get_photo_from_field_string(
            self.rankings, self.ranking_table_name, self.index_field_name
        )
        if not photo_id:
            url = ''
        else:
            photo = FacebookPhoto.objects.get(facebook_id=photo_id)
            url = photo.url()

        return {
            'url': url,
            'field': '.'.join([self.ranking_table_name, self.index_field_name]),
            }


class AlbumPage(YearbookPage):
    def __init__(self, page, ranking_name, max_photos):
        self.ranking_table_name = ranking_name
        self.max_photos = max_photos
        super(AlbumPage, self).__init__(page)

    def page_content(self):
        return {

        }


class FieldPage(YearbookPage):
    def __init__(self, page, field_name):
        self.field_name = field_name
        super(FieldPage, self).__init__(page)

    def page_content(self):
        return {

        }


class BackInTimePage(YearbookPage):
    def page_content(self):
        return {

        }


class FriendsCollagePage(YearbookPage):
    def page_content(self):
        return {

        }
