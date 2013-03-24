from django.conf.urls import patterns, include, url
from django.contrib.auth.views import logout
from django.views.generic.base import TemplateView

urlpatterns = patterns('',
    url(r'^logout/$', logout, {'next_page': '/'}, name='logout'),
)

