from django.conf import settings

def seo_context(request):
    return {
        'SITE_NAME': getattr(settings, 'SITE_NAME', 'Clean Uganda'),
        'SITE_DESCRIPTION': getattr(settings, 'SITE_DESCRIPTION', 'Waste Management Platform'),
        'META_KEYWORDS': getattr(settings, 'META_KEYWORDS', 'waste management, recycling, Uganda'),
    }