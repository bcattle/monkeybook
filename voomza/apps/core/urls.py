from django.conf.urls import patterns, include, url
from django.views.generic.base import TemplateView
from voomza.apps.core.views import homepage

urlpatterns = patterns('',
    url(r'^$', homepage, name='homepage'),
)

