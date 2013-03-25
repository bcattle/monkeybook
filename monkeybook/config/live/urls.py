from django.conf.urls import patterns, include, url
from monkeybook.config.common_urls import *

urlpatterns = patterns('',
    url(r'', include(common_urls)),
)

