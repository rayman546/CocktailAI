"""
Signal handlers for the inventory app.
"""

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from django.db import transaction

from .models import (
    InventoryTransaction, InventoryItem, Product, 
    InventoryCount, InventoryCountItem, Order, OrderItem
)


@receiver(post_save, sender=InventoryTransaction)
def update_inventory_on_transaction(sender, instance, created, **kwargs):
    """
    Update inventory quantity when a transaction is saved.
    
    Uses atomic transactions to ensure database consistency.
    Handles all transaction types including transfers.
    
    Args:
        sender: The model class (InventoryTransaction)
        instance: The InventoryTransaction instance
        created: Boolean indicating if the transaction was created
        **kwargs: Additional keyword arguments
    """
    if created:
        with transaction.atomic():
            # Get or create inventory item for the primary location
            inventory_item, _ = InventoryItem.objects.get_or_create(
                product=instance.product,
                location=instance.location,
                defaults={'quantity': 0}
            )
            
            # Handle transfer logic with destination location
            if instance.transaction_type == "transferred" and instance.destination_location:
                # Get or create inventory item for the destination location
                destination_item, _ = InventoryItem.objects.get_or_create(
                    product=instance.product,
                    location=instance.destination_location,
                    defaults={'quantity': 0}
                )
                
                # Reduce from source (instance.quantity should already be negative)
                inventory_item.quantity += instance.quantity
                
                # Add to destination (convert to positive)
                destination_item.quantity += abs(instance.quantity)
                
                # Save both items
                inventory_item.save()
                destination_item.save()
            else:
                # For all other transaction types
                # We use addition regardless of transaction type because:
                # - "received" transactions have positive quantities
                # - "sold" transactions have negative quantities (enforced by serializer)
                # - "adjustment" transactions can be either positive or negative
                inventory_item.quantity += instance.quantity
                
                # Ensure quantity doesn't go below zero for physical inventory
                if inventory_item.quantity < 0 and instance.transaction_type != "adjustment":
                    inventory_item.quantity = 0
                    
                # Save the updated inventory item
                inventory_item.save()


@receiver(post_save, sender=InventoryCount)
def handle_completed_count(sender, instance, **kwargs):
    """
    Process inventory when a count is marked as completed.
    
    Args:
        sender: The model class (InventoryCount)
        instance: The InventoryCount instance
        **kwargs: Additional keyword arguments
    """
    # Only proceed if the count was just completed
    if instance.status == "completed" and instance.completed_date is not None:
        # Use atomic transaction for all adjustments
        with transaction.atomic():
            # Process all count items
            for count_item in instance.count_items.filter(is_counted=True):
                if count_item.variance != 0:
                    # Create an adjustment transaction for the variance
                    InventoryTransaction.objects.create(
                        transaction_type="adjustment",
                        product=count_item.product,
                        location=instance.location,
                        quantity=count_item.variance,
                        unit_price=count_item.product.unit_price,
                        reference=f"Count adjustment: {instance.name}",
                        notes=f"Automatic adjustment from inventory count {instance.name}",
                        performed_by=instance.completed_by or instance.created_by
                    )


@receiver(pre_save, sender=InventoryCount)
def set_completed_date(sender, instance, **kwargs):
    """
    Set the completed date when a count is marked as completed.
    
    Args:
        sender: The model class (InventoryCount)
        instance: The InventoryCount instance
        **kwargs: Additional keyword arguments
    """
    if instance.pk:
        # Get the original instance from the database
        original = sender.objects.get(pk=instance.pk)
        
        # If the status changed to completed, set the completed date
        if original.status != "completed" and instance.status == "completed":
            instance.completed_date = timezone.now()


@receiver(post_save, sender=Order)
def create_count_items_for_received_order(sender, instance, **kwargs):
    """
    Create inventory transactions when an order is marked as received.
    
    Args:
        sender: The model class (Order)
        instance: The Order instance
        **kwargs: Additional keyword arguments
    """
    # Only proceed if the order was just marked as received
    if instance.status == "received" and instance.actual_delivery_date is not None:
        # Use atomic transaction for all order items
        with transaction.atomic():
            # Get all order items that have a received quantity
            received_items = instance.items.filter(received_quantity__gt=0)
            
            # Process each received item
            for item in received_items:
                # Use order's delivery location if specified, or fall back to default
                location = instance.delivery_location
                if not location:
                    from .models import Location
                    location = Location.objects.filter(is_storage=True, is_active=True).first()
                
                if location:
                    # Create a received transaction for each item
                    InventoryTransaction.objects.create(
                        transaction_type="received",
                        product=item.product,
                        location=location,
                        quantity=item.received_quantity,  # Should be positive
                        unit_price=item.unit_price,
                        reference=f"Order #{instance.order_number}",
                        notes=f"Received from order #{instance.order_number}",
                        performed_by=instance.updated_by or instance.created_by
                    ) 