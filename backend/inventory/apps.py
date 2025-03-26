"""
Inventory app configuration.
"""

from django.apps import AppConfig


class InventoryConfig(AppConfig):
    """Configuration for the inventory app."""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'inventory'
    
    def ready(self):
        """Import signals when the app is ready."""
        import inventory.signals  # noqa 