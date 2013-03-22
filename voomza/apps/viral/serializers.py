from rest_framework import serializers
from voomza.apps.viral.models import SentInvite


class SentInviteSerializer(serializers.ModelSerializer):
    class Meta:
        model = SentInvite
        fields = ('to_facebook_user', 'request_id',)
