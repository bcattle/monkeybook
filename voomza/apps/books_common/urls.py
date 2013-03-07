from __future__ import division, print_function, unicode_literals
from django.conf.urls import patterns, include, url
from django.conf import settings
from django.views.generic.base import TemplateView
from views.client import *

urlpatterns = patterns('',
    url(r'^$',          homepage, name='homepage'),
    url(r'^canvas/$',   homepage, name='homepage_canvas', kwargs={'template_name': 'homepage_canvas.html'}),

    url(r'^start/$',    start,    name='start'),
    url(r'^running/$',  loading,  name='loading'),

    url(r'^yearbook/$', yearbook_no_hash, name='yearbook_no_hash'),
    url(r'^yearbook/(?P<hash>[a-fA-F0-9]{%d})/$' % settings.YEARBOOK_HASH_LENGTH, yearbook, name='yearbook'),

    url(r'^about/$',    TemplateView.as_view(template_name='about.html'), name='about_us'),
    url(r'^contact/$',  TemplateView.as_view(template_name='contact.html'), name='contact'),
    url(r'^terms/$',    TemplateView.as_view(template_name='terms.html'), name='terms'),
    url(r'^privacy/$',  TemplateView.as_view(template_name='privacy.html'), name='privacy'),
    # Sample yearbook pages
    url(r'^sample-pages/(?P<filename>page[0-9]+\.html)$', sample_yearbook_page, name='sample_yearbook_page')
)
