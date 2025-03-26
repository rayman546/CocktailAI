import os
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import transaction
from django.conf import settings
import time


class Command(BaseCommand):
    help = 'Loads all demo fixture data in the correct order'

    def add_arguments(self, parser):
        parser.add_argument(
            '--flush',
            action='store_true',
            help='Flush the database before loading fixtures',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        start_time = time.time()
        
        if options['flush']:
            self.stdout.write(self.style.WARNING('Flushing database...'))
            call_command('flush', '--noinput')
            self.stdout.write(self.style.SUCCESS('Database flushed successfully'))
        
        # Order matters due to foreign key relationships
        fixtures = [
            # Users first since they're referenced by other models
            'accounts/fixtures/admin_user.json',
            
            # Base inventory models
            'inventory/fixtures/categories.json',
            'inventory/fixtures/suppliers.json',
            'inventory/fixtures/locations.json',
            
            # Products depend on categories and suppliers
            'inventory/fixtures/products.json',
            
            # Inventory items depend on products and locations
            'inventory/fixtures/inventory_items.json',
            
            # Transactions depend on products, locations, and users
            'inventory/fixtures/transactions.json',
            
            # Menu data
            'menu/fixtures/recipe_categories.json',
            'menu/fixtures/recipes.json',  # Has recipe ingredients nested
            'menu/fixtures/menus.json',  # Depends on recipes
        ]
        
        total_fixtures = len(fixtures)
        loaded_fixtures = 0
        
        for fixture in fixtures:
            try:
                self.stdout.write(f'Loading fixture: {fixture}')
                call_command('loaddata', fixture)
                loaded_fixtures += 1
                self.stdout.write(self.style.SUCCESS(f'Successfully loaded {fixture}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Failed to load {fixture}: {str(e)}'))
                # Since we're in a transaction, this will roll back all changes
                raise
        
        elapsed_time = time.time() - start_time
        self.stdout.write(self.style.SUCCESS(
            f'Successfully loaded {loaded_fixtures}/{total_fixtures} fixtures in {elapsed_time:.2f} seconds'
        ))
        
        # Give summary of loaded data
        from django.contrib.auth import get_user_model
        from inventory.models import Product, Category, Supplier, Location, InventoryItem
        from menu.models import Recipe, Menu
        
        User = get_user_model()
        
        self.stdout.write("\nData summary:")
        self.stdout.write(f"Users: {User.objects.count()}")
        self.stdout.write(f"Categories: {Category.objects.count()}")
        self.stdout.write(f"Suppliers: {Supplier.objects.count()}")
        self.stdout.write(f"Locations: {Location.objects.count()}")
        self.stdout.write(f"Products: {Product.objects.count()}")
        self.stdout.write(f"Inventory Items: {InventoryItem.objects.count()}")
        self.stdout.write(f"Recipes: {Recipe.objects.count()}")
        self.stdout.write(f"Menus: {Menu.objects.count()}") 