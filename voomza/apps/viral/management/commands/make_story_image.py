from __future__ import division, print_function, unicode_literals
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    args = '<username> <page>'
    help = 'Generates a story image from a page of the specified user\'s yearbook.' \
           'Image is saved to the current directory.'

    def handle(self, *args, **options):
        username = args[0]
        page = args[1]

        # Get the user
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            print('No user found with username <%s>' % username)
            return

        # Get the user's yearbook

        # Dereference the image in question

        # Run the task to generate the output image

        # Enqueue the task to create the image
        make_story_image_async = make_story_image.apply_async(kwargs={'photo_instance': url})

        print('Enqueued make_story_image for username <%s>, page %d' % (username, page))

        saved_url = make_story_image_async.get()

        print('Saved story image to <%s>' % saved_url)
