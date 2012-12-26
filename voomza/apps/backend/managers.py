from django.db import models
from voomza.apps.core import bulk

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