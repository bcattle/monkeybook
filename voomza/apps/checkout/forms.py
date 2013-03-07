from __future__ import division, print_function, unicode_literals
from django import forms
from django_countries.countries import COUNTRIES
from django_localflavor_us.forms import USStateField, USStateSelect, USZipCodeField
from voomza.apps.checkout.models import Order


class OrderForm(forms.ModelForm):
    stripe_single_use_token = forms.CharField(widget=forms.HiddenInput(), required=True)
    charged_total           = forms.CharField(widget=forms.HiddenInput(), required=False)
    digital_upgrade         = forms.CharField(widget=forms.HiddenInput(), initial='0')
    full_quantity           = forms.CharField(widget=forms.HiddenInput(), initial='0')
    abridged_quantity       = forms.CharField(widget=forms.HiddenInput(), initial='0')

    class Meta:
        model = Order
        fields = [
            'stripe_single_use_token',
            'abridged_quantity', 'full_quantity', 'digital_upgrade'
        ]


class OrderBillingAddressForm(forms.ModelForm):
    billing_address         = forms.CharField(   label='Address',                    widget=forms.TextInput( attrs={'class': 'required input-xxlarge', 'placeholder': 'Enter Address...'}))
    billing_address2        = forms.CharField(   label='',                           widget=forms.TextInput( attrs={'class': 'input-xxlarge'}),     required=False)
    billing_country         = forms.ChoiceField( label='Country', choices=COUNTRIES, widget=forms.Select(    attrs={'class': 'countrySelect required'}))
    billing_us_state        = USStateField(      label='State',                      widget=USStateSelect(   attrs={'class': 'usStateSelect'}),     required=False)
    billing_state_province  = forms.CharField(   label='State / Province / Region',  widget=forms.TextInput( attrs={}),                             required=False)
    billing_city            = forms.CharField(   label='City',                       widget=forms.TextInput( attrs={'class': 'required', 'placeholder': 'Enter City...'}))
    billing_us_zip          = USZipCodeField(    label='ZIP Code',                   widget=forms.TextInput( attrs={'class': 'required zipcode'}),  required=False)
    billing_postal          = forms.CharField(   label='Postal Code',                widget=forms.TextInput( attrs={'class': 'required'}),          required=False)

    def clean(self):
        cleaned_data = super(OrderBillingAddressForm, self).clean()
        if cleaned_data['billing_country'] == 'US':
            # us_state and us_zip need to be filled
            if not cleaned_data.get('billing_us_state'):
                self._errors['billing_us_state'] = self.error_class([self.fields['billing_us_state'].error_messages['required']])
            if not cleaned_data.get('billing_us_zip'):
                self._errors['billing_us_zip'] = self.error_class([self.fields['billing_us_zip'].error_messages['required']])
        else:
            # state_province and postal need to be filled
            if not cleaned_data.get('billing_state_province'):
                self._errors['billing_state_province'] = self.error_class([self.fields['billing_state_province'].error_messages['required']])
            if not cleaned_data.get('billing_postal'):
                self._errors['billing_postal'] = self.error_class([self.fields['billing_postal'].error_messages['required']])
        return cleaned_data

    class Meta:
        model = Order
        fields = [
            'billing_address', 'billing_address2', 'billing_country', 'billing_city',
            'billing_state_province', 'billing_postal'
        ]


class OrderShippingAddressForm(forms.ModelForm):
    shipping_name            = forms.CharField(label='Name',                      widget=forms.TextInput(attrs={'class': 'required'}))
    shipping_address         = forms.CharField(label='Address',                   widget=forms.TextInput(attrs={'class': 'required input-xxlarge', 'placeholder': 'Enter Address...'}))
    shipping_address2        = forms.CharField(label='',                          widget=forms.TextInput(attrs={'class': 'input-xxlarge'}))
    shipping_country         = forms.ChoiceField(label='Country', choices=COUNTRIES, widget=forms.Select(attrs={'class': 'countrySelect required'}))
    shipping_us_state        = forms.CharField(label='State',                     widget=USStateSelect(attrs={'class': 'usStateSelect'}))
    shipping_state_province  = forms.CharField(label='State / Province / Region', widget=forms.TextInput(attrs={}))
    shipping_city            = forms.CharField(label='City',                      widget=forms.TextInput(attrs={'class': 'required', 'placeholder': 'Enter City...'}))
    shipping_us_zip          = USZipCodeField(label='ZIP Code',                    widget=forms.TextInput(attrs={'class': 'required zipcode'}))
    shipping_postal          = forms.CharField(label='Postal Code',         widget=forms.TextInput(attrs={'class': 'required'}))

    def clean(self):
        cleaned_data = super(OrderShippingAddressForm, self).clean()
        if cleaned_data['shipping_country'] == 'US':
            # us_state and us_zip need to be filled
            if not cleaned_data.get('shipping_us_state'):
                self._errors['shipping_us_state'] = self.error_class([self.fields['shipping_us_state'].error_messages['required']])
            if not cleaned_data.get('shipping_us_zip'):
                self._errors['shipping_us_zip'] = self.error_class([self.fields['shipping_us_zip'].error_messages['required']])
        else:
            # state_province and postal need to be filled
            if not cleaned_data.get('shipping_state_province'):
                self._errors['shipping_state_province'] = self.error_class([self.fields['shipping_state_province'].error_messages['required']])
            if not cleaned_data.get('shipping_postal'):
                self._errors['shipping_postal'] = self.error_class([self.fields['shipping_postal'].error_messages['required']])
        return cleaned_data

    class Meta:
        model = Order
        fields = [
            'shipping_name', 'shipping_address', 'shipping_address2',
            'shipping_country', 'shipping_city',
            'shipping_state_province', 'shipping_postal'
        ]


class CreditCardForm(forms.Form):
    name_on_card  = forms.CharField(label='Name on Card',       widget=forms.TextInput(attrs={'class': 'required'}))
    card_number   = forms.CharField(label='Credit Card Number', widget=forms.TextInput(attrs={'class': 'required creditcard'}))
    exp_month     = forms.CharField(label='Expiration (MM/YY)', widget=forms.TextInput(attrs={'class': 'required input-mini', 'maxlength': '2'}))
    exp_year      = forms.CharField(label='',                   widget=forms.TextInput(attrs={'class': 'required input-mini', 'maxlength': '2'}))
    cvv_code      = forms.CharField(label='Security Code',      widget=forms.TextInput(attrs={'class': 'required cvccode input-mini', 'maxlength': '4'}))
