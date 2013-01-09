from django.conf.urls import patterns, include, url
from django.conf import settings
from django.views.generic.base import TemplateView
from views import *
from ajax import v1_api

urlpatterns = patterns('',
    url(r'^$', homepage, name='homepage'),
    url(r'^canvas/$', homepage, name='homepage', kwargs={'template_name': 'homepage_canvas.html'}),

    url(r'^start/$', invite_friends_to_sign, name='invite_friends_to_sign'),

#    url(r'^transfer/$', transfer_screen, name='transfer_screen'),
#    url(r'^sign/$', sign_friends, name='sign_friends'),

    url(r'^yearbook/$', yearbook_no_hash, name='yearbook_no_hash'),
    url(r'^yearbook/(?P<hash>[a-fA-F0-9]{%d})/$' % settings.YEARBOOK_HASH_LENGTH, yearbook, name='yearbook'),

    (r'^api/', include(v1_api.urls)),

    url(r'^about/$', TemplateView.as_view(template_name='about.html'), name='about_us'),
    url(r'^contact/$', TemplateView.as_view(template_name='contact.html'), name='contact'),
    url(r'^terms/$', TemplateView.as_view(template_name='terms.html'), name='terms'),
    url(r'^privacy/$', TemplateView.as_view(template_name='privacy.html'), name='privacy'),
    # Sample yearbook pages
    url(r'^sample-pages/(?P<filename>page[0-9]+\.html)$', sample_yearbook_page, name='sample_yearbook_page')
)
