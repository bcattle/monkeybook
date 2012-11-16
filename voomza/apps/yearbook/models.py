from django.db import models
from django.contrib.auth.models import User


class TopFriend(models.Model):
    """
    A subset of the user's friends, ranked in
    order of how close the relationship is
    """
    user = models.ForeignKey('account.UserProfile')
    friend = models.ForeignKey('account.FacebookUserWithPic')
    rank = models.PositiveSmallIntegerField()


class TopFriendStats(models.Model):
    """
    All of the scores we pulled to calculate
    who a user's top friends were
    """
    top_friend = models.OneToOneField(TopFriend)
    tagged_with = models.PositiveSmallIntegerField(help_text='How many times you\'re tagged with this person')
    you_posts_to = models.PositiveSmallIntegerField(help_text='How many times you posted to this person ')
    you_photos_liked = models.PositiveSmallIntegerField(help_text='How many times you liked a photo from this person')
    you_links_liked = models.PositiveSmallIntegerField(help_text='How many times you liked a link from this person')
    you_statuses_liked = models.PositiveSmallIntegerField(help_text='How many times you liked a status from this person')
    them_posts_to = models.PositiveSmallIntegerField(help_text='How many times they posted to you')
    them_comment_to_photo = models.PositiveSmallIntegerField(help_text='How many times they commented on your photo')
    them_comment_to_link = models.PositiveSmallIntegerField(help_text='How many times they commented on your link')
    them_comment_to_status = models.PositiveSmallIntegerField(help_text='How many times they commented on your status')
    them_like_photo = models.PositiveSmallIntegerField(help_text='How many times they liked your photo')
    them_like_link = models.PositiveSmallIntegerField(help_text='How many times they liked your link')
    them_like_status = models.PositiveSmallIntegerField(help_text='How many times they liked your status')


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
    to_facebook_user = models.ForeignKey('account.FacebookUserWithPic')
    created_at = models.DateTimeField(auto_now_add=True)


class YearbookSign(models.Model):
    from_user = models.ForeignKey(User)
    text = models.TextField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)


