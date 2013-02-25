from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from backend.tasks import top_friends_fast


class Command(BaseCommand):
    args = '<username>'
    help = 'Runs the specified user\'s yearbook. Leaves the original in place'

    def handle(self, *args, **options):
        username = args[0]

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            print('No user found with username <%s>' % username)
            return

        # Run `top_friends_fast` with `run_yearbook`=True
        top_friends_fast.apply_async(kwargs={'user': user, 'run_yearbook': True})
        print('Enqueued yearbook for username <%s>' % username)
