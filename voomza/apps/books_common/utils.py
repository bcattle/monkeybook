from django.conf import settings

def set_table_row_format(rankings_cls):
    """
    This is needed because MySQL row langth isn't long enough
    to hold reasonable JSON content by default
    """
    if settings.DATABASES['default']['ENGINE'] == 'django.db.backends.mysql':
        # Set ROW_FORMAT=DYNAMIC to allow longer rows
        from django.db import connection, transaction
        cursor = connection.cursor()
        cursor.execute('ALTER TABLE `%s` ROW_FORMAT=DYNAMIC' % rankings_cls._meta.db_table)
        transaction.commit_unless_managed()
