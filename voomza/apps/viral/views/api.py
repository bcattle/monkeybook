from rest_framework import generics
from voomza.apps.viral.models import InviteRequestSent
from voomza.apps.viral.serializers import InviteRequestSentSerializer


class InviteSentList(generics.ListCreateAPIView):
    model = InviteRequestSent
    serializer_class = InviteRequestSentSerializer

class InviteSentDetail(generics.CreateAPIView):
    model = InviteRequestSent
    serializer_class = InviteRequestSentSerializer

