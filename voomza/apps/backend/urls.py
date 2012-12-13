from django.conf.urls import patterns, include, url
from backend.ajax import v1_api


urlpatterns = patterns('',
    (r'^api/', include(v1_api.urls)),
)
