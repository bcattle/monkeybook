from django.conf.urls import patterns, include, url
from django.conf import settings
from views import *
from ajax import v1_api

urlpatterns = patterns('',
    url(r'^start/$', invite_friends_to_sign, name='invite_friends_to_sign'),
    url(r'^sign/$', sign_friends, name='sign_friends'),
    url(r'^yearbook/(?P<hash>[a-fA-F0-9]{%d})/$' % settings.YEARBOOK_HASH_LENGTH, yearbook, name='yearbook'),
    url(r'^yearbook/$', yearbook_no_hash, name='yearbook_no_hash'),
    (r'^api/', include(v1_api.urls)),
)
