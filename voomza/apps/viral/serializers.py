from rest_framework import serializers
from voomza.apps.viral.models import InviteRequestSent


class InviteRequestSentSerializer(serializers.ModelSerializer):
    class Meta:
        model = InviteRequestSent
        fields = ('to_facebook_user', 'request_id',)
