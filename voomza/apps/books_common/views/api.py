from __future__ import division, print_function, unicode_literals
from django.conf import settings
from django.http import Http404
from rest_framework import generics
from rest_framework.decorators import api_view
from voomza.apps.account.views.api import UserResourceByFbIdMixin
from voomza.apps.books_common.models import GenericBook
from voomza.apps.books_common.serializers import GenericBookSerializer
from voomza.apps.core.views.api import task_progress


class BookList(generics.ListAPIView, UserResourceByFbIdMixin):
    """
    Returns GenericBooks belonging to this user
    """
    model = GenericBook
    serializer_class = GenericBookSerializer

    # Don't need to do anything else, UserResourceByFbIdMixin takes care of it


class BookDetail:
    pass



class FriendBookList(generics.ListAPIView, UserResourceByFbIdMixin):
    """
    Returns books that belong to the user's friends
    """
    model = GenericBook
    serializer_class = GenericBookSerializer
    # permission_classes = (IsOwner,)

    def get_queryset(self):
        return super(FriendBookList, self).get_queryset().filter(owner__profile__isnull=False)


@api_view(['GET'])
def book_progress(request, book_type, format=None):
    """
    Look up the name of the task corresponding to the given book
    and return `task_progress` for that task
    """
    if book_type in settings.ALL_BOOKS:
        # The name of the book's task is "book_type.['run_task']",
        #   e.g. "2012yearbook.tasks.run_book"
        task_name = '%s.%s' % (book_type, settings.ALL_BOOKS[book_type]['run_task'])
        return task_progress(request, task_name, format)
    else:
        raise Http404
