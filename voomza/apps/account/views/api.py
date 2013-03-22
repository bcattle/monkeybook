from rest_framework import generics, permissions
from voomza.apps.account.models import FacebookUser
from voomza.apps.account.serializers import FacebookFriendSerializer


class UserResourceByFbIdMixin(object):
    """
    Mixin for resources belonging to the user
    indicated by the URL param `fb_id`
    """
    def get_queryset(self):
        fb_id = self.kwargs['fb_id']
        return self.model.objects.filter(owner__profile__facebook_user__id=fb_id)


class FriendList(generics.ListAPIView, UserResourceByFbIdMixin):
    model = FacebookUser
    serializer_class = FacebookFriendSerializer
    permission_classes = (IsOwner,)


class FriendInAppList(FriendList):
    def get_queryset(self):
        return super(FriendInAppList, self).get_queryset().filter(profile__isnull=False)


class FriendNotInAppList(FriendList):
    def get_queryset(self):
        return super(FriendNotInAppList, self).get_queryset().filter(profile__isnull=True)


# Permissions

class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Permissions are only allowed to the owner
        return obj.owner == request.user
