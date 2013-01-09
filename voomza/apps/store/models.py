import logging
from decimal import Decimal
from django.db import models
from django.db.models.signals import post_save
from django.dispatch.dispatcher import receiver
from django.contrib.auth.models import User
from django_countries import CountryField

logger = logging.getLogger(__name__)


class StoreProfile(models.Model):
    user = models.OneToOneField('auth.User', related_name='store_profile')
    stripe_customer_id = models.CharField(max_length=30, blank=True)


PRICE_FOR_DIGITAL   = Decimal('4.99')
PRICE_FOR_ABRIDGED  = Decimal('39.99')
PRICE_FOR_FULL      = Decimal('79.99')
PRICE_FOR_SHIPPING  = Decimal('8.99')
CA_SALES_TAX        = Decimal('.0875')      # San Francisco
CA_STATE_ABBR       = 'CA'


QUANTITY_CHOICES = [
    ('', 0), ('1', 1), ('2', 2), ('3', 3), ('4', 4), ('5', 5),
]
DIGITAL_QUANTITY_CHOICES = [
    ('', 0), ('1', 1),
]


class Order(models.Model):
    user = models.ForeignKey('auth.User')
    stripe_single_use_token = models.CharField(max_length=255)
    created = models.DateTimeField(auto_now_add=True)

    charged_total = models.CharField(max_length=8, blank=True)
    abridged_quantity = models.PositiveSmallIntegerField(choices=QUANTITY_CHOICES, default=0, blank=True)
    full_quantity = models.PositiveSmallIntegerField(choices=QUANTITY_CHOICES, default=0, blank=True)
    digital_upgrade = models.PositiveSmallIntegerField(choices=DIGITAL_QUANTITY_CHOICES, default=0, blank=True)

    billing_address = models.CharField(max_length=255)
    billing_address2 = models.CharField(max_length=255, blank=True)
    billing_country = CountryField()
    billing_city = models.CharField(max_length=50)
    billing_state_province = models.CharField(max_length=50)
    billing_postal = models.CharField(max_length=10)

    shipping_name = models.CharField(max_length=255)
    shipping_address = models.CharField(max_length=255)
    shipping_address2 = models.CharField(max_length=255, blank=True)
    shipping_country = CountryField()
    shipping_city = models.CharField(max_length=50)
    shipping_state_province = models.CharField(max_length=50)
    shipping_postal = models.CharField(max_length=10)

    def get_total(self):
        # Electronic goods not taxable
        # Shipping not taxed
        # Shipped out of state not taxed
        untaxed_subtotal = PRICE_FOR_DIGITAL if self.digital_upgrade else 0
        taxed_subtotal = PRICE_FOR_ABRIDGED * self.abridged_quantity + PRICE_FOR_FULL * self.full_quantity
        shipping_subtotal = PRICE_FOR_SHIPPING if (self.abridged_quantity or self.full_quantity) else 0
        tax_subtotal = taxed_subtotal * CA_SALES_TAX if self.shipping_state_province == CA_STATE_ABBR else 0
        return untaxed_subtotal + taxed_subtotal + shipping_subtotal + tax_subtotal

    def populate_from_forms(self, order_form, billing_address_form, shipping_address_form=None):
        self.stripe_single_use_token = order_form.cleaned_data['stripe_single_use_token']
        self.abridged_quantity       = order_form.cleaned_data['abridged_quantity']
        self.full_quantity           = order_form.cleaned_data['full_quantity']
        self.digital_upgrade         = order_form.cleaned_data['digital_upgrade']

        self.billing_address         = billing_address_form.cleaned_data['billing_address']
        self.billing_address2        = billing_address_form.cleaned_data['billing_address2']
        self.billing_country         = billing_address_form.cleaned_data['billing_country']
        self.billing_city            = billing_address_form.cleaned_data['billing_city']
        self.billing_state_province  = billing_address_form.cleaned_data['billing_us_state'] if billing_address_form.cleaned_data['billing_country'] == 'US' else billing_address_form.cleaned_data['billing_state_province']
        self.billing_postal          = billing_address_form.cleaned_data['billing_us_zip'] if billing_address_form.cleaned_data['billing_country'] == 'US' else billing_address_form.cleaned_data['billing_postal']

        if shipping_address_form:
            self.shipping_name     = shipping_address_form.cleaned_data['shipping_name']
            self.shipping_address  = shipping_address_form.cleaned_data['shipping_address']
            self.shipping_address2 = shipping_address_form.cleaned_data['shipping_address2']
            self.shipping_country  = shipping_address_form.cleaned_data['shipping_country']
            self.shipping_city     = shipping_address_form.cleaned_data['shipping_city']
            self.shipping_state_province = shipping_address_form.cleaned_data['shipping_us_state'] if shipping_address_form.cleaned_data['shipping_country'] == 'US' else shipping_address_form.cleaned_data['shipping_state_province']
            self.shipping_postal   = shipping_address_form.cleaned_data['shipping_us_zip'] if shipping_address_form.cleaned_data['shipping_country'] == 'US' else shipping_address_form.cleaned_data['shipping_postal']

        # Double check the order totals
#        if 'charged_total' in order_form.cleaned_data and Decimal(order_form.cleaned_data['charged_total']) != self.get_total():
#            logger.error('OrderForm charged_total didn\'t match model total. %s != %s' % (order_form.cleaned_data['charged_total'], self.get_total()))


# Create a StoreProfile when creating a User
@receiver(post_save, sender=User, dispatch_uid='store.models')
def create_user_profile(sender, instance, created, **kwargs):
    if created and instance.username != 'admin':
        StoreProfile.objects.create(user=instance)
