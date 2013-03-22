from __future__ import division, print_function, unicode_literals
import logging
from django.db import models
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from jsonfield.fields import JSONField
from voomza.apps.account.models import FacebookUser
from voomza.apps.books_common.managers import FacebookPhotoManager
from voomza.apps.books_common.ranking import RankedPhotosMixin
from voomza.apps.books_common.short_url import UrlEncoder
from voomza.apps.books_common.settings import *

logger = logging.getLogger(__name__)


class FacebookPhoto(models.Model):
    facebook_id = models.BigIntegerField(primary_key=True)
    created = models.DateTimeField(null=True)
    people_in_photo = models.PositiveSmallIntegerField(default=0, help_text='Total, i.e. including me')
    height = models.PositiveIntegerField(default=0)
    width = models.PositiveIntegerField(default=0)
    fb_url = models.CharField(max_length=200)
    local_url = models.CharField(max_length=200, default='')
    caption = models.CharField(max_length=1000, default='')
    comments = JSONField(default="[]", max_length=100000)

    def url(self):
        return self.local_url or self.fb_url

    @property
    def aspect_ratio(self):
        return float(self.width) / float(self.height)

    def is_square(self):
        return LOWEST_SQUARE_ASPECT_RATIO < self.aspect_ratio < HIGHEST_SQUARE_ASPECT_RATIO

    def is_portrait(self):
        return self.aspect_ratio < LOWEST_SQUARE_ASPECT_RATIO

    def is_landscape(self):
        return self.aspect_ratio > HIGHEST_SQUARE_ASPECT_RATIO

    def get_top_comment(self):
        if self.comments:

            # Assign a score
            for comment in self.comments:
                comment['score'] = comment_score(comment)

            # Sort by score, then by date
            # Take the highest-scoring, earliest
            comments_sorted = sorted(self.comments,
                                     key=lambda comment: (-comment['score'], comment['time']))

            top_comment, top_comment_name, top_comment_pic = '', '', ''
            for comment in comments_sorted:
                # Get user's name and photo
                try:
                    fb_user = FacebookUser.objects.get(facebook_id=comment['fromid'])
                except FacebookUser.DoesNotExist:
                    continue
                    # If the user exists
                if fb_user.name and fb_user.pic_square:
                    top_comment_name = fb_user.name
                    top_comment_pic = fb_user.pic_square
                    top_comment = comment

            return {
                'text': top_comment,
                'user_name': top_comment_name,
                'user_pic': top_comment_pic,
                }

    objects = FacebookPhotoManager()


class GenericBook(models.Model):
    owner = models.ForeignKey('auth.User', related_name='books')
    short_slug = models.CharField(max_length=20, unique=True, db_index=True)
    book_key = models.CharField(max_length=20, db_index=True, help_text='Lookup to settings.ALL_BOOKS')

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    book_object = generic.GenericForeignKey()

    # Derived fields
    def title(self):
        return settings.ALL_BOOKS[self.book_key]['title']

    def cover(self):
        return settings.STATIC_URL + settings.ALL_BOOKS[self.book_key]['cover']

    class Meta:
        verbose_name_plural = 'Generic books'

    def save(self, *args, **kwargs):
        # Save the model, then set the `short_slug` and save it again
        super(GenericBook, self).save(*args, **kwargs)
        if not self.short_slug:
            self.short_slug = UrlEncoder().encode_url(self.id)
            super(GenericBook, self).save(*args, **kwargs)


ALLOWED_TO_SEE_CHOICES = (
    'EVERYONE', 'NOBODY', 'FRIENDS', 'CUSTOM'
)

class BaseBookModel(models.Model, RankedPhotosMixin):
    generic_book = generic.GenericRelation(GenericBook)
    owner = models.ForeignKey('auth.User', related_name='books')
    allowed_to_see = models.CharField(max_length=10, choices=ALLOWED_TO_SEE_CHOICES, default='EVERYONE')
    allowed_to_see_custom_users = models.ManyToManyField('account.FacebookFriend')
    created = models.DateTimeField(auto_now_add=True)
    run_time = models.FloatField(null=True)

    def user_can_see_book(self, fb_id):
        """
        Returns true if the user w/ `fb_id`
        can see the book
        """
        if self.allowed_to_see == 'EVERYONE':
            return True
        elif self.allowed_to_see == 'NOBODY':
            # Only the owner can see
            return self.owner.profile.facebook_user.id == fb_id
        elif self.allowed_to_see == 'FRIENDS':
            # `fb_id` is one of this user's friends
            raise NotImplementedError
        elif self.allowed_to_see == 'CUSTOM':
            # one of the usere in `allowed_to_see_custom_users`
            raise NotImplementedError

    def get_absolute_url(self):
        return reverse('yearbook', kwargs={'hash': self.hash})

    def save(self, *args, **kwargs):
        # Can't create a book without a `key`
        assert self.book_key
        # Create a GenericBook for this model if it doesn't have one
        if not self.generic_book:
            self.generic_book = GenericBook(book_key=self.book_key, owner=self.owner)
        super(BaseBookModel, self).save(*args, **kwargs)

    class Meta:
        abstract = True
        ordering = ['-created']

