from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.views.static import serve
from django.contrib.sitemaps.views import sitemap
from django.http import HttpResponse
import os
from . import views

# Import your sitemaps
from .sitemap import StaticViewSitemap, WasteListingSitemap, ProfileSitemap

sitemaps = {
    'static': StaticViewSitemap,
    # 'waste_listings': WasteListingSitemap,
    # 'profiles': ProfileSitemap,
}

def google_verification(request):
    """Direct serve Google verification file"""
    verification_content = "google-site-verification: google00cc440b909d6e2d.html"
    return HttpResponse(verification_content, content_type='text/plain')

def serve_google_verification_file(request):
    """Serve Google verification file directly from filesystem"""
    try:
        file_path = os.path.join(settings.BASE_DIR, 'google00cc440b909d6e2d.html')
        with open(file_path, 'r') as f:
            content = f.read()
        return HttpResponse(content, content_type='text/plain')
    except FileNotFoundError:
        # Fallback to template if file doesn't exist
        return TemplateView.as_view(
            template_name='google00cc440b909d6e2d.html',
            content_type='text/plain'
        )(request)

def health_check(request):
    """Simple health check endpoint for Render"""
    return HttpResponse("OK", status=200)

urlpatterns = [
    path('', views.home, name='home'),
    path('admin/', admin.site.urls),
    path('users/', include('users.urls')),
    path('waste/', include('waste.urls')),
    path('matching/', include('matching.urls')),
    path('analytics/', include('analytics.urls')),
    path('education/', include('education.urls')),
    path('educ/', include('educ.urls')),
    path('report/', include('report.urls')),
    path('chatbot/', include('chatbot.urls')),
    
    # SEO URLs
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('robots.txt', TemplateView.as_view(
        template_name='robots.txt', 
        content_type='text/plain'
    )),
    
    # Health check for Render
    path('health/', health_check, name='health_check'),

    # Multiple methods for Google verification
    path('google00cc440b909d6e2d.html', google_verification),  # Method 1: Direct response
    path('google-verification/', serve_google_verification_file),  # Method 2: File system
]

# Serve media files in production (for Render)
if not settings.DEBUG:
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', serve, {
            'document_root': settings.MEDIA_ROOT,
        }),
    ]

# Serve static and media files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Fallback for static files in production (already handled by WhiteNoise)
