from django.db import models
from django.contrib.auth.models import User


class TopFriend(models.Model):
    user = models.ForeignKey('auth.User', related_name='top_friends')
    friend_id = models.BigIntegerField()
    rank = models.PositiveSmallIntegerField(default=0, db_index=True, help_text='The higher the better')

    class Meta:
        unique_together = ['user', 'friend_id']


class TopFriendStat(models.Model):
    """
    All of the scores we pulled to calculate
    who a user's top friends were
    """
    user = models.ForeignKey('auth.User', related_name='top_friend_stats')
    friend_id = models.BigIntegerField()
    tagged_with = models.PositiveSmallIntegerField(null=True, help_text='How many times you\'re tagged with this person')
    you_posts_to = models.PositiveSmallIntegerField(null=True, help_text='How many times you posted to this person ')
    you_photos_liked = models.PositiveSmallIntegerField(null=True, help_text='How many times you liked a photo from this person')
    you_links_liked = models.PositiveSmallIntegerField(null=True, help_text='How many times you liked a link from this person')
    you_statuses_liked = models.PositiveSmallIntegerField(null=True, help_text='How many times you liked a status from this person')
    them_posts_to = models.PositiveSmallIntegerField(null=True, help_text='How many times they posted to you')
    them_comment_to_photo = models.PositiveSmallIntegerField(null=True, help_text='How many times they commented on your photo')
    them_comment_to_link = models.PositiveSmallIntegerField(null=True, help_text='How many times they commented on your link')
    them_comment_to_status = models.PositiveSmallIntegerField(null=True, help_text='How many times they commented on your status')
    them_like_photo = models.PositiveSmallIntegerField(null=True, help_text='How many times they liked your photo')
    them_like_link = models.PositiveSmallIntegerField(null=True, help_text='How many times they liked your link')
    them_like_status = models.PositiveSmallIntegerField(null=True, help_text='How many times they liked your status')


class Badge(models.Model):
    """
    Yearbook "badges" - best smile, most likely to get arrested, etc.
    """
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=200)
    icon_small = models.CharField(max_length=200)


class BadgeVote(models.Model):
    badge = models.ForeignKey(Badge)
    from_user = models.ForeignKey(User)
    # To a FacebookUser, because the person nominated
    # may or may not be in the app
    to_facebook_user = models.ForeignKey('account.YearbookFacebookUser')
    created_at = models.DateTimeField(auto_now_add=True)


class YearbookSign(models.Model):
    from_user = models.ForeignKey(User)
    text = models.TextField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)


