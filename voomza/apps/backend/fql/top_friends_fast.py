import logging
from voomza.apps.backend.fql.base import FQLTask, FqlTaskPipeline
from voomza.apps.backend.getter import ResultGetter
from voomza.apps.backend.settings import *

logger = logging.getLogger(__name__)


class GetFriendsTask(FQLTask):
    """
    Pulls all of the user's friends
    """
    fql = '''
        SELECT uid, first_name, name, pic_square FROM user
            WHERE uid IN (SELECT uid2 FROM friend WHERE uid1 = me())
    '''
    def on_results(self, results):
        getter = ResultGetter(
            results,
            fields=['first_name', 'name', 'pic_square'],
            id_field='uid'
        )
        return getter


class TaggedWithMeTask(FQLTask):
    """
    Returns all of the tags of all photos I am in
    We do this because we can't pull `tags`
    from the `photo` table.
    --> This is a workaround for the fact that
        facebook WHERE queries are broken for `photo_tags`
    """
    fql = '''
        SELECT subject, object_id, created FROM photo_tag WHERE object_id IN
            (SELECT object_id FROM photo_tag WHERE subject=me())
        AND subject!=me() AND created < %s ORDER BY created DESC
    ''' % UNIX_THIS_YEAR_END
    def on_results(self, results):
        """
        Build a list of user ids that are tagged with
        the current user
        """
        # We *don't* want to collapse on the object_id field here
        # 2/20: sometimes the `created` field comes back None
        # for some people
        getter = ResultGetter(
            results,
            auto_id_field=True,
            fields=['subject', 'created'],
            integer_fields=['object_id', 'subject'],
            timestamps=['created'],
            defaults={'created': datetime.datetime(2012 - 2, 1, 1, tzinfo=utc)},
        )
        return getter


class TopFriendsFastPipeline(FqlTaskPipeline):
    class Meta:
        tasks = [GetFriendsTask(), TaggedWithMeTask()]
