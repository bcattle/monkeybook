from rest_framework import serializers
from voomza.apps.account.models import FacebookUser

class FacebookUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = FacebookUser
        fields = ('facebook_id', 'name', 'pic_square',)
