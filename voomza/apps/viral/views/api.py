from rest_framework import generics
from voomza.apps.viral.models import SentInvite
from voomza.apps.viral.serializers import SentInviteSerializer


class InviteSentList(generics.ListCreateAPIView):
    model = SentInvite
    serializer_class = SentInviteSerializer

class InviteSentDetail(generics.CreateAPIView):
    model = SentInvite
    serializer_class = SentInviteSerializer

