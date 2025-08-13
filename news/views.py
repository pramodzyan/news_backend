from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, TemplateView
from django.views.generic.edit import CreateView
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Count, Prefetch
from django.core.paginator import Paginator
from django.utils import timezone
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.core.cache import cache
from taggit.models import Tag
from .models import Article, Category, Author, Comment, Newsletter, ContactMessage


@method_decorator(cache_page(60 * 5), name='dispatch')  # Cache for 5 minutes
class HomeView(ListView):
    """Homepage view with featured and latest articles"""
    model = Article
    template_name = 'news/home.html'
    context_object_name = 'articles'
    paginate_by = 10

    def get_queryset(self):
        return Article.objects.filter(
            status='published',
            published_at__lte=timezone.now()
        ).select_related('author__user', 'category').prefetch_related('tags')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Try to get data from cache first
        cache_key = 'homepage_data'
        cached_data = cache.get(cache_key)

        if cached_data:
            context.update(cached_data)
        else:
            # Featured articles
            featured_articles = Article.objects.filter(
                status='published',
                is_featured=True,
                published_at__lte=timezone.now()
            ).select_related('author__user', 'category').prefetch_related('tags')[:5]

            # Breaking news
            breaking_news = Article.objects.filter(
                status='published',
                is_breaking=True,
                published_at__lte=timezone.now()
            ).select_related('author__user', 'category')[:3]

            # Categories with article count
            categories = Category.objects.filter(
                is_active=True
            ).annotate(
                article_count=Count('articles', filter=Q(articles__status='published'))
            )

            # Popular tags
            popular_tags = Tag.objects.all()[:10]

            cached_data = {
                'featured_articles': featured_articles,
                'breaking_news': breaking_news,
                'categories': categories,
                'popular_tags': popular_tags,
            }

            # Cache for 10 minutes
            cache.set(cache_key, cached_data, 60 * 10)
            context.update(cached_data)

        return context


class ArticleDetailView(DetailView):
    """Individual article detail view"""
    model = Article
    template_name = 'news/article_detail.html'
    context_object_name = 'article'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        return Article.objects.filter(
            status='published',
            published_at__lte=timezone.now()
        ).select_related('author__user', 'category').prefetch_related('tags')

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        # Increment view count using F() to avoid race conditions
        from django.db.models import F
        Article.objects.filter(id=obj.id).update(views_count=F('views_count') + 1)
        # Refresh the object to get updated view count
        obj.refresh_from_db(fields=['views_count'])
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Related articles with optimized query
        context['related_articles'] = Article.objects.filter(
            category=self.object.category,
            status='published',
            published_at__lte=timezone.now()
        ).exclude(id=self.object.id).select_related('author__user', 'category')[:4]

        # Comments with prefetch for replies
        context['comments'] = self.object.comments.filter(
            is_approved=True,
            parent=None
        ).prefetch_related('replies').order_by('created_at')

        return context


class CategoryDetailView(ListView):
    """Category-wise article listing"""
    model = Article
    template_name = 'news/category_detail.html'
    context_object_name = 'articles'
    paginate_by = 12

    def get_queryset(self):
        self.category = get_object_or_404(Category, slug=self.kwargs['slug'])
        return Article.objects.filter(
            category=self.category,
            status='published',
            published_at__lte=timezone.now()
        ).select_related('author__user', 'category')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context


class TagDetailView(ListView):
    """Tag-wise article listing"""
    model = Article
    template_name = 'news/tag_detail.html'
    context_object_name = 'articles'
    paginate_by = 12

    def get_queryset(self):
        self.tag = get_object_or_404(Tag, slug=self.kwargs['slug'])
        return Article.objects.filter(
            tags=self.tag,
            status='published',
            published_at__lte=timezone.now()
        ).select_related('author__user', 'category')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tag'] = self.tag
        return context


class AuthorDetailView(DetailView):
    """Author profile and articles"""
    model = Author
    template_name = 'news/author_detail.html'
    context_object_name = 'author'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['articles'] = Article.objects.filter(
            author=self.object,
            status='published',
            published_at__lte=timezone.now()
        ).select_related('category')[:10]
        return context


class SearchView(ListView):
    """Search functionality"""
    model = Article
    template_name = 'news/search_results.html'
    context_object_name = 'articles'
    paginate_by = 10

    def get_queryset(self):
        query = self.request.GET.get('q', '')
        if query:
            return Article.objects.filter(
                Q(title__icontains=query) |
                Q(content__icontains=query) |
                Q(excerpt__icontains=query),
                status='published',
                published_at__lte=timezone.now()
            ).select_related('author__user', 'category')
        return Article.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        return context


class ContactView(CreateView):
    """Contact form view"""
    model = ContactMessage
    template_name = 'news/contact.html'
    fields = ['name', 'email', 'subject', 'message']
    success_url = '/contact/'

    def form_valid(self, form):
        messages.success(self.request, 'Your message has been sent successfully!')
        return super().form_valid(form)


class NewsletterSubscribeView(TemplateView):
    """Newsletter subscription via AJAX"""

    def post(self, request, *args, **kwargs):
        email = request.POST.get('email')
        if email:
            newsletter, created = Newsletter.objects.get_or_create(email=email)
            if created:
                return JsonResponse({'success': True, 'message': 'Successfully subscribed!'})
            else:
                return JsonResponse({'success': False, 'message': 'Email already subscribed!'})
        return JsonResponse({'success': False, 'message': 'Invalid email!'})


class TrendingArticlesView(TemplateView):
    """API endpoint for trending articles"""

    def get(self, request, *args, **kwargs):
        articles = Article.objects.filter(
            status='published',
            published_at__lte=timezone.now()
        ).order_by('-views_count')[:5]

        data = [{
            'title': article.title,
            'url': article.get_absolute_url(),
            'views': article.views_count,
            'category': article.category.name
        } for article in articles]

        return JsonResponse({'articles': data})
