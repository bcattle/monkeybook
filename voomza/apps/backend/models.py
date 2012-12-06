import logging
from django.db import models
from jsonfield.fields import JSONField

logger = logging.getLogger(__name__)


class FacebookPhoto(models.Model):
    facebook_id = models.BigIntegerField(primary_key=True)
    height = models.PositiveIntegerField(default=0)
    width = models.PositiveIntegerField(default=0)
    fb_url = models.CharField(max_length=200)
    local_url = models.CharField(max_length=200, default='')

    def url(self):
        return self.local_url or self.fb_url


class PhotoRankings(models.Model):
    """
    The photo rankings for a user,
    holds a ranking of all photos for relevance in each category
    """
    user = models.ForeignKey('auth.User', related_name='photo_rankings')
    # Lists of photos for each category
    family_with = JSONField(default=[], max_length=100000)
    family_alone = JSONField(default=[], max_length=100000)
    gfbf_with = JSONField(default=[], max_length=100000)
    gfbf_alone = JSONField(default=[], max_length=100000)
    group_shots = JSONField(default=[], max_length=100000)
    top_photos = JSONField(default=[], max_length=100000)
    top_photos_first_half = JSONField(default=[], max_length=100000)
    top_photos_second_half = JSONField(default=[], max_length=100000)
    # This is TBD, will want to see some combination of user and group,
    # some (most?) of these lists may be empty
    you_back_in_time_year_1 = JSONField(default=[], max_length=100000)
    you_back_in_time_year_2 = JSONField(default=[], max_length=100000)
    you_back_in_time_year_3 = JSONField(default=[], max_length=100000)
    you_back_in_time_year_4 = JSONField(default=[], max_length=100000)
    you_back_in_time_year_5 = JSONField(default=[], max_length=100000)
    you_back_in_time_year_6 = JSONField(default=[], max_length=100000)
    you_back_in_time_year_7 = JSONField(default=[], max_length=100000)
    you_back_in_time_year_8 = JSONField(default=[], max_length=100000)
    group_back_in_time_year_1 = JSONField(default=[], max_length=100000)
    group_back_in_time_year_2 = JSONField(default=[], max_length=100000)
    group_back_in_time_year_3 = JSONField(default=[], max_length=100000)
    group_back_in_time_year_4 = JSONField(default=[], max_length=100000)
    group_back_in_time_year_5 = JSONField(default=[], max_length=100000)
    group_back_in_time_year_6 = JSONField(default=[], max_length=100000)
    group_back_in_time_year_7 = JSONField(default=[], max_length=100000)
    group_back_in_time_year_8 = JSONField(default=[], max_length=100000)
    # Albums
    top_albums = JSONField(default=[], max_length=100000)
    # Show up to 5 friends (if no family or gfbf)
    top_friend_1 = JSONField(default=[], max_length=100000)
    top_friend_2 = JSONField(default=[], max_length=100000)
    top_friend_3 = JSONField(default=[], max_length=100000)
    top_friend_4 = JSONField(default=[], max_length=100000)
    top_friend_5 = JSONField(default=[], max_length=100000)



