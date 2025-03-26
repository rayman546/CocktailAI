"""
Signal handlers for the accounts app.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import User, UserPreferences


@receiver(post_save, sender=User)
def create_user_preferences(sender, instance, created, **kwargs):
    """
    Create UserPreferences when a new User is created.
    
    Args:
        sender: The model class (User)
        instance: The User instance
        created: Boolean indicating if the User was created
        **kwargs: Additional keyword arguments
    """
    if created:
        UserPreferences.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_preferences(sender, instance, **kwargs):
    """
    Save UserPreferences when User is saved.
    
    Args:
        sender: The model class (User)
        instance: The User instance
        **kwargs: Additional keyword arguments
    """
    if hasattr(instance, 'preferences'):
        instance.preferences.save()
    else:
        # If preferences doesn't exist for some reason, create it
        UserPreferences.objects.create(user=instance) 