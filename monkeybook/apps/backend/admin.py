from django.contrib import admin
from monkeybook.apps.backend.models import FacebookPhoto, PhotoRankings, Yearbook


class FacebookPhotoAdmin(admin.ModelAdmin):
    search_fields = ('facebook_id',)
    list_display = ('facebook_id', 'fb_url', 'height', 'width', 'is_portrait',
                    'is_landscape', 'is_square', 'caption', 'comments', 'created')

class YearbookAdmin(admin.ModelAdmin):
    list_display = ('rankings', 'hash', 'run_time', 'created')

class PhotoRankingsAdmin(admin.ModelAdmin):
    list_display = ('user', 'top_photos', 'group_shots', 'top_albums_photos',
                    'top_albums_ranked', 'back_in_time', 'top_friends_ids',
                    'top_friends_photos', 'top_posts'
    )

admin.site.register(FacebookPhoto, FacebookPhotoAdmin)
admin.site.register(PhotoRankings, PhotoRankingsAdmin)
admin.site.register(Yearbook, YearbookAdmin)
