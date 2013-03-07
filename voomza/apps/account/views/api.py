from rest_framework import generics
from voomza.apps.account.models import FacebookUser
from voomza.apps.account.serializers import FacebookUserSerializer


class FriendList(generics.ListAPIView):
    model = FacebookUser
    serializer_class = FacebookUserSerializer

