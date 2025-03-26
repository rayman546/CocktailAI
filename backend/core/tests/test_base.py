"""
Base test case classes for the CocktailAI project.
These classes provide common functionality for other test cases to inherit.
"""
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class BaseTestCase(TestCase):
    """Base test case for regular Django tests."""
    
    fixtures = [
        'accounts/fixtures/admin_user.json',
        'inventory/fixtures/categories.json',
        'inventory/fixtures/suppliers.json',
        'inventory/fixtures/locations.json',
        'inventory/fixtures/products.json',
        'inventory/fixtures/inventory_items.json',
        'inventory/fixtures/transactions.json',
        'menu/fixtures/recipe_categories.json',
        'menu/fixtures/recipes.json',
        'menu/fixtures/menus.json',
    ]
    
    @classmethod
    def setUpTestData(cls):
        """Set up data for the whole TestCase."""
        # The fixtures will load the admin user and other data
        cls.admin_user = User.objects.get(username='admin')
        
        # Create a regular (non-staff) test user
        cls.regular_user = User.objects.create_user(
            username='regularuser',
            email='regular@example.com',
            password='regularpass123',
            first_name='Regular',
            last_name='User',
            is_active=True
        )


class BaseAPITestCase(APITestCase):
    """Base test case for API tests using DRF's APITestCase."""
    
    fixtures = [
        'accounts/fixtures/admin_user.json',
        'inventory/fixtures/categories.json',
        'inventory/fixtures/suppliers.json',
        'inventory/fixtures/locations.json',
        'inventory/fixtures/products.json',
        'inventory/fixtures/inventory_items.json',
        'inventory/fixtures/transactions.json',
        'menu/fixtures/recipe_categories.json',
        'menu/fixtures/recipes.json',
        'menu/fixtures/menus.json',
    ]
    
    @classmethod
    def setUpTestData(cls):
        """Set up data for the whole TestCase."""
        # The fixtures will load the admin user and other data
        cls.admin_user = User.objects.get(username='admin')
        
        # Create a regular (non-staff) test user
        cls.regular_user = User.objects.create_user(
            username='regularuser',
            email='regular@example.com',
            password='regularpass123',
            first_name='Regular',
            last_name='User',
            is_active=True
        )
    
    def setUp(self):
        """Set up for each test method."""
        self.client = APIClient()
    
    def authenticate_as_admin(self):
        """Authenticate as admin user."""
        self.client.force_authenticate(user=self.admin_user)
    
    def authenticate_as_regular_user(self):
        """Authenticate as regular user."""
        self.client.force_authenticate(user=self.regular_user)
    
    def get_admin_tokens(self):
        """Get JWT tokens for admin user."""
        refresh = RefreshToken.for_user(self.admin_user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
    
    def get_regular_user_tokens(self):
        """Get JWT tokens for regular user."""
        refresh = RefreshToken.for_user(self.regular_user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
    
    def authenticate_with_token(self, token):
        """Authenticate with JWT token."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}') 