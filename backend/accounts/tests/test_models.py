"""
Tests for the accounts app models.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
from accounts.models import UserPreferences
from core.tests.test_base import BaseTestCase

User = get_user_model()


class UserModelTests(BaseTestCase):
    """Tests for the User model."""
    
    def test_create_user(self):
        """Test creating a regular user."""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            first_name="Test",
            last_name="User"
        )
        
        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.email, "test@example.com")
        self.assertEqual(user.first_name, "Test")
        self.assertEqual(user.last_name, "User")
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertTrue(user.check_password("testpass123"))
    
    def test_create_superuser(self):
        """Test creating a superuser."""
        admin_user = User.objects.create_superuser(
            username="admin2",
            email="admin2@example.com",
            password="adminpass123"
        )
        
        self.assertEqual(admin_user.username, "admin2")
        self.assertEqual(admin_user.email, "admin2@example.com")
        self.assertTrue(admin_user.is_active)
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)
    
    def test_user_string_representation(self):
        """Test the string representation of a user."""
        user = User.objects.create_user(
            username="testuser2",
            email="test2@example.com",
            password="testpass123",
            first_name="Test2",
            last_name="User2"
        )
        
        self.assertEqual(str(user), "testuser2")
    
    def test_email_is_normalized(self):
        """Test that the email address is normalized when creating a user."""
        email = "test3@EXAMPLE.com"
        user = User.objects.create_user(
            username="testuser3",
            email=email,
            password="testpass123"
        )
        
        self.assertEqual(user.email, email.lower())
    
    def test_email_is_required(self):
        """Test that email is required when creating a user."""
        with self.assertRaises(ValueError):
            User.objects.create_user(
                username="testuser4",
                email=None,
                password="testpass123"
            )
    
    def test_username_unique(self):
        """Test that username is unique."""
        User.objects.create_user(
            username="uniqueuser",
            email="unique@example.com",
            password="testpass123"
        )
        
        with self.assertRaises(IntegrityError):
            User.objects.create_user(
                username="uniqueuser",
                email="different@example.com",
                password="testpass123"
            )


class UserPreferencesTests(BaseTestCase):
    """Tests for the UserPreferences model."""
    
    def test_user_preferences_created_with_user(self):
        """Test that UserPreferences are created when a user is created."""
        user = User.objects.create_user(
            username="prefuser",
            email="pref@example.com",
            password="testpass123"
        )
        
        # Verify UserPreferences was created
        preferences = UserPreferences.objects.filter(user=user).first()
        self.assertIsNotNone(preferences)
    
    def test_preferences_default_values(self):
        """Test the default values of UserPreferences."""
        user = User.objects.create_user(
            username="prefuser2",
            email="pref2@example.com",
            password="testpass123"
        )
        
        preferences = user.preferences
        
        # Check default values
        self.assertEqual(preferences.items_per_page, 20)
        self.assertEqual(preferences.default_view, "list")
        self.assertTrue(preferences.low_stock_alerts)
        self.assertTrue(preferences.order_status_notifications)
        self.assertTrue(preferences.inventory_count_reminders)
        self.assertEqual(preferences.date_format, "MM/DD/YYYY")
        self.assertEqual(preferences.time_format, "12-hour")
        self.assertEqual(preferences.timezone, "UTC")
    
    def test_preferences_string_representation(self):
        """Test the string representation of UserPreferences."""
        user = User.objects.create_user(
            username="prefuser3",
            email="pref3@example.com",
            password="testpass123"
        )
        
        preferences = user.preferences
        self.assertEqual(str(preferences), "prefuser3's preferences")
    
    def test_preferences_update(self):
        """Test updating UserPreferences."""
        user = User.objects.create_user(
            username="prefuser4",
            email="pref4@example.com",
            password="testpass123"
        )
        
        preferences = user.preferences
        
        # Update preferences
        preferences.items_per_page = 50
        preferences.default_view = "grid"
        preferences.low_stock_alerts = False
        preferences.date_format = "DD/MM/YYYY"
        preferences.save()
        
        # Refresh from database
        preferences.refresh_from_db()
        
        # Check updated values
        self.assertEqual(preferences.items_per_page, 50)
        self.assertEqual(preferences.default_view, "grid")
        self.assertFalse(preferences.low_stock_alerts)
        self.assertEqual(preferences.date_format, "DD/MM/YYYY") 