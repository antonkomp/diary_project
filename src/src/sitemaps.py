from django.contrib.sitemaps import Sitemap
from django.urls import reverse


class HomePageSitemap(Sitemap):
    priority = 1.0
    changefreq = 'weekly'

    def items(self):
        return ['main']

    def location(self, item):
        return reverse(item)
