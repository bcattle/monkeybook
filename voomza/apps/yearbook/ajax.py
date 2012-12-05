from tastypie.resources import ModelResource, fields
from tastypie.authorization import Authorization
from tastypie.authentication import SessionAuthentication
from tastypie.api import Api
from voomza.apps.account.models import FacebookUser
from voomza.apps.yearbook.models import InviteRequestSent, YearbookSign


class FriendResource(ModelResource):
    """
    Returns a paginated list of the user's friends,
    in order of "top friends" relevance
    """
    class Meta:
        queryset = FacebookUser.objects.all()
        list_allowed_methods = ['get']
        detail_allowed_methods = ['get']
        fields = ['facebook_id', 'name', 'pic_square']
        filtering = {
            'name': ('icontains'),
        }
        authentication = SessionAuthentication()
        authorization = Authorization()

    def get_object_list(self, request):
        # This limits results to the current user
        #  so no need for `apply_authorization_limits`
        return FacebookUser.objects.get_friends_for_user(request)


class FriendWhoHasntSignedResource(FriendResource):
    def get_object_list(self, request):
        return FacebookUser.objects.get_friends_who_havent_signed(request)


class InviteSentResource(ModelResource):
    class Meta:
        queryset = InviteRequestSent.objects.all()
        list_allowed_methods = ['post', 'patch']
        detail_allowed_methods = ['put']            # Implied by PATCH
        fields = ['to_facebook_user', 'request_id']
        authentication = SessionAuthentication()
        authorization = Authorization()

    def hydrate(self, bundle):
        # Tag with the currently logged-in user
        bundle.obj.to_facebook_user_id = bundle.data['facebook_user_id']
        bundle.obj.from_user = bundle.request.user
        return bundle


class YearbookSignResource(ModelResource):
    """
    Pulls signs from people who have signed my yearbook,
    handles POST when I sign others' yearbooks
    """
    from_facebook_user = fields.ForeignKey(FriendResource, 'from_facebook_user', full=True)

    class Meta:
        queryset = YearbookSign.objects.all()
        allowed_methods = ['get', 'post']
        fields = ['from_facebook_user', 'text', 'read']
        limit = 6
        authentication = SessionAuthentication()
        authorization = Authorization()

    def get_object_list(self, request):
        return YearbookSign.objects.get_in_sign_order(user=request.user)

    def obj_create(self, bundle, request=None, **kwargs):
        # TODO: see if there is a pending "sign my yearbook" request, if there is - delete it

        # TODO: make sure the user is actually friends with the person they're signing

        return super(YearbookSignResource, self).obj_create(bundle, request, user=request.user)

    def hydrate(self, bundle):
        # Tag with the currently logged-in user
        bundle.obj.from_facebook_user_id = bundle.request.user.profile.facebook_id
        bundle.obj.to_facebook_user_id = bundle.data['to_facebook_user_id']
        return bundle

    def dehydrate(self, bundle):
        # Add the `can_sign` field
        bundle.data['can_sign'] = bundle.obj.can_sign and True
        return bundle


class YearbookToSignResource(ModelResource):
    """
    Users whose yearbooks I should sign,
    these are rendered in right column of page
    --> These *do not include* anyone who's signed me
    """
    class Meta:
        queryset = FacebookUser.objects.all()
        list_allowed_methods = ['get']
        detail_allowed_methods = []
        fields = ['facebook_id', 'name', 'pic_square']      # 'top_friends_order'
        include_resource_uri = False
        limit = 6
        filtering = {
            'name': ('icontains'),
        }
        authentication = SessionAuthentication()
        authorization = Authorization()

    def get_object_list(self, request):
        return FacebookUser.objects.get_yearbooks_to_sign(request.user)


class UnsignedYearbookResource(YearbookToSignResource):
    """
    Pulls users whose yearbooks I have not signed
    Used in typeahead search
    --> ** includes people who signed me **
    """
    def get_object_list(self, request):
        return FacebookUser.objects.get_yearbooks_i_didnt_sign(request.user)


class SignedYearbookResource(YearbookToSignResource):
    """
    Pulls users whose yearbooks I have already signed
    Used in typeahead to remind user
    if they're looking for a friend they already signed
    """
    def get_object_list(self, request):
        return FacebookUser.objects.get_yearbooks_i_signed(request.user)


v1_api = Api(api_name='v1')
v1_api.register(FriendResource())
v1_api.register(FriendWhoHasntSignedResource())
v1_api.register(InviteSentResource())
v1_api.register(YearbookSignResource())
v1_api.register(YearbookToSignResource())
v1_api.register(UnsignedYearbookResource())
v1_api.register(SignedYearbookResource())
