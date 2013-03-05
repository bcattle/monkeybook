from __future__ import division, print_function, unicode_literals
from django.conf import settings
from django.conf.urls import url
from django.template.context import RequestContext
from django.template.loader import render_to_string
from tastypie import fields
from tastypie.bundle import Bundle
from tastypie.exceptions import NotFound
from tastypie.http import HttpNotFound
from tastypie.resources import Resource
from tastypie.authorization import ReadOnlyAuthorization
from tastypie.authentication import Authentication, SessionAuthentication
from tastypie.utils.urls import trailing_slash
from voomza.apps.backend.progress import YearbookProgress
from voomza.apps.yearbook.pages import *


class YearbookProgressResource(Resource):
    """
    Returns the status of the user's yearbook
    running if async in session, or done if
    async done or model exists in db
    """
    status = fields.CharField(attribute='get_status', readonly=True)
    hash = fields.CharField(attribute='get_hash', readonly=True)

    class Meta:
        resource_name = 'yearbook_progress'
        object_class = YearbookProgress
        list_allowed_methods = ['get']
        detail_allowed_methods = ['get']
        include_resource_uri = False
        authentication = SessionAuthentication()
        authorization = ReadOnlyAuthorization()

    def obj_get_list(self, request=None, **kwargs):
        """
        Runs before filters
        """
        return self.get_object_list(request)

    def get_object_list(self, request):
        """
        Runs after filters
        """
        return [self.obj_get(request=request)]

    def obj_get(self, request=None, **kwargs):
        """
        Fetches an individual object on the resource.
        If the object can not be found this should raise a NotFound exception
        """
        progress = YearbookProgress(request=request)
        return progress


class PageResource(Resource):
    page = fields.IntegerField(attribute='page', readonly=True)
    page_content = fields.CharField(readonly=True)

    class Meta:
        resource_name = 'yearbookpage'
        object_class = YearbookPage
        limit = 2
        list_allowed_methods = ['get']
        detail_allowed_methods = ['get']
        authentication = Authentication()       # open to the world!
        authorization = ReadOnlyAuthorization()
        detail_uri_name = 'page'

    def prepend_urls(self):
        # Add a url for the `next` method
        return [
            url(r"^(?P<resource_name>%s)/(?P<hash>[a-fA-F0-9]{%d})%s$"
                % (self._meta.resource_name, settings.YEARBOOK_HASH_LENGTH, trailing_slash()),
                    self.wrap_view('dispatch_list'), name="api_dispatch_list"),

            url(r"^(?P<resource_name>%s)/(?P<hash>[a-fA-F0-9]{%d})/(?P<%s>\w[\w/-]*)/next/(?P<next_index>[\d]+)%s$"
                % (self._meta.resource_name, settings.YEARBOOK_HASH_LENGTH, self._meta.detail_uri_name, trailing_slash()),
                    self.wrap_view('get_next'), name="api_get_next"),

            url(r"^(?P<resource_name>%s)/(?P<hash>[a-fA-F0-9]{%d})/(?P<%s>\w[\w/-]*)/next/(?P<next_index>[\d]+)/(?P<photo_index>[\d]+)%s$"
                % (self._meta.resource_name, settings.YEARBOOK_HASH_LENGTH, self._meta.detail_uri_name, trailing_slash()),
                    self.wrap_view('get_next'), name="api_get_next_photo"),

            url(r"^(?P<resource_name>%s)/(?P<hash>[a-fA-F0-9]{%d})/(?P<%s>\w[\w/-]*)%s$"
            % (self._meta.resource_name, settings.YEARBOOK_HASH_LENGTH, self._meta.detail_uri_name, trailing_slash()),
                self.wrap_view('dispatch_detail'), name="api_dispatch_detail"),

        ]

    def detail_uri_kwargs(self, bundle_or_obj):
        """
        Given a Bundle or an object,
        returns the extra kwargs needed to generate a detail URI
        """
        kwargs = {}
        if isinstance(bundle_or_obj, Bundle):
            kwargs[self.Meta.detail_uri_name] = bundle_or_obj.obj.page
            kwargs['hash'] = bundle_or_obj.obj.yearbook.hash
        else:
            kwargs[self.Meta.detail_uri_name] = bundle_or_obj.page
            kwargs['hash'] = bundle_or_obj.yearbook.hash
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
        factory = YearbookPageFactory(user=request.user)
        return factory.pages()

    
    def obj_get(self, request=None, **kwargs):
        """
        Fetches an individual object on the resource.
        If the object can not be found this should raise a NotFound exception
        """
        factory = YearbookPageFactory(hash=kwargs['hash'])
        page = None
        try:
            page = factory.get_page(int(kwargs[self.Meta.detail_uri_name]))
        except ValueError: pass
        if not page:
            raise NotFound("Couldn't find an instance of '%s' which matched page='%s'." % (self.__class__.__name__, kwargs[self.Meta.detail_uri_name]))
        return page


    def dehydrate(self, bundle):
        context = bundle.obj.get_page_content()
        # Render the template
        template = PAGE_TEMPLATE_DIR + bundle.obj.template
#        bundle.data['page_content'] = render(bundle.request, template, context).strip()
        bundle.data['page_content'] = render_to_string(template, context, RequestContext(bundle.request)).strip()
        return bundle


    def get_next(self, request, next_index, photo_index=None, **kwargs):
        print('next_index: %s' % next_index)
        self.method_check(request, allowed=['get'])
        self.is_authenticated(request)
        self.throttle_check(request)

        page = self.obj_get(**kwargs)
        if hasattr(page, 'get_next_image'):
            try:
                if photo_index:
                    # These return full template context including the new image
                    # urls start counting at 1
                    next_data = page.get_next_data(int(next_index) - 1, int(photo_index) - 1)
                else:
                    next_data = page.get_next_data(int(next_index) - 1)

                template = PAGE_TEMPLATE_DIR + page.template
                data = {
                    'page_content': render(request, template, next_data).strip()
                }

                self.log_throttled_access(request)
                return self.create_response(request, data)
            except ValueError: pass
        return HttpNotFound()


# API registered in yearbook/ajax.py
#v1_api = Api(api_name='v1')
#v1_api.register(PageResource())
#v1_api.register(YearbookProgressResource())
