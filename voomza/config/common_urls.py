from django.conf.urls import patterns, include, url
#from dajaxice.core import dajaxice_autodiscover, dajaxice_config
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

# Enable admin
from django.contrib import admin
admin.autodiscover()

# Enable dajaxice
#dajaxice_autodiscover()

common_urls = patterns('',
    url(r'', include('account.urls')),
    url(r'', include('core.urls')),
    url(r'', include('yearbook.urls')),
    url(r'', include('store.urls')),
#    url(r'^backend/', include('backend.urls')),
    # Admin
    url(r'^admin/', include(admin.site.urls)),
    # Autosuggest
#    url(r'^%s/' % settings.SELECTABLE_MEDIA_PREFIX, include('selectable.urls')),
    # General ajax
#    url(dajaxice_config.dajaxice_url, include('dajaxice.urls')),
    # Django-Facebook
    (r'^facebook/', include('django_facebook.urls')),
    (r'^accounts/', include('django_facebook.auth_urls')),
)

# Static files, needed by dajaxice
common_urls += staticfiles_urlpatterns()
