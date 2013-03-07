from __future__ import division, print_function, unicode_literals
import logging
from voomza.apps.books_common.fql import FQLTask
from voomza.apps.books_common.getter import ResultGetter
from voomza.apps.core.utils import unix_date_from_utc

logger = logging.getLogger(__name__)


class OwnerPostsFromYearTask(FQLTask):
    def __init__(self, year, name=None):
        unix_this_year     = unix_date_from_utc(year, 1, 1)
        unix_this_year_end = unix_date_from_utc(year, 12, 31)

        self.fql = '''
            SELECT post_id, actor_id, created_time, comments, likes, message FROM stream
                WHERE source_id=me() AND message!='' AND filter_key='owner'
                AND created_time > %s AND created_time < %s LIMIT 500
        ''' % (unix_this_year, unix_this_year_end)

        super(OwnerPostsFromYearTask, self).__init__(name)


    def on_results(self, results):
        getter = ResultGetter(
            results,
            id_field='post_id',
            id_is_int=False,
            fields=['actor_id', 'created_time', 'comments', 'comments.count',
                    'likes.count', 'message'],
            field_names={'comments.count': 'comment_count', 'likes.count': 'like_count'},
            defaults={'comments.count': 0, 'likes.count':0 },
            timestamps=['created_time']
        )
        return getter


class OthersPostsFromYearTask(OwnerPostsFromYearTask):
    def __init__(self, year, name=None):
        unix_this_year     = unix_date_from_utc(year, 1, 1)
        unix_this_year_end = unix_date_from_utc(year, 12, 31)

        self.fql = '''
            SELECT post_id, actor_id, created_time, comments, likes, message FROM stream
                WHERE source_id=me() AND message!='' AND filter_key='others'
                AND created_time > %s AND created_time < %s LIMIT 500
        ''' % (unix_this_year, unix_this_year_end)

        super(OwnerPostsFromYearTask, self).__init__(name)


#class GetPostTask(FQLTask):
#    def __init__(self, post_ids, name=None):
#        self.fql = ['''
#            SELECT message, comments, likes, created_time, place, attachment
#                FROM stream WHERE post_id = '%s'
#        ''' % post_id for post_id in post_ids]
#        super(GetPostTask, self).__init__(name)
#
#    def on_results(self, results):
#        # This one requires looping through to get the comments (and likes for that matter)
#        # Just return the JSON
#        return results

