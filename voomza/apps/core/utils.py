import datetime
from itertools import chain
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


import cProfile

def profileit(name):
    def inner(func):
        def wrapper(*args, **kwargs):
            prof = cProfile.Profile()
            retval = prof.runcall(func, *args, **kwargs)
            # Note use of name from outer scope
            prof.dump_stats('%s-%s.profile' % (name, datetime.datetime.now()))
            return retval
        return wrapper
    return inner


import time
from functools import wraps

def timeit(func):
    @wraps(func)
    def wrapper(*args, **kwds):
        start = time.time()
        value = func(*args, **kwds)
        end = time.time()
        return (end-start), value
    return wrapper


def merge_spaces(s):
    """
    Combines consecutive spaces into one,
    useful for cleaning up multiline strings
    """
    return " ".join(s.split())

# http://stackoverflow.com/a/38990/1161906
def merge_dicts(*dicts):
    return dict(chain(*[d.iteritems() for d in dicts]))
