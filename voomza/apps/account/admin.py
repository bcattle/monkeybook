from django.contrib import admin
from voomza.apps.account.models import UserProfile, FamilyConnection, FacebookUser, FacebookFriend


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'facebook_id', 'locale', 'relationship_status', 'significant_other_id', 'access_token')

class FamilyConnectionAdmin(admin.ModelAdmin):
    list_display = ('owner', 'facebook_id', 'relationship')

class FacebookUserAdmin(admin.ModelAdmin):
    search_fields = ('facebook_id', 'name')
    list_display = ('facebook_id', 'name', 'pic_square')

class FacebookFriendAdmin(admin.ModelAdmin):
    list_display = ('owner', 'facebook_user', 'top_friends_order')
    ordering = ('owner', '-top_friends_order')


admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(FamilyConnection, FamilyConnectionAdmin)
admin.site.register(FacebookUser, FacebookUserAdmin)
admin.site.register(FacebookFriend, FacebookFriendAdmin)
