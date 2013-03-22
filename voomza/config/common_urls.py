from __future__ import division, print_function, unicode_literals
from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from rest_framework.urlpatterns import format_suffix_patterns
from voomza.apps.books_common import short_url
from voomza.apps.books_common.views import api as books_common_api
from voomza.apps.account.views import api as account_api
from voomza.apps.core.views import api as core_api
from voomza.apps.books_common.views.client import view_book_short_url

# Enable admin
from django.contrib import admin

admin.autodiscover()

# Prefixed with '/api/user/124143423/books/yearbook2012/1/'
book_detail_urls = patterns('',
    url(r'^$', , name='book-detail'),
    url(r'^friends/$', , name='book-friends-list'),
    url(r'^page/$', ,                       name='book-page-list'),
    url(r'^page/(?P<page_num>[0-9]+)/$', ,  name='book-page-detail'),
    url(r'^page/(?P<page_num>[0-9]+)/next/$', ,                         name='book-page-next-list'),
    url(r'^page/(?P<page_num>[0-9]+)/next/(?P<image_index>[0-9]+)/$', , name='book-page-next-detail'),
)

# Prefixed with '/api/user/124143423/'
user_api_urls = patterns('',
    url(r'^friends/$',              account_api.FriendList.as_view(),          name='friend-list'),
    url(r'^friends/not-in-app/$',   account_api.FriendNotInAppList.as_view(),  name='friend-not-inapp-list'),
    url(r'^friends/in-app/$',       account_api.FriendInAppList.as_view(),     name='friend-inapp-list'),
    url(r'^friends/books/$',        books_common_api.FriendBookList.as_view(), name='friend-books-list'),

    url(r'^friends/progress/$',            core_api.task_progress, {'task_name': ''}, name=''),
    # url(r'^friends/not-in-app/progress/$', core_api.task_progress, {'task_name': ''}, name=''),
    # url(r'^friends/in-app/progress/$',     core_api.task_progress, {'task_name': ''}, name=''),

    url(r'^books/$', books_common_api.BookList.as_view(), name='book-list'),
    # url(r'^books/(?P<book_type>[a-zA-Z0-9]+)/$', , name='book-bytype-list'),
    url(r'^books/(?P<book_type>[a-zA-Z0-9]+)/progress/$', books_common_api.book_progress, name='book-bytype-progress'),
    url(r'^books/(?P<book_type>[a-zA-Z0-9]+)/(?P<pk>[0-9]+)/', include(book_detail_urls)),
)

# Prefixed with '/api/
api_urls = patterns('',
    # url(r'^$', core_api.api_root),
    url(r'^user/(?P<fb_id>[0-9]+)/', include(user_api_urls)),
)

api_urls = format_suffix_patterns(api_urls, allowed=['json', 'html'])

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
    # Django REST login/logout
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    # API URLs
    url(r'^api/', include(api_urls)),

    # Shortened urls, here after everything else
    url(r'^(?P<slug>[%s]+)/$' % short_url.DEFAULT_ALPHABET, view_book_short_url),
)

# Static files, needed by dajaxice
common_urls += staticfiles_urlpatterns()
