from itertools import chain, dropwhile
from operator import mul, attrgetter, __not__
from django.db import models
from django.db.models.query import REPR_OUTPUT_SIZE, EmptyQuerySet
from django.db.models.signals import post_syncdb
from django.dispatch.dispatcher import receiver
from south.signals import post_migrate


class DefaultUnicodeBase(models.Model):
    """
    Stolen from django_facebook
    """
    def __unicode__(self):
        """
        Looks at some common ORM naming standards and tries to display those before
        default to the django default
        """
        attributes = ['name', 'title', 'slug']
        name = None
        for a in attributes:
            if hasattr(self, a):
                name = getattr(self, a)
        if not name:
            name = repr(self.__class__)
        return name

    def __repr__(self):
        return '<%s[%s]>' % (self.__class__.__name__, self.pk)

    class Meta:
        abstract = True


def mul_it(it1, it2):
    """
    Element-wise iterables multiplications.
    """
    assert len(it1) == len(it2),\
    "Can not element-wise multiply iterables of different length."
    return map(mul, it1, it2)


def chain_sing(*iterables_or_items):
    """
    As itertools.chain except that if an argument is not iterable then chain it
    as a singleton.
    """
    for iter_or_item in iterables_or_items:
        if hasattr(iter_or_item, '__iter__'):
            for item in iter_or_item:
                yield item
        else:
            yield iter_or_item


class IableSequence(object):
    """
    Wrapper for sequence of iterable and indexable by non-negative integers
    objects. That is a sequence of objects which implement __iter__, __len__ and
    __getitem__ for slices, ints and longs.

    Note: not a Django-specific class.
    """
    def __init__(self, *args, **kwargs):
        self.iables = args # wrapped sequence
        self._len = None # length cache
        self._collapsed = [] # collapsed elements cache

    def __len__(self):
        if not self._len:
            self._len = sum(len(iable) for iable in self.iables)
        return self._len


    def __iter__(self):
        return chain(*self.iables)

    def __nonzero__(self):
        try:
            iter(self).next()
        except StopIteration:
            return False
        return True


    def _collect(self, start=0, stop=None, step=1):
        if not stop:
            stop = len(self)
        sub_iables = []
        # collect sub sets
        it = self.iables.__iter__()
        try:
            while stop>start:
                i = it.next()
                i_len = len(i)
                if i_len > start:
                    # no problem with 'stop' being too big
                    sub_iables.append(i[start:stop:step])
                start = max(0, start-i_len)
                stop -= i_len
        except StopIteration:
            pass
        return sub_iables

    def __getitem__(self, key):
        """
        Preserves wrapped indexable sequences.
        Does not support negative indices.
        """
        # params validation
        if not isinstance(key, (slice, int, long)):
            raise TypeError
        assert ((not isinstance(key, slice) and (key >= 0))
                or (isinstance(key, slice) and (key.start is None or key.start >= 0)
                    and (key.stop is None or key.stop >= 0))),\
        "Negative indexing is not supported."
        # initialization
        if isinstance(key, slice):
            start, stop, step = key.indices(len(self))
            ret_item=False
        else: # isinstance(key, (int,long))
            start, stop, step = key, key+1, 1
            ret_item=True
            # collect sub sets
        ret_iables = self._collect(start, stop, step)
        # return the simplest possible answer
        if not len(ret_iables):
            if ret_item:
                raise IndexError("'%s' index out of range" % self.__class__.__name__)
            return ()
        if ret_item:
            # we have exactly one query set with exactly one item
            assert len(ret_iables) == 1 and len(ret_iables[0]) == 1
            return ret_iables[0][0]
            # otherwise we have more then one item in at least one query set
        if len(ret_iables) == 1:
            return ret_iables[0]
            # Note: this can't be self.__class__ instead of IableSequence; exemplary
        # cause is that indexing over query sets returns lists so we can not
        # return QuerySetSequence by default. Some type checking enhancement can
        # be implemented in subclasses.
        return IableSequence(*ret_iables)


    def collapse(self, stop=None):
        """
        Collapses sequence into a list.

        Try to do it effectively with caching.
        """
        if not stop:
            stop = len(self)
            # if we already calculated sufficient collapse then return it
        if len(self._collapsed) >= stop:
            return self._collapsed[:stop]
            # otherwise collapse only the missing part
        items = self._collapsed
        sub_iables = self._collect(len(self._collapsed), stop)
        for sub_iable in sub_iables:
            items+=sub_iable
            # cache new collapsed items
        self._collapsed = items
        return self._collapsed

    def __repr__(self):
        # get +1 element for the truncation msg if applicable
        items = self.collapse(stop=REPR_OUTPUT_SIZE+1)
        if len(items) > REPR_OUTPUT_SIZE:
            items[-1] = "...(remaining elements truncated)..."
        return repr(items)



