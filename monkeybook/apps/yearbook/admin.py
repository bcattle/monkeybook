from django.contrib import admin
from monkeybook.apps.yearbook.models import InviteRequestSent, YearbookSign


class InviteRequestSentAdmin(admin.ModelAdmin):
    list_display = ('from_user', 'to_facebook_user', 'request_id', 'sent_at',
                    'accepted_at')


class YearbookSignAdmin(admin.ModelAdmin):
    list_display = ('from_facebook_user', 'to_facebook_user', 'text', 'created_at', 'read')


admin.site.register(InviteRequestSent, InviteRequestSentAdmin)
admin.site.register(YearbookSign, YearbookSignAdmin)
