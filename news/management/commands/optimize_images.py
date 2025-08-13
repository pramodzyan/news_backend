from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from news.models import Article, Author
from news.utils import optimize_image, create_thumbnail
import os


class Command(BaseCommand):
    help = 'Optimize existing images in the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force optimization even if optimized version exists',
        )

    def handle(self, *args, **options):
        self.stdout.write('Starting image optimization...')
        
        force = options['force']
        optimized_count = 0
        thumbnail_count = 0
        
        # Optimize article featured images
        articles = Article.objects.filter(featured_image__isnull=False)
        self.stdout.write(f'Found {articles.count()} articles with featured images')
        
        for article in articles:
            try:
                # Create thumbnail if it doesn't exist or force is True
                if not article.featured_image_thumbnail or force:
                    thumbnail_result = create_thumbnail(article.featured_image)
                    if thumbnail_result:
                        thumbnail_name, thumbnail_content = thumbnail_result
                        article.featured_image_thumbnail.save(
                            thumbnail_name, 
                            thumbnail_content, 
                            save=False
                        )
                        article.save(update_fields=['featured_image_thumbnail'])
                        thumbnail_count += 1
                        self.stdout.write(f'Created thumbnail for article: {article.title}')
                
                # Optimize main image if needed
                if force:
                    optimize_result = optimize_image(article.featured_image)
                    if optimize_result:
                        optimized_name, optimized_content = optimize_result
                        article.featured_image.save(
                            optimized_name,
                            optimized_content,
                            save=False
                        )
                        article.save(update_fields=['featured_image'])
                        optimized_count += 1
                        self.stdout.write(f'Optimized image for article: {article.title}')
                        
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error processing article {article.title}: {e}')
                )
        
        # Optimize author profile images
        authors = Author.objects.filter(profile_image__isnull=False)
        self.stdout.write(f'Found {authors.count()} authors with profile images')
        
        for author in authors:
            try:
                if force:
                    optimize_result = optimize_image(author.profile_image, max_width=400, max_height=400)
                    if optimize_result:
                        optimized_name, optimized_content = optimize_result
                        author.profile_image.save(
                            optimized_name,
                            optimized_content,
                            save=False
                        )
                        author.save(update_fields=['profile_image'])
                        optimized_count += 1
                        self.stdout.write(f'Optimized profile image for author: {author.get_full_name()}')
                        
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error processing author {author.get_full_name()}: {e}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Image optimization completed! '
                f'Optimized: {optimized_count} images, '
                f'Created: {thumbnail_count} thumbnails'
            )
        )
