from tastypie.resources import ModelResource
from tastypie.authorization import Authorization
from tastypie.authentication import SessionAuthentication
from tastypie.api import Api
from voomza.apps.account.models import FacebookUser
from voomza.apps.yearbook.models import InviteRequestSent


class FriendResource(ModelResource):
    """
    Returns a paginated list of the user's friends,
    in order of "top friends" relevance
    """
    class Meta:
        queryset = FacebookUser.objects.all()
        list_allowed_methods = ['get']
        detail_allowed_methods = []
        fields = ['facebook_id', 'name', 'pic_square']      # 'top_friends_order'
        include_resource_uri = False
        filtering = {
            'name': ('icontains'),
        }
        authentication = SessionAuthentication()
        authorization = Authorization()

        # TODO: filter on name for autosuggest

    def get_object_list(self, request):
        # This limits results to the current user
        #  so no need for `apply_authorization_limits`
        return FacebookUser.objects.get_friends_for_user(request)


class InviteRequestSentResource(ModelResource):
    class Meta:
        queryset = InviteRequestSent.objects.all()
        allowed_methods = ['post']
        fields = ['facebook_user', 'request_id']
        authentication = SessionAuthentication()
        authorization = Authorization()

    def hydrate_user(self, bundle):
        bundle.data['user'] = bundle.request.user
        return bundle


class YearbookSignResource(ModelResource):
    """
    Pulls people who have signed my yearbook,
    handles POST when I sign others' yearbooks
    """
    class Meta:
#        allowed_methods = ['get', 'post']
        allowed_methods = ['get']
        authentication = SessionAuthentication()


class YearbookToSignResource(ModelResource):
    """
    Pulls recommended yearbooks I should sign
    """
    class Meta:
        allowed_methods = ['get']
        authentication = SessionAuthentication()

    def build_filters(self, filters=None):
        """
        Handle the 'i_signed' filter
        """
        if filters is None:
            filters = {}

        orm_filters = super(YearbookToSignResource, self).build_filters(filters)

        if "q" in filters:
            sqs = SearchQuerySet().auto_query(filters['q'])

            orm_filters["pk__in"] = [i.pk for i in sqs]

        return orm_filters


v1_api = Api(api_name='v1')
v1_api.register(FriendResource())
#v1_api.register(InviteResource())
#v1_api.register(BadgeVoteResource())
v1_api.register(YearbookSignResource())
v1_api.register(YearbookToSignResource())
