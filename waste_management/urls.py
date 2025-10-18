from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.contrib.sitemaps.views import sitemap
from . import views

# Import your sitemaps
from .sitemap import StaticViewSitemap, WasteListingSitemap, ProfileSitemap

sitemaps = {
    'static': StaticViewSitemap,
    # 'waste_listings': WasteListingSitemap,  # Uncomment if you have these models
    # 'profiles': ProfileSitemap,  # Uncomment if you have these models
}

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
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)