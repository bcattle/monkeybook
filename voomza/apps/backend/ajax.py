from django.conf.urls import url
from tastypie import fields
from tastypie.bundle import Bundle
from tastypie.exceptions import NotFound
from tastypie.http import HttpNotFound
from tastypie.resources import Resource
from tastypie.authorization import Authorization
from tastypie.authentication import SessionAuthentication
from tastypie.api import Api
from tastypie.utils.urls import trailing_slash
from voomza.apps.backend.serializers import DjangoTemplateSerializer
from voomza.apps.yearbook.pages import *


class PageResource(Resource):
    page = fields.IntegerField(attribute='page', readonly=True)
    page_content = fields.CharField(readonly=True)

    factory = YearbookPageFactory()

    class Meta:
        resource_name = 'yearbookpage'
        object_class = YearbookPage
        limit = 5
        list_allowed_methods = ['get']
        detail_allowed_methods = ['get']
        authentication = SessionAuthentication()
        authorization = Authorization()
#        serializer = DjangoTemplateSerializer()

    def prepend_urls(self):
        # Add a url for the `next` method
        return [
            url(r"^(?P<resource_name>%s)/(?P<%s>\w[\w/-]*)/next/(?P<next_index>[\d]+)%s$"
                % (self._meta.resource_name, self._meta.detail_uri_name, trailing_slash()),
                self.wrap_view('get_next'), name="api_get_next"),
            url(r"^(?P<resource_name>%s)/(?P<%s>\w[\w/-]*)/next/(?P<next_index>[\d]+)/(?P<photo_index>[\d]+)%s$"
                % (self._meta.resource_name, self._meta.detail_uri_name, trailing_slash()),
                    self.wrap_view('get_next'), name="api_get_next_photo"),
        ]

    def detail_uri_kwargs(self, bundle_or_obj):
        """
        Given a Bundle or an object,
        returns the extra kwargs needed to generate a detail URI
        """
        kwargs = {}
        if isinstance(bundle_or_obj, Bundle):
            kwargs['pk'] = bundle_or_obj.obj.page
        else:
            kwargs['pk'] = bundle_or_obj.page
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
        return self.factory.pages()

    
    def obj_get(self, request=None, **kwargs):
        """
        Fetches an individual object on the resource.
        If the object can not be found this should raise a NotFound exception
        """
        try:
            page = self.factory.get_page(int(kwargs['pk']))
        except ValueError:
            raise NotFound
        if not page:
            raise NotFound
        return page


    def dehydrate(self, bundle):
        user = bundle.request.user
        bundle.data['template'] = bundle.obj.template
        bundle.data['page_content'] = bundle.obj.get_page_content(user)
        return bundle


    def get_next(self, request, next_index, photo_index=None, **kwargs):
        print 'next_index: %s' % next_index
        self.method_check(request, allowed=['get'])
        self.is_authenticated(request)
        self.throttle_check(request)

        page = self.obj_get(**kwargs)
        page.set_user(request.user)
        if hasattr(page, 'get_next_image'):
            try:
                if photo_index:
                    # urls start counting at 1
                    next_data = page.get_next_image(int(next_index) - 1, int(photo_index) - 1)
                else:
                    next_data = page.get_next_image(int(next_index) - 1)

                data = {
                    'objects': next_data,
                }

                self.log_throttled_access(request)
                return self.create_response(request, data)
            except ValueError: pass
        return HttpNotFound()


v1_api = Api(api_name='v1')
v1_api.register(PageResource())