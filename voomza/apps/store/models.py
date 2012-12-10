from django.db import models
from django.db.models.signals import post_save
from django.dispatch.dispatcher import receiver
from django.contrib.auth.models import User


class StoreProfile(models.Model):
    user = models.OneToOneField('auth.User', related_name='store_profile')
    stripe_customer_id = models.CharField(max_length=30, blank=True)


# Create a StoreProfile when creating a User
@receiver(post_save, sender=User, dispatch_uid='store.models')
def create_user_profile(sender, instance, created, **kwargs):
    if created and instance.username != 'admin':
        StoreProfile.objects.create(user=instance)
