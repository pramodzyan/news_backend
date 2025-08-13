from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import (
    Category, Author, Article, Comment,
    Newsletter, ContactMessage, SiteSettings
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'article_count', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'updated_at']

    def article_count(self, obj):
        return obj.articles.filter(status='published').count()
    article_count.short_description = 'Published Articles'


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ['get_full_name', 'user_email', 'article_count', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['user__first_name', 'user__last_name', 'user__username', 'user__email']
    readonly_fields = ['created_at']

    def get_full_name(self, obj):
        return obj.get_full_name()
    get_full_name.short_description = 'Full Name'

    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'Email'

    def article_count(self, obj):
        return obj.articles.filter(status='published').count()
    article_count.short_description = 'Published Articles'


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    readonly_fields = ['created_at']
    fields = ['name', 'email', 'content', 'is_approved', 'created_at']


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'author', 'category', 'status', 'is_featured',
        'is_breaking', 'views_count', 'published_at'
    ]
    list_filter = [
        'status', 'is_featured', 'is_breaking', 'category',
        'created_at', 'published_at'
    ]
    search_fields = ['title', 'content', 'excerpt']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['views_count', 'created_at', 'updated_at', 'get_reading_time']
    inlines = [CommentInline]

    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'subtitle', 'author', 'category')
        }),
        ('Content', {
            'fields': ('content', 'excerpt', 'tags')
        }),
        ('Media', {
            'fields': ('featured_image', 'featured_image_alt')
        }),
        ('Status & Visibility', {
            'fields': ('status', 'is_featured', 'is_breaking', 'published_at')
        }),
        ('SEO', {
            'fields': ('meta_description', 'meta_keywords'),
            'classes': ('collapse',)
        }),
        ('Statistics', {
            'fields': ('views_count', 'get_reading_time', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    def get_reading_time(self, obj):
        return f"{obj.get_reading_time()} min"
    get_reading_time.short_description = 'Reading Time'

    def save_model(self, request, obj, form, change):
        if not change:  # If creating new article
            if not hasattr(obj, 'author') or not obj.author:
                # Try to get or create author for current user
                author, created = Author.objects.get_or_create(
                    user=request.user,
                    defaults={'bio': f'Author: {request.user.get_full_name() or request.user.username}'}
                )
                obj.author = author

        # Set published_at when status changes to published
        if obj.status == 'published' and not obj.published_at:
            obj.published_at = timezone.now()

        super().save_model(request, obj, form, change)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['name', 'article', 'is_approved', 'created_at']
    list_filter = ['is_approved', 'created_at']
    search_fields = ['name', 'email', 'content']
    readonly_fields = ['created_at']
    actions = ['approve_comments', 'disapprove_comments']

    def approve_comments(self, request, queryset):
        queryset.update(is_approved=True)
        self.message_user(request, f'{queryset.count()} comments approved.')
    approve_comments.short_description = 'Approve selected comments'

    def disapprove_comments(self, request, queryset):
        queryset.update(is_approved=False)
        self.message_user(request, f'{queryset.count()} comments disapproved.')
    disapprove_comments.short_description = 'Disapprove selected comments'


@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ['email', 'is_active', 'subscribed_at']
    list_filter = ['is_active', 'subscribed_at']
    search_fields = ['email']
    readonly_fields = ['subscribed_at']
    actions = ['activate_subscriptions', 'deactivate_subscriptions']

    def activate_subscriptions(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, f'{queryset.count()} subscriptions activated.')
    activate_subscriptions.short_description = 'Activate selected subscriptions'

    def deactivate_subscriptions(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, f'{queryset.count()} subscriptions deactivated.')
    deactivate_subscriptions.short_description = 'Deactivate selected subscriptions'


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'subject', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at']
    search_fields = ['name', 'email', 'subject', 'message']
    readonly_fields = ['created_at']
    actions = ['mark_as_read', 'mark_as_unread']

    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
        self.message_user(request, f'{queryset.count()} messages marked as read.')
    mark_as_read.short_description = 'Mark selected messages as read'

    def mark_as_unread(self, request, queryset):
        queryset.update(is_read=False)
        self.message_user(request, f'{queryset.count()} messages marked as unread.')
    mark_as_unread.short_description = 'Mark selected messages as unread'


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Basic Information', {
            'fields': ('site_name', 'site_description', 'site_logo', 'site_favicon')
        }),
        ('Contact Information', {
            'fields': ('contact_email', 'contact_phone', 'contact_address')
        }),
        ('Social Media', {
            'fields': ('facebook_url', 'twitter_url', 'instagram_url', 'youtube_url')
        }),
        ('SEO', {
            'fields': ('meta_description', 'meta_keywords')
        }),
        ('Analytics', {
            'fields': ('google_analytics_id',)
        })
    )

    def has_add_permission(self, request):
        # Only allow one SiteSettings instance
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        # Don't allow deletion of SiteSettings
        return False


# Customize admin site header and title
admin.site.site_header = 'News Portal Administration'
admin.site.site_title = 'News Portal Admin'
admin.site.index_title = 'Welcome to News Portal Administration'
