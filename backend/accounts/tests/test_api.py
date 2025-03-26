"""
Tests for the accounts app API endpoints.
"""
from django.urls import reverse
from rest_framework import status
from django.contrib.auth import get_user_model
from accounts.models import UserPreferences
from core.tests.test_base import BaseAPITestCase

User = get_user_model()


class UserAPITests(BaseAPITestCase):
    """Tests for the User API endpoints."""
    
    def setUp(self):
        """Set up for test case."""
        super().setUp()
        self.user_list_url = reverse('api:user-list')
        self.admin_detail_url = reverse('api:user-detail', args=[self.admin_user.id])
        self.regular_user_detail_url = reverse('api:user-detail', args=[self.regular_user.id])
        self.login_url = reverse('api:token_obtain_pair')
    
    def test_login_with_valid_credentials(self):
        """Test that a user can login with valid credentials."""
        payload = {
            'username': 'admin',
            'password': 'adminpass123',
        }
        
        response = self.client.post(self.login_url, payload)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
    
    def test_login_with_invalid_credentials(self):
        """Test that login fails with invalid credentials."""
        payload = {
            'username': 'admin',
            'password': 'wrongpass',
        }
        
        response = self.client.post(self.login_url, payload)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_list_users_as_admin(self):
        """Test that admin can list all users."""
        self.authenticate_as_admin()
        
        response = self.client.get(self.user_list_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 2)  # At least admin and regular user
    
    def test_list_users_as_regular_user(self):
        """Test that a regular user cannot list all users."""
        self.authenticate_as_regular_user()
        
        response = self.client.get(self.user_list_url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_retrieve_own_user_profile(self):
        """Test that a user can retrieve their own profile."""
        self.authenticate_as_regular_user()
        
        response = self.client.get(self.regular_user_detail_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], self.regular_user.username)
    
    def test_retrieve_another_user_profile_as_regular_user(self):
        """Test that a regular user cannot retrieve another user's profile."""
        self.authenticate_as_regular_user()
        
        response = self.client.get(self.admin_detail_url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_retrieve_another_user_profile_as_admin(self):
        """Test that an admin can retrieve another user's profile."""
        self.authenticate_as_admin()
        
        response = self.client.get(self.regular_user_detail_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], self.regular_user.username)
    
    def test_create_user_as_admin(self):
        """Test that an admin can create a new user."""
        self.authenticate_as_admin()
        
        payload = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpass123',
            'first_name': 'New',
            'last_name': 'User',
        }
        
        response = self.client.post(self.user_list_url, payload)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['username'], payload['username'])
        self.assertEqual(response.data['email'], payload['email'])
        
        # Verify user was created in the database
        self.assertTrue(User.objects.filter(username='newuser').exists())
    
    def test_create_user_as_regular_user(self):
        """Test that a regular user cannot create a new user."""
        self.authenticate_as_regular_user()
        
        payload = {
            'username': 'newuser2',
            'email': 'newuser2@example.com',
            'password': 'newpass123',
            'first_name': 'New',
            'last_name': 'User',
        }
        
        response = self.client.post(self.user_list_url, payload)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        # Verify user was not created in the database
        self.assertFalse(User.objects.filter(username='newuser2').exists())
    
    def test_update_own_profile(self):
        """Test that a user can update their own profile."""
        self.authenticate_as_regular_user()
        
        payload = {
            'first_name': 'Updated',
            'last_name': 'Name',
        }
        
        response = self.client.patch(self.regular_user_detail_url, payload)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], payload['first_name'])
        self.assertEqual(response.data['last_name'], payload['last_name'])
        
        # Verify the user was updated in the database
        self.regular_user.refresh_from_db()
        self.assertEqual(self.regular_user.first_name, payload['first_name'])
        self.assertEqual(self.regular_user.last_name, payload['last_name'])
    
    def test_update_another_user_as_regular_user(self):
        """Test that a regular user cannot update another user's profile."""
        self.authenticate_as_regular_user()
        
        payload = {
            'first_name': 'Should',
            'last_name': 'Fail',
        }
        
        response = self.client.patch(self.admin_detail_url, payload)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Verify the user was not updated in the database
        self.admin_user.refresh_from_db()
        self.assertNotEqual(self.admin_user.first_name, payload['first_name'])
    
    def test_delete_user_as_admin(self):
        """Test that an admin can delete a user."""
        self.authenticate_as_admin()
        
        # Create a user to delete
        user_to_delete = User.objects.create_user(
            username='deleteuser',
            email='delete@example.com',
            password='deletepass123'
        )
        
        url = reverse('api:user-detail', args=[user_to_delete.id])
        
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # Verify the user was deleted from the database
        self.assertFalse(User.objects.filter(username='deleteuser').exists())
    
    def test_delete_user_as_regular_user(self):
        """Test that a regular user cannot delete a user."""
        self.authenticate_as_regular_user()
        
        # Create a user to delete
        user_to_delete = User.objects.create_user(
            username='deleteuser2',
            email='delete2@example.com',
            password='deletepass123'
        )
        
        url = reverse('api:user-detail', args=[user_to_delete.id])
        
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        # Verify the user was not deleted from the database
        self.assertTrue(User.objects.filter(username='deleteuser2').exists())


