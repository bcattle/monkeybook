# http://stackoverflow.com/questions/2108824/mysql-incorrect-string-value-error-when-save-unicode-string-in-django
import MySQLdb
from django.core.management.base import NoArgsCommand
from django.conf import settings

class Command(NoArgsCommand):
    help = 'Sets all columns in django db to utf8'

    def handle_noargs(self, **options):
        host = settings.DATABASES['default']['HOST']
        port = settings.DATABASES['default']['PORT']
        passwd = settings.DATABASES['default']['PASSWORD']
        user = settings.DATABASES['default']['USER']
        dbname = settings.DATABASES['default']['NAME']

        db = MySQLdb.connect(host=host, user=user, passwd=passwd, db=dbname, port=int(port))
        cursor = db.cursor()

        cursor.execute("ALTER DATABASE `%s` CHARACTER SET 'utf8' COLLATE 'utf8_unicode_ci'" % dbname)

        sql = "SELECT DISTINCT(table_name) FROM information_schema.columns WHERE table_schema = '%s'" % dbname
        cursor.execute(sql)

        results = cursor.fetchall()
        for row in results:
            sql = "ALTER TABLE `%s` convert to character set DEFAULT COLLATE DEFAULT" % (row[0])
            cursor.execute(sql)
        db.close()