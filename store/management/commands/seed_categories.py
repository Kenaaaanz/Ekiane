from django.core.management.base import BaseCommand
from store.models import Category


class Command(BaseCommand):
    help = 'Create product categories for Ekiane Luxury Organics'

    def handle(self, *args, **options):
        categories_data = [
            {'name': 'Shea Butter', 'slug': 'shea-butter', 'description': 'Premium organic shea butter for deep moisturizing and hair nourishment'},
            {'name': 'Shampoo', 'slug': 'shampoo', 'description': 'Natural shampoos formulated to cleanse and revitalize your hair'},
            {'name': 'Conditioner', 'slug': 'conditioner', 'description': 'Rich conditioners designed for optimal hydration and shine'},
            {'name': 'Beard Oil', 'slug': 'beard-oil', 'description': 'Premium beard oils for grooming and facial hair care'},
        ]

        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                slug=cat_data['slug'],
                defaults={
                    'name': cat_data['name'],
                    'description': cat_data['description'],
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created category: {category.name}'))
            else:
                self.stdout.write(self.style.WARNING(f'Category already exists: {category.name}'))

        self.stdout.write(self.style.SUCCESS('Categories initialized successfully!'))
