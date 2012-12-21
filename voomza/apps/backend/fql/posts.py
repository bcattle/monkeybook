import logging, datetime, calendar
from pytz import utc
from voomza.apps.backend.fql import FQLTask
from voomza.apps.backend.getter import FreqDistResultGetter, ResultGetter

logger = logging.getLogger(__name__)

# http://stackoverflow.com/a/11409065/1161906
this_year = datetime.datetime(datetime.datetime.now().year, 1, 1, tzinfo=utc)
unix_this_year = calendar.timegm(this_year.utctimetuple())

class OwnerPostsFromYearTask(FQLTask):
    fql = '''
        SELECT post_id, actor_id, comments, likes FROM stream
            WHERE source_id = me() AND filter_key='owner' AND created_time > %s LIMIT 500
    ''' % unix_this_year

    def on_results(self, results):
        getter = ResultGetter(
            results,
            id_field='post_id',
            id_is_int=False,
            fields=['actor_id', 'comments.count', 'likes.count'],
            field_names={'comments.count': 'comment_count', 'likes.count': 'like_count'},
            defaults={'comments.count': 0, 'likes.count':0 },
        )
        return getter


class OthersPostsFromYearTask(OwnerPostsFromYearTask):
    fql = '''
        SELECT post_id, actor_id, comments, likes FROM stream
            WHERE source_id = me() AND filter_key='others' AND created_time > %s LIMIT 500
    ''' % unix_this_year


class GetPostTask(FQLTask):
    def __init__(self, post_id, name=None):
        self.fql = '''
            SELECT message, comments, likes, created_time, place, attachment
                FROM stream WHERE post_id = '%s'
        ''' % post_id
        super(GetPostTask, self).__init__(name)

    def on_results(self, results):
        # This one requires looping through to get the comments (and likes for that matter)
        # Just return the JSON
        return results


# birthday_this_year = datetime.datetime(datetime.date.today().year, birthday.month, birthday.day, 0, 0, 0)
# start_time = birthday_this_year - datetime.timedelta(days=1)
# end_time = birthday_this_year + datetime.timedelta(days=3)
# start_unix_time = calendar.timegm(start_time.utctimetuple())
# end_unix_time = calendar.timegm(end_time.utctimetuple())
