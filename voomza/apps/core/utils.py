from django.db import transaction

@transaction.commit_manually
def flush_transaction():
    """
    Flush the current transaction so we don't read stale data
    http://stackoverflow.com/a/7794220/1161906

    Use in long running processes to make sure fresh data is read from
    the database.  This is a problem with MySQL and the default
    transaction mode.  You can fix it by setting
    "transaction-isolation = READ-COMMITTED" in my.cnf or by calling
    this function at the appropriate moment

    """
    transaction.commit()


def db_table_exists(table_name):
    """
    https://gist.github.com/527113/307c2dec09ceeb647b8fa1d6d49591f3352cb034#gistcomment-337110
    """
    from django.db import connection
    return table_name in connection.introspection.table_names()