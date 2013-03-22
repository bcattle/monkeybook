from __future__ import division, print_function, unicode_literals
from voomza.apps.account.models import FamilyConnection, FacebookUser
from voomza.apps.books_common.fql.base import FQLTask, FqlTaskPipeline
from voomza.apps.books_common.getter import ResultGetter
from voomza.apps.core import bulk


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


class ProfileFieldsTask(FQLTask):
    fql = '''
        SELECT uid, first_name, pic_square, locale, significant_other_id
            FROM user WHERE uid = me()
    '''

    def on_results(self, results):
        return results[0]

    def save_profile_fields(self, user, profile_fields):
        # Create a FacebookUser
        fbu = FacebookUser(
            facebook_id = profile_fields['uid'],
            name = user.profile.facebook_name,
            first_name = profile_fields['first_name'],
            pic_square = profile_fields['pic_square'],
        )
        fbu.save()

        user.profile.first_name = profile_fields['first_name']
        user.profile.locale = profile_fields['locale']
        user.profile.pic_square = profile_fields['pic_square']
        user.profile.significant_other_id = profile_fields['significant_other_id']
        user.profile.facebook_id = profile_fields['uid']
        user.profile.facebook_user = fbu
        user.profile.save()


class FamilyTask(FQLTask):
    fql = '''
        SELECT uid, relationship FROM family WHERE profile_id = me()
    '''

    def on_results(self, results):
        getter = ResultGetter(
            results,
            id_field='uid',
            fields=['relationship']
        )
        return getter

    def save_family(self, user, getter):
        family = []
        for family_member in getter.fields:
            fam_db = FamilyConnection(
                owner           = user,
                facebook_id     = family_member['id'],
                relationship    = family_member['relationship'],
            )
            family.append(fam_db)
        bulk.insert_or_update_many(FamilyConnection, family)


class ProfilePipeline(FqlTaskPipeline):
    tasks = [
        ProfileFieldsTask(),
        FamilyTask()
    ]
