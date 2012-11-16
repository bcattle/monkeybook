from django.conf.urls import patterns, include, url
from voomza.config.common_urls import *

urlpatterns = patterns('',
    url(r'', include(common_urls)),
)

