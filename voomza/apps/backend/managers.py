from django.db import models
from voomza.apps.core import bulk

class FacebookPhotoManager(models.Manager):
    def from_fb_response(self, response):
        """
        Saves photo results to FacebookPhoto models
        """
        facebook_photos = []
        for photo in response.fields:
            photo_obj = self.model(
                facebook_id = photo['id'],
                created = photo['created'],
                height = photo['height'],
                width = photo['width'],
                fb_url = photo['fb_url'],
            )
            facebook_photos.append(photo_obj)
        bulk.insert_many(self.model, facebook_photos)
