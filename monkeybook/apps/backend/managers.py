import collections
from django.db import models
from monkeybook.apps.core import bulk


class FacebookPhotoManager(models.Manager):
    def from_getter(self, getter):
        """
        Saves photo results to FacebookPhoto models
        """
        facebook_photos = []
        for photo in getter.fields:
            photo_obj = self.model(
                facebook_id  = photo['id'],
                created      = photo['created'],
                height       = photo['height'],
                width        = photo['width'],
                fb_url       = photo['fb_url'],
                caption      = photo.get('caption', '')
            )
            facebook_photos.append(photo_obj)
        bulk.insert_or_update_many(self.model, facebook_photos, exclude_fields=['comments'])
        return self


class YearbookManager(models.Manager):
    def get_friends_books(self, user):
        """
        Returns books belonging to facebook friends
        of the supplied user

        This returns a *QuerySet* that may contain
        more than one book per person
        """
        return self.model.objects.filter(
            rankings__user__profile__facebook_user__friend_of__owner=user
        ).order_by('-rankings__user__profile__facebook_user__friend_of__top_friends_order', '-created')

    def get_distinct_friends_books(self, user):
        """
        This returns a *list*, made by returning only the
        most recent book from each user
        """
        friends_books_qs = self.get_friends_books(user)
        books_by_friend = collections.OrderedDict()
        for yb in friends_books_qs:
            if yb.rankings.user in books_by_friend:
                if yb.created > books_by_friend[yb.rankings.user].created:
                    books_by_friend[yb.rankings.user] = yb
            else:
                books_by_friend[yb.rankings.user] = yb
        return books_by_friend.items()


