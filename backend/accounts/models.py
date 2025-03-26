"""
Models for the accounts app.
"""

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser.
    
    Adds additional fields needed for the CocktailAI platform.
    """
    
    # Basic profile information
    phone_number = models.CharField(_("Phone Number"), max_length=20, blank=True)
    position = models.CharField(_("Position/Role"), max_length=100, blank=True)
    bio = models.TextField(_("Biography"), blank=True)
    profile_image = models.ImageField(
        _("Profile Image"), 
        upload_to='profile_images/', 
        blank=True, 
        null=True
    )
    
    # Preferences and settings
    notification_email = models.BooleanField(_("Email Notifications"), default=True)
    notification_sms = models.BooleanField(_("SMS Notifications"), default=False)
    dark_mode = models.BooleanField(_("Dark Mode"), default=False)
    
    # Business-related fields
    company_name = models.CharField(_("Company Name"), max_length=255, blank=True)
    location = models.CharField(_("Location"), max_length=255, blank=True)
    
    # Date fields
    date_updated = models.DateTimeField(_("Date Updated"), auto_now=True)
    
    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")
        ordering = ["username"]
    
    def __str__(self):
        """Return the user's full name or username."""
        return self.get_full_name() or self.username
    
    def get_location_display(self):
        """Return formatted location if available."""
        return self.location if self.location else _("No location set")


class UserPreferences(models.Model):
    """
    Additional user preferences for the application.
    
    Separated from User model to keep it clean and focused.
    """
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="preferences"
    )
    
    # Interface preferences
    items_per_page = models.PositiveIntegerField(_("Items Per Page"), default=20)
    default_view = models.CharField(
        _("Default View"),
        max_length=50,
        choices=[
            ("list", _("List")),
            ("grid", _("Grid")),
            ("calendar", _("Calendar")),
        ],
        default="list"
    )
    
    # Notification settings
    low_stock_alerts = models.BooleanField(_("Low Stock Alerts"), default=True)
    order_status_notifications = models.BooleanField(_("Order Status Notifications"), default=True)
    inventory_count_reminders = models.BooleanField(_("Inventory Count Reminders"), default=True)
    
    # Date and time preferences
    date_format = models.CharField(_("Date Format"), max_length=20, default="MM/DD/YYYY")
    time_format = models.CharField(_("Time Format"), max_length=20, default="12-hour")
    timezone = models.CharField(_("Timezone"), max_length=50, default="UTC")
    
    class Meta:
        verbose_name = _("User Preferences")
        verbose_name_plural = _("User Preferences")
    
    def __str__(self):
        """Return the associated user's username."""
        return f"{self.user.username}'s preferences" 