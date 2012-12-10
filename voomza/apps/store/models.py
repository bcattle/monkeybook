from django.db import models

class StoreProfile(models.Model):
    user = models.OneToOneField('auth.User', related_name='store_profile')
    stripe_customer_id = models.CharField(max_length=30, blank=True)


