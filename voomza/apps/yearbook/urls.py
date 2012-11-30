from django.conf.urls import patterns, include, url
from views import *
from ajax2 import v1_api


urlpatterns = patterns('',
    url(r'^start/$', invite_friends_to_sign, name='invite_friends_to_sign'),
    url(r'^vote/$', vote_badges, name='vote_badges'),
    url(r'^sign/$', sign_friends, name='sign_friends'),
    url(r'^done/$', teaser, name='teaser'),
    (r'^api/', include(v1_api.urls)),
)
