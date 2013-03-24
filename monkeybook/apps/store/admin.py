from django.contrib import admin
from voomza.apps.store.models import StoreProfile, Order


class StoreProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'stripe_customer_id')

class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'created', 'stripe_single_use_token',
                    'charged_total', 'get_total', 'abridged_quantity',
                    'full_quantity', 'digital_upgrade',

                    'billing_address', 'billing_address2', 'billing_city',
                    'billing_state_province', 'billing_postal', 'billing_country',

                    'shipping_name',
                    'shipping_address', 'shipping_address2', 'shipping_city',
                    'shipping_state_province', 'shipping_postal', 'shipping_country',
    )


admin.site.register(StoreProfile, StoreProfileAdmin)
admin.site.register(Order, OrderAdmin)
