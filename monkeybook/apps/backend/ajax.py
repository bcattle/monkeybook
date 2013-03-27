from django.conf.urls import url
from django.shortcuts import render
from django.template.context import RequestContext
from django.template.loader import render_to_string
from tastypie import fields
from tastypie.bundle import Bundle
from tastypie.exceptions import NotFound
from tastypie.http import HttpNotFound
from tastypie.resources import Resource
from tastypie.authorization import ReadOnlyAuthorization, DjangoAuthorization
from tastypie.authentication import Authentication, SessionAuthentication
from tastypie.utils.urls import trailing_slash
from monkeybook.apps.backend import short_url
from monkeybook.apps.backend.progress import YearbookProgress
from monkeybook.apps.yearbook.pages import *


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
        print 'obj_get yearbook progress ' + str(kwargs)
        progress = YearbookProgress(request=request)
        return progress

# Empty class to make shit work.
class YearbookUpdate(object):
	def __init__(self):
		return
	
data = [YearbookUpdate()]
class YearbookUpdateResource(Resource):
    """
    Update yearbook
    """
    class Meta:
        resource_name = 'yearbook_update'
        object_class = YearbookUpdate
        list_allowed_methods = ['post']
        detail_allowed_methods = ['post']
        authentication = Authentication()       # open to the world!
        authorization = DjangoAuthorization()

    def get_resource_uri(self, bundle_or_obj):
    	return 'yearbook_update'
 
    def get_object_list(self, request):
        # inner get of object list... this is where you'll need to
        # fetch the data from what ever data source
        return [YearbookUpdate()]
 
    def obj_get_list(self, request = None, **kwargs):
        # outer get of object list... this calls get_object_list and
        # could be a point at which additional filtering may be applied
        return self.get_object_list(request)
 
    def obj_get(self, request = None, **kwargs):
        # get one object from data source
        return YearbookUpdate()
    
    def obj_create(self, bundle, request = None, **kwargs):
        # create a new row
        # hash, page, index, id
        print 'obj_create ' + str(kwargs) + ' ' + str(bundle)
        try:
            page = YearbookPageFactory(user=request.user, hash=bundle.data['hash']
            						   ).get_page(int(bundle.data['page']))
            						  
            print page
        except Exception as e: 
        	print e
        if not page:
            raise NotFound("Couldn't find an instance of '%s' which matched page='%s'." % (self.__class__.__name__, bundle.data['page']))
        
        page.update_image(int(bundle.data['index']), int(bundle.data['id']))
        bundle.obj = YearbookUpdate()
        
        bundle = self.full_hydrate(bundle)
        return bundle
  

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
            url(r"^(?P<resource_name>%s)/(?P<hash>[%s]+)%s$"
                % (self._meta.resource_name, short_url.DEFAULT_ALPHABET, trailing_slash()),
                    self.wrap_view('dispatch_list'), name="api_dispatch_list"),

            url(r"^(?P<resource_name>%s)/(?P<hash>[%s]+)/(?P<%s>\w[\w/-]*)/next/(?P<next_index>[\d]+)%s$"
                % (self._meta.resource_name, short_url.DEFAULT_ALPHABET, self._meta.detail_uri_name, trailing_slash()),
                    self.wrap_view('get_next'), name="api_get_next"),

            url(r"^(?P<resource_name>%s)/(?P<hash>[%s]+)/(?P<%s>\w[\w/-]*)/next/(?P<next_index>[\d]+)/(?P<photo_index>[\d]+)%s$"
                % (self._meta.resource_name, short_url.DEFAULT_ALPHABET, self._meta.detail_uri_name, trailing_slash()),
                    self.wrap_view('get_next'), name="api_get_next_photo"),

            url(r"^(?P<resource_name>%s)/(?P<hash>[%s]+)/(?P<%s>\w[\w/-]*)%s$"
            % (self._meta.resource_name, short_url.DEFAULT_ALPHABET, self._meta.detail_uri_name, trailing_slash()),
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
        print 'Getting objects for ' + str(kwargs)
        factory = YearbookPageFactory(hash=kwargs['hash'])
        page = None
        try:
            page = factory.get_page(int(kwargs[self.Meta.detail_uri_name]))
        except ValueError: pass
        if not page:
            raise NotFound("Couldn't find an instance of '%s' which matched page='%s'." % (self.__class__.__name__, kwargs[self.Meta.detail_uri_name]))
        print 'ajax.obj_get returning' + str(page)
        #page returns page.pagecontent() which has two FacebookPhoto objects.
        return page


    def dehydrate(self, bundle):
        context = bundle.obj.get_page_content()
        
        # Render the template
        template = PAGE_TEMPLATE_DIR + bundle.obj.template
#        bundle.data['page_content'] = render(bundle.request, template, context).strip()
        bundle.data['page_content'] = render_to_string(template, context, RequestContext(bundle.request)).strip()
        bundle.data['alternate_photos'] = bundle.obj.get_alternate_photos()
        return bundle


    def get_next(self, request, next_index, photo_index=None, **kwargs):
        print 'next_index: %s' % next_index
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
