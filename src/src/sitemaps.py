from django.contrib.sitemaps import Sitemap
from django.urls import reverse


class HomePageSitemap(Sitemap):
    priority = 0.9
    changefreq = 'weekly'

    def items(self):
        return ['main']

    def location(self, item):
        return reverse(item)

