from voomza.apps.backend.models import PhotoRankings, Yearbook, FacebookPhoto

class YearbookPage(object):
    def __init__(self, page):
        self.page = page

    def set_user(self, user):
        # Get the user's PhotoRankings and Yearbook
        self.rankings = PhotoRankings.objects.get(user=user)
        self.yearbook = Yearbook.objects.get(owner=user)

    def get_page_content(self, user):
        raise NotImplementedError

    def get_next_content(self, user):
        raise NotImplementedError


class PhotoPage(YearbookPage):
    def __init__(self, page, ranking_name, field_name):
        self.ranking_table_name = ranking_name
        self.index_field_name = field_name
        super(PhotoPage, self).__init__(page)

    def get_page_content(self, user):
        self.set_user(user)
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
    @property
    def page_content(self):
        return {

        }


class FourPhotosPage(PhotoPage):
    @property
    def page_content(self):
        return {

        }
