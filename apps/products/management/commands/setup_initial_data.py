from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.products.models import Product

User = get_user_model()


class Command(BaseCommand):
    help = 'Set up initial data for the snacks payment system'

    def handle(self, *args, **options):
        self.stdout.write('Setting up initial data...')
        
        # Create products if they don't exist
        mandazi, created = Product.objects.get_or_create(
            name='MANDAZI',
            defaults={
                'price': 10.00,
                'description': 'Fresh mandazi',
                'is_available': True
            }
        )
        if created:
            self.stdout.write(
                self.style.SUCCESS(f'Created product: {mandazi.get_name_display()}')
            )
        else:
            self.stdout.write(f'Product already exists: {mandazi.get_name_display()}')
        
        eggs, created = Product.objects.get_or_create(
            name='EGGS',
            defaults={
                'price': 15.00,
                'description': 'Boiled eggs',
                'is_available': True
            }
        )
        if created:
            self.stdout.write(
                self.style.SUCCESS(f'Created product: {eggs.get_name_display()}')
            )
        else:
            self.stdout.write(f'Product already exists: {eggs.get_name_display()}')
        
        self.stdout.write(
            self.style.SUCCESS('Initial data setup completed!')
        )