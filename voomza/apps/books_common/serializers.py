from rest_framework import serializers
from voomza.apps.books_common.models import GenericBook


class GenericBookSerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length=200)
    cover = serializers.CharField(max_length=1000)

    class Meta:
        model = GenericBook
        fields = ('title', 'cover',)
