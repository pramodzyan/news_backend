from django.urls import path
from . import views

app_name = 'news'

urlpatterns = [
    # Homepage
    path('', views.HomeView.as_view(), name='home'),
    
    # Article URLs
    path('article/<slug:slug>/', views.ArticleDetailView.as_view(), name='article_detail'),
    
    # Category URLs
    path('category/<slug:slug>/', views.CategoryDetailView.as_view(), name='category_detail'),
    
    # Tag URLs
    path('tag/<slug:slug>/', views.TagDetailView.as_view(), name='tag_detail'),
    
    # Search
    path('search/', views.SearchView.as_view(), name='search'),
    
    # Author profile
    path('author/<int:pk>/', views.AuthorDetailView.as_view(), name='author_detail'),
    
    # Contact
    path('contact/', views.ContactView.as_view(), name='contact'),
    
    # Newsletter subscription
    path('newsletter/subscribe/', views.NewsletterSubscribeView.as_view(), name='newsletter_subscribe'),
    
    # API endpoints for AJAX
    path('api/articles/trending/', views.TrendingArticlesView.as_view(), name='trending_articles'),
]
