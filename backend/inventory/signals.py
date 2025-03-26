"""
Signal handlers for the inventory app.
"""

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone

from .models import (
    InventoryTransaction, InventoryItem, Product, 
    InventoryCount, InventoryCountItem, Order, OrderItem
)


@receiver(post_save, sender=InventoryTransaction)
def update_inventory_on_transaction(sender, instance, created, **kwargs):
    """
    Update inventory quantity when a transaction is saved.
    
    Args:
        sender: The model class (InventoryTransaction)
        instance: The InventoryTransaction instance
        created: Boolean indicating if the transaction was created
        **kwargs: Additional keyword arguments
    """
    if created:
        # Get or create inventory item
        inventory_item, _ = InventoryItem.objects.get_or_create(
            product=instance.product,
            location=instance.location,
            defaults={'quantity': 0}
        )
        
        # Update quantity based on transaction type
        if instance.transaction_type in ["received", "adjustment", "count"]:
            # Positive transactions
            inventory_item.quantity += instance.quantity
        elif instance.transaction_type == "sold":
            # Negative transactions
            inventory_item.quantity -= abs(instance.quantity)
        elif instance.transaction_type == "transferred":
            # For transfers, we need to create another transaction for the destination
            # This would be handled elsewhere in the business logic
            pass
        
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
        # Get all order items that have a received quantity
        received_items = instance.items.filter(received_quantity__gt=0)
        
        # Process each received item
        for item in received_items:
            # Determine the default location (this would be set by business logic)
            # For now, just use the first active storage location
            from .models import Location
            default_location = Location.objects.filter(is_storage=True, is_active=True).first()
            
            if default_location:
                # Create a received transaction for each item
                InventoryTransaction.objects.create(
                    transaction_type="received",
                    product=item.product,
                    location=default_location,
                    quantity=item.received_quantity,
                    unit_price=item.unit_price,
                    reference=f"Order #{instance.order_number}",
                    notes=f"Received from order #{instance.order_number}",
                    performed_by=instance.updated_by or instance.created_by
                ) 