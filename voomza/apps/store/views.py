from django.shortcuts import render
from voomza.apps.store.forms import OrderForm, OrderBillingAddressForm, \
    OrderShippingAddressForm, CreditCardForm
from voomza.apps.store.models import PRICE_FOR_FULL, PRICE_FOR_ABRIDGED, PRICE_FOR_DIGITAL, CA_SALES_TAX, PRICE_FOR_SHIPPING


def checkout(request, template_name='checkout.html'):
    """
    What the user ordered comes in as a GET param
    o=full, o=abridged, o=std
    """
    order_full, order_abridged, order_std = False, False, False
    if request.method == 'POST':
        order_form = OrderForm(request.POST)
        billing_address_form = OrderBillingAddressForm(request.POST)
        shipping_address_form = OrderShippingAddressForm(request.POST)
        credit_card_form = CreditCardForm(request.POST)
        pass
    else:
        if 'o' in request.GET:
            if request.GET['o'] == 'full':
                order_full = True
            elif request.GET['o'] == 'abridged':
                order_abridged = True
            else:
                order_std = True
        else:
            order_std = True

        order_form = OrderForm()
        billing_address_form = OrderBillingAddressForm()
        shipping_address_form = OrderShippingAddressForm()
        credit_card_form = CreditCardForm()
    context = {
        'order_form':               order_form,
        'billing_address_form':     billing_address_form,
        'shipping_address_form':    shipping_address_form,
        'credit_card_form':         credit_card_form,

        'order_full':       order_full,
        'order_abridged':   order_abridged,
        'order_std':        order_std,

        'full_price':       PRICE_FOR_FULL,
        'abridged_price':   PRICE_FOR_ABRIDGED,
        'shipping_price':   PRICE_FOR_SHIPPING,
        'digital_price':    PRICE_FOR_DIGITAL,
        'ca_tax_rate':      CA_SALES_TAX,
    }
    return render(request, template_name, context)
