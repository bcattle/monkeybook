from django.conf import settings
from django.conf.urls import patterns, include, url

# Enable admin
#from django.contrib import admin
#admin.autodiscover()

# Enable dajaxice
#from dajaxice.core import dajaxice_autodiscover
#dajaxice_autodiscover()

common_urls = patterns('',
    url(r'', include('core.urls')),
    url(r'', include('signup.urls')),
    # Admin
#    url(r'^admin/', include(admin.site.urls)),
    # Autosuggest
#    url(r'^%s/' % settings.SELECTABLE_MEDIA_PREFIX, include('selectable.urls')),
    # General ajax
#    url(r'^%s/' % settings.DAJAXICE_MEDIA_PREFIX, include('dajaxice.urls')),
    # Django-Facebook
    (r'^facebook/', include('django_facebook.urls')),
    (r'^accounts/', include('django_facebook.auth_urls')),
)
