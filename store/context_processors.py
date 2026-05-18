from django.conf import settings


def currency(request):
    return {
        'currency_symbol': getattr(settings, 'CURRENCY_SYMBOL', 'KES'),
    }

def google_analytics(request):
    from django.conf import settings
    return {
        'GTM_ID': getattr(settings, 'GOOGLE_TAG_MANAGER_ID', ''),
        'GA_ID': getattr(settings, 'GOOGLE_ANALYTICS_ID', ''),
    }