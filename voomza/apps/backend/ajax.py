from tastypie import fields
from tastypie.bundle import Bundle
from tastypie.exceptions import NotFound
from tastypie.resources import Resource
from tastypie.authorization import Authorization
from tastypie.authentication import SessionAuthentication
from tastypie.api import Api
from voomza.apps.yearbook.pages import PhotoWithCommentPage, PhotoPage, YearbookPage, AlbumPage, FieldPage, TopFriendNamePage, BackInTimePage, FriendsCollagePage


class PageResource(Resource):
    page = fields.IntegerField(attribute='page', readonly=True)
    page_content = fields.CharField(readonly=True)

    class Meta:
        resource_name = 'page'
        object_class = YearbookPage
        authentication = SessionAuthentication()
        authorization = Authorization()

    def detail_uri_kwargs(self, bundle_or_obj):
        """
        Given a Bundle or an object,
        returns the extra kwargs needed to generate a detail URI
        """
        kwargs = {}
        if isinstance(bundle_or_obj, Bundle):
            kwargs['page'] = bundle_or_obj.obj.page
        else:
            kwargs['page'] = bundle_or_obj.page
        return kwargs

    def obj_get_list(self, request=None, **kwargs):
        """
        Runs before filters
        """
        return self.get_object_list(request)


    def get_object_list(self, request):
        """
        Runs after filters
        """
        # Return the pages
        return YearbookPageFactory.pages()

    
    def obj_get(self, request=None, **kwargs):
        """
        Fetches an individual object on the resource.
        If the object can not be found this should raise a NotFound exception
        """
        page_cls = YearbookPageFactory.get_page(kwargs['page'])
        if not page_cls:
            raise NotFound
        return page_cls(request.user)


    def dehydrate(self, bundle):
        user = bundle.request.user
        bundle.data['page_content'] = bundle.obj.get_page_content(user)
        return bundle



class YearbookPageFactory(object):
    _pages = [
        FieldPage(            page=3, field_name='owner.first_name'),

        PhotoPage(            page=5,  ranking_name='top_photos',             field_name='top_photo_1'),
        PhotoWithCommentPage( page=6,  ranking_name='top_photos',             field_name='top_photo_2'),
        PhotoWithCommentPage( page=7,  ranking_name='top_photos',             field_name='top_photo_3'),

        PhotoPage(            page=9,  ranking_name='top_photos_first_half',  field_name='first_half_photo_1'),
        PhotoPage(            page=10, ranking_name='top_photos_first_half',  field_name='first_half_photo_2'),
        PhotoPage(            page=11, ranking_name='top_photos_first_half',  field_name='first_half_photo_3'),
        PhotoPage(            page=12, ranking_name='top_photos_second_half', field_name='second_half_photo_1'),
        PhotoPage(            page=13, ranking_name='top_photos_second_half', field_name='second_half_photo_2'),
        PhotoPage(            page=14, ranking_name='top_photos_second_half', field_name='second_half_photo_3'),

        PhotoPage(            page=16, ranking_name='group_shots',            field_name='group_photo_1'),
        PhotoWithCommentPage( page=17, ranking_name='group_shots',            field_name='group_photo_2'),
        PhotoWithCommentPage( page=18, ranking_name='group_shots',            field_name='group_photo_3'),

        AlbumPage(            page=20, ranking_name='top_albums.top_album_1', max_photos=4),
        AlbumPage(            page=21, ranking_name='top_albums.top_album_2', max_photos=4),
        AlbumPage(            page=22, ranking_name='top_albums.top_album_3', max_photos=4),

        # Top status message
        FieldPage(            page=26, field_name='top_comment'),

        # Birthday comments
        FieldPage(            page=27, field_name='birthday_comments'),
                              # really a two-page spread

        # Top photos back in time
        BackInTimePage(       page=29),
                              # really a two-page spread

        TopFriendNamePage(    page=33, ranking_name='top_friends',              field_name='top_friend_1'),
        PhotoPage(            page=34, ranking_name='top_friends.top_friend_1', field_name='top_friend_1_photo_1'),
        TopFriendNamePage(    page=35, ranking_name='top_friends',              field_name='top_friend_2'),
        PhotoPage(            page=36, ranking_name='top_friends.top_friend_2', field_name='top_friend_2_photo_1'),
        TopFriendNamePage(    page=37, ranking_name='top_friends',              field_name='top_friend_3'),
        PhotoPage(            page=38, ranking_name='top_friends.top_friend_3', field_name='top_friend_3_photo_1'),
        TopFriendNamePage(    page=39, ranking_name='top_friends',              field_name='top_friend_4'),
        PhotoPage(            page=40, ranking_name='top_friends.top_friend_4', field_name='top_friend_4_photo_1'),

        # Friends collage
        FriendsCollagePage(   page=43),
                              # really a two-page spread
    ]

    @classmethod
    def pages(cls):
        return cls._pages

    @classmethod
    def get_page(cls, page):
        for page_instance in cls.pages():
            if page_instance.page == page:
                return page_instance
        return None


v1_api = Api(api_name='v1')
v1_api.register(PageResource())