class QuerySetSequence(IableSequence):
    """
    Wrapper for the query sets sequence without the restriction on the identity
    of the base models.
    """
    def count(self):
        if not self._len:
            self._len = sum(qs.count() for qs in self.iables)
        return self._len

    def __len__(self):
        # override: use DB effective count's instead of len()
        return self.count()

    def order_by(self, *field_names):
        """
        Returns a list of the QuerySetSequence items with the ordering changed.
        """
        # construct a comparator function based on the field names prefixes
        reverses = [1] * len(field_names)
        field_names = list(field_names)
        for i in range(len(field_names)):
            field_name = field_names[i]
            if field_name[0] == '-':
                reverses[i] = -1
                field_names[i] = field_name[1:]
            # wanna iterable and attrgetter returns single item if 1 arg supplied
        fields_getter = lambda i: chain_sing(attrgetter(*field_names)(i))
        # comparator gets the first non-zero value of the field comparison
        # results taking into account reverse order for fields prefixed with '-'
        comparator = lambda i1, i2:\
        dropwhile(__not__,
            mul_it(map(cmp, fields_getter(i1), fields_getter(i2)), reverses)
        ).next()
        # return new sorted list
        return sorted(self.collapse(), cmp=comparator)

    def filter(self, *args, **kwargs):
        """
        Returns a new QuerySetSequence or instance with the args ANDed to the
        existing set.

        QuerySetSequence is simplified thus result actually can be one of:
        QuerySetSequence, QuerySet, EmptyQuerySet.
        """
        return self._filter_or_exclude(False, *args, **kwargs)

    def exclude(self, *args, **kwargs):
        """
        Returns a new QuerySetSequence instance with NOT (args) ANDed to the
        existing set.

        QuerySetSequence is simplified thus result actually can be one of:
        QuerySetSequence, QuerySet, EmptyQuerySet.
        """
        return self._filter_or_exclude(True, *args, **kwargs)

    def _simplify(self, qss=None):
        """
        Returns QuerySetSequence, QuerySet or EmptyQuerySet depending on the
        contents of items, i.e. at least two non empty QuerySets, exactly one
        non empty QuerySet and all empty QuerySets respectively.

        Does not modify original QuerySetSequence.
        """
        not_empty_qss = filter(None, qss if qss else self.iables)
        if not len(not_empty_qss):
            return EmptyQuerySet()
        if len(not_empty_qss) == 1:
            return not_empty_qss[0]
        return QuerySetSequence(*not_empty_qss)

    def _filter_or_exclude(self, negate, *args, **kwargs):
        """
        Maps _filter_or_exclude over QuerySet items and simplifies the result.
        """
        # each Query set is cloned separately

#        return self._simplify(*map(lambda qs:
#        qs._filter_or_exclude(negate, *args, **kwargs), self.iables))

        return self._simplify(map(lambda qs:
        qs._filter_or_exclude(negate, *args, **kwargs), self.iables))

    def exists(self):
        for qs in self.iables:
            if qs.exists():
                return True
        return False



# http://stackoverflow.com/questions/2108824/mysql-incorrect-string-value-error-when-save-unicode-string-in-django
@receiver(post_syncdb, dispatch_uid='core.models')
@receiver(post_migrate, dispatch_uid='core.models')
def set_all_cols_utf8(app, **kwargs):
    # post_syncdb, `app` is a Module. post_migrate `app` is a string
    from django.conf import settings
    if settings.DATABASES['default']['ENGINE'] == 'django.db.backends.mysql':
        # Set ROW_FORMAT=DYNAMIC to allow longer rows
        from django.db import connection, transaction
        cursor = connection.cursor()
        db_name = settings.DATABASES['default']['NAME']
        cursor.execute("ALTER DATABASE `%s` CHARACTER SET 'utf8' COLLATE 'utf8_unicode_ci'" % db_name)

        sql = "SELECT DISTINCT(table_name) FROM information_schema.columns WHERE table_schema = '%s'" % db_name
        cursor.execute(sql)

        results = cursor.fetchall()
        for row in results:
            sql = "ALTER TABLE `%s` convert to character set DEFAULT COLLATE DEFAULT" % (row[0])
            cursor.execute(sql)
        transaction.commit_unless_managed()
