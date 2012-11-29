import logging
from django.db import models
from django.db.models.signals import post_save
from django.dispatch.dispatcher import receiver
from django.contrib.auth.models import User
from django_facebook.model_managers import FacebookUserManager
from django_facebook.models import BaseFacebookProfileModel
from south.signals import post_migrate
from voomza.apps.core.utils import db_table_exists

logger = logging.getLogger(name=__name__)


class UserProfile(BaseFacebookProfileModel):
    """
    Created by a hook into the post_save signal on User
    """
    user = models.OneToOneField('auth.User', related_name='profile')
    first_name = models.CharField(max_length=40, blank=True)
    locale = models.CharField(max_length=10, blank=True)
#    location?
    pic_square = models.CharField(max_length=200, blank=True)
    current_page = models.CharField(max_length=40, default='invite_friends_to_sign')

    def friends(self):
        friends = YearbookFacebookUser.objects.filter(user_id=self.user_id)
        return friends


### Add an index to the facebook_id field
## Done here because it lives in abstract base model
UserProfile._meta.get_field('facebook_id').db_index = True


class YearbookFacebookUser(models.Model):
    """
    Model for storing a user's friends,
    also store their picture URL for speed
    """
    user = models.ForeignKey('auth.User', db_index=True, help_text='App user this person is a friend of')
    facebook_id = models.BigIntegerField(db_index=True)
    name = models.TextField(blank=True, null=True)
    gender = models.CharField(choices=(('F', 'female'), ('M', 'male')), blank=True, null=True, max_length=1)
    pic_square = models.CharField(max_length=200, blank=True)
    top_friends_order = models.PositiveSmallIntegerField(default=0, help_text='Higher the better',
                                                         db_index=True)
    objects = FacebookUserManager()

    class Meta:
        unique_together = ['user', 'facebook_id']

    def __unicode__(self):
        return u'Facebook user %s' % self.name




## DATABASE VIEWS


class YearbookFacebookUserUsingApp(models.Model):
    """
    This is a DATABASE VIEW
    It pulls only the YearbookFacebookUsers who
    are themselves using the app
    """
    owner = models.ForeignKey('auth.User', related_name='friends_using_app')
    owner_top_friends_order = models.PositiveSmallIntegerField()
    user = models.ForeignKey('auth.User', related_name='yearbook_facebook_user_in_app')
    yearbook_facebook_user = models.ForeignKey(YearbookFacebookUser, primary_key=True, related_name='users_in_app')

    @classmethod
    def setUp(cls):
        """
        Installs the view in the db
        """
        from django.db import connection, transaction
        cursor = connection.cursor()

        # Drop if table exists
        if db_table_exists('account_yearbookfacebookuserusingapp'):
            cls.tearDown()

        # Data modifying operation - commit required

        # It is MUCH FASTER to do a JOIN here rather than NOT IN,
        # see http://stackoverflow.com/a/1519333/1161906
        cursor.execute('''
        CREATE ALGORITHM=MERGE VIEW `account_yearbookfacebookuserusingapp` AS
            SELECT
            `account_yearbookfacebookuser`.`user_id` AS `owner_id`,                               # The "owner"
            `account_yearbookfacebookuser`.`top_friends_order` AS `owner_top_friends_order`,      # Top friends order to owner
            `account_userprofile`.`user_id`,
            `account_yearbookfacebookuser`.`id` AS `yearbook_facebook_user_id`

            FROM `account_yearbookfacebookuser`
            LEFT JOIN `account_userprofile`
                ON `account_userprofile`.`facebook_id`=`account_yearbookfacebookuser`.`facebook_id`
            WHERE (`account_userprofile`.`facebook_id` IS NOT NULL)    # They have a UserProfile
        ''')
        transaction.commit_unless_managed()

    @classmethod
    def tearDown(cls):
        from django.db import connection, transaction
        cursor = connection.cursor()
        # Drop table
        cursor.execute('DROP VIEW `account_yearbookfacebookuserusingapp`')
        # Commit
        transaction.commit_unless_managed()

    class Meta:
        managed = False


class YearbookFacebookUserNotUsingApp(models.Model):
    """
    This view pulls only YearbookFacebookUsers
    who are NOT using the app
    """
    owner = models.ForeignKey('auth.User', related_name='friends_not_using_app')
    owner_top_friends_order = models.PositiveSmallIntegerField()
    yearbook_facebook_user = models.ForeignKey(YearbookFacebookUser,  primary_key=True, related_name='users_not_in_app')

    @classmethod
    def setUp(cls):
        """
        Installs the view in the db
        """
        from django.db import connection, transaction
        cursor = connection.cursor()

        # Drop if table exists
        if db_table_exists('account_yearbookfacebookusernotusingapp'):
            cls.tearDown()

        # Data modifying operation - commit required
        cursor.execute('''
        CREATE ALGORITHM=MERGE VIEW `account_yearbookfacebookusernotusingapp` AS
            SELECT
            `account_yearbookfacebookuser`.`user_id` AS `owner_id`,                               # The "owner"
            `account_yearbookfacebookuser`.`top_friends_order` AS `owner_top_friends_order`,      # Top friends order to owner
            `account_yearbookfacebookuser`.`id` AS `yearbook_facebook_user_id`

            FROM `account_yearbookfacebookuser`
            LEFT JOIN `account_userprofile`
                ON `account_userprofile`.`facebook_id`=`account_yearbookfacebookuser`.`facebook_id`
            WHERE (`account_userprofile`.`facebook_id` IS NULL)    # They do not have a UserProfile
        ''')
        transaction.commit_unless_managed()

    @classmethod
    def tearDown(cls):
        from django.db import connection, transaction
        cursor = connection.cursor()
        # Drop table
        cursor.execute('DROP VIEW `account_yearbookfacebookusernotusingapp`')
        # Commit
        transaction.commit_unless_managed()

    class Meta:
        managed = False


## SIGNALS


# Make sure we create a UserProfile when creating a User
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created and instance.username != 'admin':
        # Why do we need this here? threading?
        # somehow this is getting called twice, conflicting pk's
        try:
            profile = instance.profile
        except UserProfile.DoesNotExist:
            print 'UserProfile create called()'
            UserProfile.objects.create(user=instance)


#@receiver(post_syncdb, sender=account.models)
@receiver(post_migrate)
def create_db_views(app, **kwargs):
    if app == 'account':
        # Set up thew views
        YearbookFacebookUserUsingApp.setUp()
        YearbookFacebookUserNotUsingApp.setUp()
