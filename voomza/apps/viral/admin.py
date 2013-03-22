from django.contrib import admin
from voomza.apps.viral.models import SentInvite


class SentInviteAdmin(admin.ModelAdmin):
    list_display = ('from_user', 'to_facebook_user', 'request_id', 'sent_at',
                    'accepted_at')

admin.site.register(SentInvite, SentInviteAdmin)
