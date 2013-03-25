from django.conf.urls import patterns, include, url
from django.views.generic.base import TemplateView
from monkeybook.apps.store.views import checkout

urlpatterns = patterns('',
    url(r'^hardcover/$', TemplateView.as_view(template_name='hardcover_feature.html'), name='hardcover_feature'),
    url(r'^standard/$', TemplateView.as_view(template_name='standard_feature.html'), name='standard_feature'),
    url(r'^checkout/$', checkout, name='checkout'),
)
