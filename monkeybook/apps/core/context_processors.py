def analytics(request):
    from django.conf import settings
    return {
        'MIXPANEL_API_TOKEN': settings.MIXPANEL_API_TOKEN,
        'IS_LIVE': settings.IS_LIVE,
    }