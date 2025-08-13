from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from ckeditor_uploader.fields import RichTextUploadingField
from taggit.managers import TaggableManager
from PIL import Image
import os
from .utils import optimize_image, create_thumbnail, get_upload_path


class Category(models.Model):
    """News categories like Politics, Sports, Business, etc."""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=7, default='#007bff', help_text='Hex color code')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('news:category_detail', kwargs={'slug': self.slug})


class Author(models.Model):
    """Extended user profile for authors"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    profile_image = models.ImageField(upload_to=get_upload_path, blank=True, null=True)
    social_twitter = models.URLField(blank=True)
    social_facebook = models.URLField(blank=True)
    social_linkedin = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}" or self.user.username

    def get_full_name(self):
        return f"{self.user.first_name} {self.user.last_name}".strip() or self.user.username


class Article(models.Model):
    """Main article model"""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    subtitle = models.CharField(max_length=300, blank=True, help_text='Optional subtitle')
    content = RichTextUploadingField()
    excerpt = models.TextField(max_length=500, blank=True, help_text='Brief summary of the article')

    # Relationships
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='articles')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='articles')
    tags = TaggableManager(blank=True)

    # Media
    featured_image = models.ImageField(upload_to=get_upload_path, blank=True, null=True)
    featured_image_alt = models.CharField(max_length=200, blank=True, help_text='Alt text for featured image')
    featured_image_thumbnail = models.ImageField(upload_to='thumbnails/', blank=True, null=True, editable=False)

    # Status and visibility
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    is_featured = models.BooleanField(default=False, help_text='Show on homepage as featured')
    is_breaking = models.BooleanField(default=False, help_text='Mark as breaking news')

    # SEO fields
    meta_description = models.CharField(max_length=160, blank=True, help_text='SEO meta description')
    meta_keywords = models.CharField(max_length=200, blank=True, help_text='SEO keywords, comma separated')

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(blank=True, null=True)

    # Analytics
    views_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-published_at', '-created_at']
        indexes = [
            models.Index(fields=['status', 'published_at']),
            models.Index(fields=['category', 'status']),
            models.Index(fields=['is_featured', 'status']),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)

        # Set published_at when status changes to published
        if self.status == 'published' and not self.published_at:
            self.published_at = timezone.now()

        # Handle image optimization
        if self.featured_image:
            # Create thumbnail if it doesn't exist
            if not self.featured_image_thumbnail:
                thumbnail_result = create_thumbnail(self.featured_image)
                if thumbnail_result:
                    thumbnail_name, thumbnail_content = thumbnail_result
                    self.featured_image_thumbnail.save(
                        thumbnail_name,
                        thumbnail_content,
                        save=False
                    )

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('news:article_detail', kwargs={'slug': self.slug})

    def get_reading_time(self):
        """Calculate estimated reading time in minutes"""
        word_count = len(self.content.split())
        reading_time = word_count / 200  # Average reading speed
        return max(1, round(reading_time))

    @property
    def is_published(self):
        return self.status == 'published' and self.published_at and self.published_at <= timezone.now()


class Comment(models.Model):
    """Comments on articles"""
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='comments')
    name = models.CharField(max_length=100)
    email = models.EmailField()
    website = models.URLField(blank=True)
    content = models.TextField()
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    # For nested comments (replies)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, related_name='replies')

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'Comment by {self.name} on {self.article.title}'


class Newsletter(models.Model):
    """Newsletter subscription model"""
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email


class ContactMessage(models.Model):
    """Contact form messages"""
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Message from {self.name} - {self.subject}'


class SiteSettings(models.Model):
    """Site-wide settings"""
    site_name = models.CharField(max_length=100, default='News Portal')
    site_description = models.TextField(blank=True)
    site_logo = models.ImageField(upload_to='site/', blank=True, null=True)
    site_favicon = models.ImageField(upload_to='site/', blank=True, null=True)

    # Contact information
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=20, blank=True)
    contact_address = models.TextField(blank=True)

    # Social media links
    facebook_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    youtube_url = models.URLField(blank=True)

    # SEO
    meta_description = models.CharField(max_length=160, blank=True)
    meta_keywords = models.CharField(max_length=200, blank=True)

    # Analytics
    google_analytics_id = models.CharField(max_length=50, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Site Settings'
        verbose_name_plural = 'Site Settings'

    def __str__(self):
        return self.site_name
