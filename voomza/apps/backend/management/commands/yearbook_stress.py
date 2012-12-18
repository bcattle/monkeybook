import itertools
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from backend.tasks import run_yearbook

class Command(BaseCommand):
    args = '<num yearbooks to run>'
    help = 'Fires the `run_yearbook` task a specified number of times.'

    def handle(self, *args, **options):
        num = args[0]

        usernames = [
            'bcattle'
        ]
        users = itertools.cycle((User.objects.get(username=username) for username in usernames))

        for n in range(int(num)):
            run_yearbook.delay(users.next())

        print 'Enqueued `run_yearbook` %s times' % num
