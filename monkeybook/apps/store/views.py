import logging
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.conf import settings
from voomza.apps.store.forms import OrderForm, OrderBillingAddressForm, \
    OrderShippingAddressForm, CreditCardForm
from voomza.apps.store.models import PRICE_FOR_FULL, PRICE_FOR_ABRIDGED, PRICE_FOR_DIGITAL, CA_SALES_TAX, PRICE_FOR_SHIPPING, Order

logger = logging.getLogger(__name__)


def checkout(request, template_name='checkout.html'):
    """
    What the user ordered comes in as a GET param
    o=full, o=abridged, else electronic
    """
    order_full, order_abridged, order_std = False, False, False
    error_message = ''
    if request.method == 'POST':
        order_form = OrderForm(request.POST)
        billing_address_form = OrderBillingAddressForm(request.POST)
        shipping_address_form = None
        if 'same_shipping' in request.POST and request.POST['same_shipping'] == 'diff':
            shipping_address_form = OrderShippingAddressForm(request.POST)

        # If any forms fail to validate, log an error and return an error message
        error = False
        if not order_form.is_valid():
            logger.error('OrderForm failed to validate: %s. POST: %s' % (order_form.errors, request.POST))
            error = True
        if not billing_address_form.is_valid():
            logger.error('OrderBillingAddressForm failed to validate: %s. POST: %s' % (billing_address_form.errors, request.POST))
            error = True
        if shipping_address_form and not shipping_address_form.is_valid():
            logger.error('OrderShippingAddressForm failed to validate: %s. POST: %s' % (shipping_address_form.errors, request.POST))
            error = True

        if not error:
            # Save model
            order = Order(user=request.user)
            order.populate_from_forms(order_form, billing_address_form, shipping_address_form)
            order.save()
            # Return redirect to homepage
            return HttpResponseRedirect(reverse('homepage') + '?c=order')
        else:
            # Set error message
            error_message = u'Sorry, an error occurred. Please try again.'
            # Fall thorugh to checkout page

    if 'o' in request.GET:
        if request.GET['o'] == 'full':
            order_full = True
        elif request.GET['o'] == 'abridged':
            order_abridged = True

    context = {
        'error_message':            error_message,
        'order_form':               OrderForm(),
        'billing_address_form':     OrderBillingAddressForm(),
        'shipping_address_form':    OrderShippingAddressForm(),
        'credit_card_form':         CreditCardForm(),

        'order_full':       order_full,
        'order_abridged':   order_abridged,

        'full_price':       PRICE_FOR_FULL,
        'abridged_price':   PRICE_FOR_ABRIDGED,
        'shipping_price':   PRICE_FOR_SHIPPING,
        'digital_price':    PRICE_FOR_DIGITAL,
        'ca_tax_rate':      CA_SALES_TAX,

        'STRIPE_PUBLISHABLE_KEY': settings.STRIPE_PUBLISHABLE_KEY,
    }
    return render(request, template_name, context)
