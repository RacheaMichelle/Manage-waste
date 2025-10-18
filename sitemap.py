from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from waste.models import WasteListing
from users.models import Profile

class StaticViewSitemap(Sitemap):
    priority = 0.8
    changefreq = 'weekly'

    def items(self):
        return [
            'home',
            'login', 
            'register',
            'resources',
            'waste_quiz',
            'report_dumping',
            # Add more static URLs as needed
        ]

    def location(self, item):
        return reverse(item)

# If you have WasteListing model
class WasteListingSitemap(Sitemap):
    changefreq = 'daily'
    priority = 0.9

    def items(self):
        return WasteListing.objects.filter(is_active=True)

    def lastmod(self, obj):
        return obj.updated_at

# If you have Profile model
class ProfileSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.7

    def items(self):
        return Profile.objects.all()

    def location(self, obj):
        return reverse('profile_detail', kwargs={'pk': obj.pk})

# If you don't have the models yet, use this simplified version:
sitemaps = {
    'static': StaticViewSitemap,
}