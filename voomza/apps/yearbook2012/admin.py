from django.contrib import admin
from voomza.apps.yearbook2012.models import Yearbook, PhotoRankings


class YearbookAdmin(admin.ModelAdmin):
    list_display = ('rankings', 'hash', 'run_time', 'created')

class PhotoRankingsAdmin(admin.ModelAdmin):
    list_display = ('user', 'top_photos', 'group_shots', 'top_albums_photos',
                    'top_albums_ranked', 'back_in_time', 'top_friends_ids',
                    'top_friends_photos', 'top_posts'
    )

admin.site.register(Yearbook, YearbookAdmin)
admin.site.register(PhotoRankings, PhotoRankingsAdmin)
