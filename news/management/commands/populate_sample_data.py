from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from news.models import Category, Author, Article
import random


class Command(BaseCommand):
    help = 'Populate the database with sample news data'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')
        
        # Create categories
        categories_data = [
            {'name': 'Politics', 'color': '#dc3545', 'description': 'Political news and updates'},
            {'name': 'Sports', 'color': '#28a745', 'description': 'Sports news and scores'},
            {'name': 'Business', 'color': '#007bff', 'description': 'Business and economy news'},
            {'name': 'Technology', 'color': '#6f42c1', 'description': 'Tech news and innovations'},
            {'name': 'Entertainment', 'color': '#fd7e14', 'description': 'Entertainment and celebrity news'},
            {'name': 'Health', 'color': '#20c997', 'description': 'Health and wellness news'},
            {'name': 'World', 'color': '#6c757d', 'description': 'International news'},
            {'name': 'Education', 'color': '#ffc107', 'description': 'Education news and updates'},
        ]
        
        categories = []
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={
                    'color': cat_data['color'],
                    'description': cat_data['description']
                }
            )
            categories.append(category)
            if created:
                self.stdout.write(f'Created category: {category.name}')
        
        # Create sample users and authors
        users_data = [
            {'username': 'john_doe', 'first_name': 'John', 'last_name': 'Doe', 'email': 'john@example.com'},
            {'username': 'jane_smith', 'first_name': 'Jane', 'last_name': 'Smith', 'email': 'jane@example.com'},
            {'username': 'mike_wilson', 'first_name': 'Mike', 'last_name': 'Wilson', 'email': 'mike@example.com'},
            {'username': 'sarah_johnson', 'first_name': 'Sarah', 'last_name': 'Johnson', 'email': 'sarah@example.com'},
        ]
        
        authors = []
        for user_data in users_data:
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults={
                    'first_name': user_data['first_name'],
                    'last_name': user_data['last_name'],
                    'email': user_data['email'],
                    'is_staff': True
                }
            )
            if created:
                user.set_password('password123')
                user.save()
            
            author, created = Author.objects.get_or_create(
                user=user,
                defaults={
                    'bio': f'Experienced journalist specializing in various news topics. {user.get_full_name()} has been reporting for over 5 years.'
                }
            )
            authors.append(author)
            if created:
                self.stdout.write(f'Created author: {author.get_full_name()}')
        
        # Sample article data
        articles_data = [
            {
                'title': 'Breaking: Major Political Development Shakes the Nation',
                'subtitle': 'Government announces new policy changes affecting millions',
                'content': '''<p>In a significant political development, the government has announced sweeping policy changes that are expected to impact millions of citizens across the country. The announcement came during a press conference held at the capital.</p>
                
                <p>The new policies focus on economic reform, healthcare improvements, and educational initiatives. Officials believe these changes will bring positive transformation to the nation's infrastructure and social services.</p>
                
                <p>Opposition parties have expressed mixed reactions to the announcement, with some welcoming the reforms while others raising concerns about implementation timelines and budget allocations.</p>''',
                'excerpt': 'Government announces major policy changes in a significant political development affecting millions of citizens nationwide.',
                'category': 'Politics',
                'is_featured': True,
                'is_breaking': True,
            },
            {
                'title': 'Tech Giants Announce Revolutionary AI Breakthrough',
                'subtitle': 'New artificial intelligence system promises to transform industries',
                'content': '''<p>Leading technology companies have unveiled a groundbreaking artificial intelligence system that promises to revolutionize multiple industries. The announcement was made at the annual Tech Innovation Summit.</p>
                
                <p>The new AI system demonstrates unprecedented capabilities in natural language processing, image recognition, and predictive analytics. Industry experts believe this breakthrough could accelerate digital transformation across various sectors.</p>
                
                <p>The technology is expected to be available for commercial use within the next two years, with pilot programs beginning in select markets early next year.</p>''',
                'excerpt': 'Tech companies reveal revolutionary AI system with potential to transform multiple industries and accelerate digital innovation.',
                'category': 'Technology',
                'is_featured': True,
            },
            {
                'title': 'Championship Finals Draw Record-Breaking Viewership',
                'subtitle': 'Sports event attracts largest audience in tournament history',
                'content': '''<p>The championship finals have attracted a record-breaking television audience, making it the most-watched sporting event in the tournament's history. Millions of fans tuned in to witness the thrilling competition.</p>
                
                <p>The match featured outstanding performances from both teams, with spectacular plays and dramatic moments that kept viewers on the edge of their seats throughout the event.</p>
                
                <p>Broadcasting networks report that streaming numbers also reached new heights, indicating the growing popularity of digital sports consumption among younger demographics.</p>''',
                'excerpt': 'Championship finals break viewership records, becoming the most-watched sporting event in tournament history.',
                'category': 'Sports',
                'is_featured': False,
            },
            {
                'title': 'Global Markets Show Strong Recovery Signs',
                'subtitle': 'Economic indicators point to sustained growth across major economies',
                'content': '''<p>Global financial markets are showing strong signs of recovery, with major economic indicators pointing to sustained growth across developed and emerging economies. Market analysts express cautious optimism about the economic outlook.</p>
                
                <p>Stock markets have reached new highs in several countries, while unemployment rates continue to decline. Consumer confidence indices also show improvement, suggesting increased spending and investment activity.</p>
                
                <p>However, experts warn that challenges remain, including inflation concerns and geopolitical tensions that could impact future economic stability.</p>''',
                'excerpt': 'Global markets demonstrate strong recovery with positive economic indicators across major economies worldwide.',
                'category': 'Business',
            },
            {
                'title': 'Medical Breakthrough Offers Hope for Rare Disease Patients',
                'subtitle': 'New treatment shows promising results in clinical trials',
                'content': '''<p>Researchers have announced a significant medical breakthrough that offers new hope for patients suffering from a rare genetic disease. The innovative treatment has shown promising results in recent clinical trials.</p>
                
                <p>The therapy targets specific genetic mutations responsible for the condition, potentially providing relief for thousands of patients worldwide who previously had limited treatment options.</p>
                
                <p>Medical professionals are optimistic about the treatment's potential, though they emphasize that more research is needed before it becomes widely available to patients.</p>''',
                'excerpt': 'Medical researchers announce breakthrough treatment offering hope for rare disease patients through innovative therapy.',
                'category': 'Health',
            },
        ]
        
        # Create articles
        for i, article_data in enumerate(articles_data):
            category = Category.objects.get(name=article_data['category'])
            author = random.choice(authors)
            
            article, created = Article.objects.get_or_create(
                title=article_data['title'],
                defaults={
                    'subtitle': article_data['subtitle'],
                    'content': article_data['content'],
                    'excerpt': article_data['excerpt'],
                    'author': author,
                    'category': category,
                    'status': 'published',
                    'is_featured': article_data.get('is_featured', False),
                    'is_breaking': article_data.get('is_breaking', False),
                    'published_at': timezone.now(),
                    'views_count': random.randint(100, 5000),
                }
            )
            
            if created:
                # Add some tags
                tags = ['news', 'breaking', 'update', 'important', 'trending']
                article.tags.add(*random.sample(tags, random.randint(1, 3)))
                self.stdout.write(f'Created article: {article.title}')
        
        self.stdout.write(
            self.style.SUCCESS('Successfully populated database with sample data!')
        )
