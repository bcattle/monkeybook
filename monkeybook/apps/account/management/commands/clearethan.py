from django.core.management.base import NoArgsCommand
from django.contrib.auth.models import User


class Command(NoArgsCommand):
#    help = 'Deletes any user accounts having the email `bryan.cattle@gmail.com`'
    help = 'Deletes any user accounts having the username `ethansmontoya`'

    def handle_noargs(self, **options):
    #        users = User.objects.filter(email__iexact='bryan.cattle@gmail.com')
        users = User.objects.filter(username='ethansmontoya')
        if users:
            print '%d user object found' % len(users)
            users.delete()
            print 'Deleted.'
