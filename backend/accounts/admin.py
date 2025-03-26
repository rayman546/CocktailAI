"""
Admin configuration for the accounts app.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User, UserPreferences


class UserPreferencesInline(admin.StackedInline):
    """Inline admin for UserPreferences model."""
    
    model = UserPreferences
    can_delete = False
    verbose_name_plural = _("Preferences")


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom admin for User model."""
    
    inlines = (UserPreferencesInline,)
    
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name", "email", 
                                         "phone_number", "position", "bio", "profile_image")}),
        (_("Business info"), {"fields": ("company_name", "location")}),
        (_("Preferences"), {"fields": ("notification_email", "notification_sms", "dark_mode")}),
        (_("Permissions"), {"fields": ("is_active", "is_staff", "is_superuser",
                                       "groups", "user_permissions")}),
        (_("Important dates"), {"fields": ("last_login", "date_joined", "date_updated")}),
    )
    
    readonly_fields = ("date_updated",)
    
    list_display = ("username", "email", "first_name", "last_name", "is_staff", "company_name")
    list_filter = ("is_staff", "is_superuser", "is_active", "groups", "notification_email")
    search_fields = ("username", "first_name", "last_name", "email", "company_name")
    ordering = ("username",) 