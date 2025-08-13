from django.core.cache import cache
from django.db.models import Q, Count
from .models import Category, Article


def global_context(request):
    """
    Context processor to provide global data across all templates
    """
    # Try to get data from cache first
    cache_key = 'global_context_data'
    cached_data = cache.get(cache_key)
    
    if cached_data:
        return cached_data
    
    # Categories for navigation
    categories = Category.objects.filter(
        is_active=True
    ).annotate(
        article_count=Count('articles', filter=Q(articles__status='published'))
    )[:8]  # Limit to 8 categories for navigation
    
    # Breaking news for ticker
    breaking_news = Article.objects.filter(
        status='published',
        is_breaking=True
    ).select_related('category')[:5]
    
    context_data = {
        'categories': categories,
        'breaking_news': breaking_news,
    }
    
    # Cache for 15 minutes
    cache.set(cache_key, context_data, 60 * 15)
    
    return context_data
