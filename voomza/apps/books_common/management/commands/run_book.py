from __future__ import division, print_function, unicode_literals
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from voomza.apps.books_common.books import get_book_task


class Command(BaseCommand):
    args = '<book> <username>'
    help = 'Runs the specified book for a user. Leaves the original in place'

    def handle(self, *args, **options):
        book_name = args[0]
        username = args[1]

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            print('No user found with username <%s>' % username)
            return

        task = get_book_task(book_name)
        task.apply_async(kwargs={'user': user})

        print('Enqueued book "%s" username <%s>' % (book_name, username))
