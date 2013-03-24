from copy import copy
import unittest
from django.test import TestCase
from voomza.apps.store.forms import OrderBillingAddressForm, OrderShippingAddressForm

class OrderBillingAddressFormUSTestCase(unittest.TestCase):
    data = {
        'billing_address':  '780 Post St.',
        'billing_address2': 'Apt. 9',
        'billing_country':  'US',
        'billing_city':     'San Francisco',
        'billing_us_state': 'CA',
        'billing_us_zip':   '94109',
        'billing_state_province': '',
        'billing_postal': '',
        }

    def test_valid(self):
        """
        Tests that the form correctly validates a US address
        """
        form = OrderBillingAddressForm(self.data)
        self.assertTrue(form.is_valid())


    def test_invalid(self):
        data = copy(self.data)
        data['billing_us_zip'] = ''     # no zip code
        form = OrderBillingAddressForm(data)
        self.assertFalse(form.is_valid())

        data2 = copy(self.data)
        data2['billing_us_state'] = ''  # no state
        form2 = OrderBillingAddressForm(data2)
        self.assertFalse(form2.is_valid())


class OrderBillingAddressFormNonUSTestCase(unittest.TestCase):
    data = {
        'billing_address':  '780 Post St.',
        'billing_address2': 'Apt. 9',
        'billing_country':  'CA',
        'billing_city':     'Vancouver',
        'billing_us_state': '',
        'billing_us_zip':   '',
        'billing_state_province': 'BC',
        'billing_postal':   'VOM 1K0',
    }

    def test_valid(self):
        """
        Tests that the form correctly validates a non-US address
        """
        form = OrderBillingAddressForm(self.data)
        self.assertTrue(form.is_valid())

    def test_invalid(self):
        data = copy(self.data)
        data['billing_state_province'] = ''
        form = OrderBillingAddressForm(data)
        self.assertFalse(form.is_valid())

        data2 = copy(self.data)
        data2['billing_postal'] = ''
        form2 = OrderBillingAddressForm(data2)
        self.assertFalse(form2.is_valid())


class OrderShippingAddressFormUSTestCase(unittest.TestCase):
    data = {
        'shipping_address':  '780 Post St.',
        'shippingg_address2': 'Apt. 9',
        'shipping_country':  'US',
        'shipping_city':     'San Francisco',
        'shipping_us_state': 'CA',
        'shipping_us_zip':   '94109',
        'shipping_state_province': '',
        'shipping_postal': '',
        }

    def test_valid(self):
        """
        Tests that the form correctly validates a US address
        """
        form = OrderShippingAddressForm(self.data)
        self.assertTrue(form.is_valid())


    def test_invalid(self):
        data = copy(self.data)
        data['shipping_us_zip'] = ''     # no zip code
        form = OrderShippingAddressForm(data)
        self.assertFalse(form.is_valid())

        data2 = copy(self.data)
        data2['shipping_us_state'] = ''  # no state
        form2 = OrderShippingAddressForm(data2)
        self.assertFalse(form2.is_valid())


class OrderShippingAddressFormNonUSTestCase(unittest.TestCase):
    data = {
        'shipping_address':  '780 Post St.',
        'shipping_address2': 'Apt. 9',
        'shipping_country':  'CA',
        'shipping_city':     'Vancouver',
        'shipping_us_state': '',
        'shipping_us_zip':   '',
        'shipping_state_province': 'BC',
        'shipping_postal':   'VOM 1K0',
        }

    def test_valid(self):
        """
        Tests that the form correctly validates a non-US address
        """
        form = OrderShippingAddressForm(self.data)
        self.assertTrue(form.is_valid())

    def test_invalid(self):
        data = copy(self.data)
        data['shipping_state_province'] = ''
        form = OrderShippingAddressForm(data)
        self.assertFalse(form.is_valid())

        data2 = copy(self.data)
        data2['shipping_postal'] = ''
        form2 = OrderShippingAddressForm(data2)
        self.assertFalse(form2.is_valid())
