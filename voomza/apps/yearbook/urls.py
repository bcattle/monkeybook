from django.conf.urls import patterns, include, url
from views import *
from ajax2 import v1_api


urlpatterns = patterns('',
    url(r'^start/$', invite_friends_to_sign, name='invite_friends_to_sign'),
    url(r'^sign/$', sign_friends, name='sign_friends'),
    (r'^api/', include(v1_api.urls)),
)
