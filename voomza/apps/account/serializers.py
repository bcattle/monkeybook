from rest_framework import serializers
from voomza.apps.account.models import FacebookUser, FacebookFriend


class FacebookUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = FacebookUser
        fields = ('facebook_id', 'name', 'pic_square',)


class FacebookFriendSerializer(serializers.ModelSerializer):
    class Meta:
        model = FacebookFriend
        fields = ('facebook_user', 'top_friends_order',)
        depth = 1

