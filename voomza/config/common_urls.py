from __future__ import division, print_function, unicode_literals
from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

# Enable admin
from django.contrib import admin
admin.autodiscover()

# Enable dajaxice
#dajaxice_autodiscover()

common_urls = patterns('',
    url(r'', include('account.urls')),
    url(r'', include('core.urls')),
    url(r'', include('books_common.urls')),
    url(r'', include('checkout.urls')),
    # Admin
    url(r'^admin/', include(admin.site.urls)),
    # Django-Facebook
    (r'^facebook/', include('django_facebook.urls')),
    (r'^accounts/', include('django_facebook.auth_urls')),
)

# Static files, needed by dajaxice
common_urls += staticfiles_urlpatterns()
