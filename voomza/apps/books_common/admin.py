from django.contrib import admin
from voomza.apps.books_common.models import YearbookSign, FacebookPhoto


class FacebookPhotoAdmin(admin.ModelAdmin):
    search_fields = ('facebook_id',)
    list_display = ('facebook_id', 'fb_url', 'height', 'width', 'is_portrait',
                    'is_landscape', 'is_square', 'caption', 'comments', 'created')


class YearbookSignAdmin(admin.ModelAdmin):
    list_display = ('from_facebook_user', 'to_facebook_user', 'text', 'created_at', 'read')


admin.site.register(FacebookPhoto, FacebookPhotoAdmin)
admin.site.register(YearbookSign, YearbookSignAdmin)
