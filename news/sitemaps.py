from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from django.utils import timezone
from .models import Article, Category, Author
from taggit.models import Tag


class ArticleSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.8

    def items(self):
        return Article.objects.filter(
            status='published',
            published_at__lte=timezone.now()
        ).select_related('category')

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return obj.get_absolute_url()


class CategorySitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.6

    def items(self):
        return Category.objects.filter(is_active=True)

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return obj.get_absolute_url()


class TagSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.4

    def items(self):
        return Tag.objects.all()

    def location(self, obj):
        return reverse('news:tag_detail', kwargs={'slug': obj.slug})


class AuthorSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.5

    def items(self):
        return Author.objects.filter(is_active=True)

    def lastmod(self, obj):
        return obj.created_at

    def location(self, obj):
        return reverse('news:author_detail', kwargs={'pk': obj.pk})


class StaticViewSitemap(Sitemap):
    priority = 0.5
    changefreq = 'monthly'

    def items(self):
        return ['news:home', 'news:contact']

    def location(self, item):
        return reverse(item)