class Yearbook(models.Model):
    owner = models.ForeignKey('auth.User', related_name='yearbooks')
    # These indices point to the lists stored in PhotoRanking
    family_photo_1 = models.PositiveSmallIntegerField(default=0)
    family_photo_2 = models.PositiveSmallIntegerField(default=0)
    family_photo_3 = models.PositiveSmallIntegerField(default=0)
    family_photo_4 = models.PositiveSmallIntegerField(default=0)
    gfbf_photo_1 = models.PositiveSmallIntegerField(default=0)
    gfbf_photo_2 = models.PositiveSmallIntegerField(default=0)
    gfbf_photo_3 = models.PositiveSmallIntegerField(default=0)
    gfbf_photo_4 = models.PositiveSmallIntegerField(default=0)
    group_photo_1 = models.PositiveSmallIntegerField(default=0)
    group_photo_2 = models.PositiveSmallIntegerField(default=0)
    group_photo_3 = models.PositiveSmallIntegerField(default=0)
    group_photo_4 = models.PositiveSmallIntegerField(default=0)

    top_photo = models.PositiveSmallIntegerField(default=0)
    first_half_photo_1 = models.PositiveSmallIntegerField(default=0)
    first_half_photo_2 = models.PositiveSmallIntegerField(default=0)
    first_half_photo_3 = models.PositiveSmallIntegerField(default=0)
    second_half_photo_1 = models.PositiveSmallIntegerField(default=0)
    second_half_photo_2 = models.PositiveSmallIntegerField(default=0)
    second_half_photo_3 = models.PositiveSmallIntegerField(default=0)

    back_in_time_photo_1 = models.PositiveSmallIntegerField(default=0)
    back_in_time_photo_2 = models.PositiveSmallIntegerField(default=0)
    back_in_time_photo_3 = models.PositiveSmallIntegerField(default=0)
    back_in_time_photo_4 = models.PositiveSmallIntegerField(default=0)
    back_in_time_photo_5 = models.PositiveSmallIntegerField(default=0)
    back_in_time_photo_6 = models.PositiveSmallIntegerField(default=0)
    back_in_time_photo_7 = models.PositiveSmallIntegerField(default=0)
    back_in_time_photo_8 = models.PositiveSmallIntegerField(default=0)

    top_album_1_id = models.BigIntegerField(default=0)
    top_album_1_photo_1 = models.PositiveSmallIntegerField(default=0)
    top_album_1_photo_2 = models.PositiveSmallIntegerField(default=0)
    top_album_1_photo_3 = models.PositiveSmallIntegerField(default=0)
    top_album_1_photo_4 = models.PositiveSmallIntegerField(default=0)
    top_album_2_id = models.BigIntegerField(default=0)
    top_album_2_photo_1 = models.PositiveSmallIntegerField(default=0)
    top_album_2_photo_2 = models.PositiveSmallIntegerField(default=0)
    top_album_2_photo_3 = models.PositiveSmallIntegerField(default=0)
    top_album_2_photo_4 = models.PositiveSmallIntegerField(default=0)
    top_album_3_id = models.BigIntegerField(default=0)
    top_album_3_photo_1 = models.PositiveSmallIntegerField(default=0)
    top_album_3_photo_2 = models.PositiveSmallIntegerField(default=0)
    top_album_3_photo_3 = models.PositiveSmallIntegerField(default=0)
    top_album_3_photo_4 = models.PositiveSmallIntegerField(default=0)

    top_friend_1_photo_1 = models.PositiveSmallIntegerField(default=0)
    top_friend_1_photo_2 = models.PositiveSmallIntegerField(default=0)
    top_friend_1_photo_3 = models.PositiveSmallIntegerField(default=0)
    top_friend_2_photo_1 = models.PositiveSmallIntegerField(default=0)
    top_friend_2_photo_2 = models.PositiveSmallIntegerField(default=0)
    top_friend_2_photo_3 = models.PositiveSmallIntegerField(default=0)
    top_friend_3_photo_1 = models.PositiveSmallIntegerField(default=0)
    top_friend_3_photo_2 = models.PositiveSmallIntegerField(default=0)
    top_friend_3_photo_3 = models.PositiveSmallIntegerField(default=0)
    top_friend_4_photo_1 = models.PositiveSmallIntegerField(default=0)
    top_friend_4_photo_2 = models.PositiveSmallIntegerField(default=0)
    top_friend_4_photo_3 = models.PositiveSmallIntegerField(default=0)
    top_friend_5_photo_1 = models.PositiveSmallIntegerField(default=0)
    top_friend_5_photo_2 = models.PositiveSmallIntegerField(default=0)
    top_friend_5_photo_3 = models.PositiveSmallIntegerField(default=0)



class Minibook(models.Model):
    owner = models.ForeignKey('auth.User', related_name='minibooks_from')
    target = models.ForeignKey('account.FacebookUser', related_name='minibooks_to')
    photo_1 = models.PositiveSmallIntegerField(default=0)
    photo_2 = models.PositiveSmallIntegerField(default=0)
    photo_3 = models.PositiveSmallIntegerField(default=0)
    photo_4 = models.PositiveSmallIntegerField(default=0)


class MinibookRankings(models.Model):
    minibook = models.OneToOneField(Minibook, related_name='photo_rankings')
    target_with = JSONField(default=[], max_length=100000)
    target_alone = JSONField(default=[], max_length=100000)



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