class UserPreferencesAPITests(BaseAPITestCase):
    """Tests for the UserPreferences API endpoints."""
    
    def setUp(self):
        """Set up for test case."""
        super().setUp()
        self.admin_preferences_url = reverse('api:user-preferences', args=[self.admin_user.id])
        self.regular_user_preferences_url = reverse('api:user-preferences', args=[self.regular_user.id])
    
    def test_get_own_preferences(self):
        """Test that a user can get their own preferences."""
        self.authenticate_as_regular_user()
        
        response = self.client.get(self.regular_user_preferences_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user'], self.regular_user.id)
        self.assertEqual(response.data['items_per_page'], 20)  # Default value
    
    def test_get_another_user_preferences_as_regular_user(self):
        """Test that a regular user cannot get another user's preferences."""
        self.authenticate_as_regular_user()
        
        response = self.client.get(self.admin_preferences_url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_get_another_user_preferences_as_admin(self):
        """Test that an admin can get another user's preferences."""
        self.authenticate_as_admin()
        
        response = self.client.get(self.regular_user_preferences_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user'], self.regular_user.id)
    
    def test_update_own_preferences(self):
        """Test that a user can update their own preferences."""
        self.authenticate_as_regular_user()
        
        payload = {
            'items_per_page': 50,
            'default_view': 'grid',
            'low_stock_alerts': False,
        }
        
        response = self.client.patch(self.regular_user_preferences_url, payload)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['items_per_page'], payload['items_per_page'])
        self.assertEqual(response.data['default_view'], payload['default_view'])
        self.assertEqual(response.data['low_stock_alerts'], payload['low_stock_alerts'])
        
        # Verify the preferences were updated in the database
        self.regular_user.preferences.refresh_from_db()
        self.assertEqual(self.regular_user.preferences.items_per_page, payload['items_per_page'])
        self.assertEqual(self.regular_user.preferences.default_view, payload['default_view'])
        self.assertEqual(self.regular_user.preferences.low_stock_alerts, payload['low_stock_alerts'])
    
    def test_update_another_user_preferences_as_regular_user(self):
        """Test that a regular user cannot update another user's preferences."""
        self.authenticate_as_regular_user()
        
        payload = {
            'items_per_page': 100,
            'default_view': 'calendar',
        }
        
        response = self.client.patch(self.admin_preferences_url, payload)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Verify the preferences were not updated in the database
        self.admin_user.preferences.refresh_from_db()
        self.assertNotEqual(self.admin_user.preferences.items_per_page, payload['items_per_page'])
    
    def test_update_another_user_preferences_as_admin(self):
        """Test that an admin can update another user's preferences."""
        self.authenticate_as_admin()
        
        payload = {
            'items_per_page': 100,
            'default_view': 'calendar',
        }
        
        response = self.client.patch(self.regular_user_preferences_url, payload)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify the preferences were updated in the database
        self.regular_user.preferences.refresh_from_db()
        self.assertEqual(self.regular_user.preferences.items_per_page, payload['items_per_page'])
        self.assertEqual(self.regular_user.preferences.default_view, payload['default_view']) 