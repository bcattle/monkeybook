from __future__ import division, print_function, unicode_literals
from django.conf import settings
from voomza.lib.django_facebook.utils import get_class_from_string

# ALL_BOOKS = {
#     'yearbook': {
#         'title':       '2012 Yearbook',
#         'cover':      'img/book_icon_144.png'
#         'prefix':       'voomza.apps.yearbook2012',
#         'settings':       'settings',
#         'run_task':       'tasks.run_book',
#         'page_factory':   'page_factory.Yearbook2012PageFactory',
#         'url_prefix':   'yearbook',
#     },
# }

def get_book_task(book_name):
    """
    Runs the `run_task` to generate the book
    with the specified name
    """
    book_config = settings.ALL_BOOKS[book_name]
    task = get_class_from_string('.'.join((book_config['prefix'], book_config['run_task'],)))
    return task

def get_page_factory(book_name):
    book_config = settings.ALL_BOOKS[book_name]
    page_factory = get_class_from_string('.'.join((book_config['prefix'], book_config['page_factory'],)))
    return page_factory

def get_book_settings(book_name):
    book_config = settings.ALL_BOOKS[book_name]
    book_settings = get_class_from_string('.'.join((book_config['prefix'], book_config['settings'],)))
    return book_settings
