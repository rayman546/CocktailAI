"""
Admin configuration for the inventory app.
"""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import (
    Category, Supplier, Location, Product, InventoryItem,
    InventoryTransaction, InventoryCount, InventoryCountItem,
    Order, OrderItem
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin configuration for Category model."""
    
    list_display = ("name", "is_active")
    search_fields = ("name", "description")
    list_filter = ("is_active",)


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    """Admin configuration for Supplier model."""
    
    list_display = ("name", "contact_name", "email", "phone", "is_active")
    search_fields = ("name", "contact_name", "email", "phone")
    list_filter = ("is_active",)


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    """Admin configuration for Location model."""
    
    list_display = ("name", "is_storage", "is_service", "is_active")
    search_fields = ("name", "description")
    list_filter = ("is_storage", "is_service", "is_active")


class InventoryItemInline(admin.TabularInline):
    """Inline admin for InventoryItem model."""
    
    model = InventoryItem
    extra = 0
    fields = ("location", "quantity")
    readonly_fields = ("value",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Admin configuration for Product model."""
    
    list_display = (
        "name", "sku", "category", "supplier", 
        "unit_price", "total_quantity", "below_par_level"
    )
    list_filter = ("category", "supplier", "is_active")
    search_fields = ("name", "sku", "description", "barcode")
    inlines = (InventoryItemInline,)
    fieldsets = (
        (None, {
            "fields": ("name", "sku", "description", "image", "barcode", "notes")
        }),
        (_("Classification"), {
            "fields": ("category", "supplier")
        }),
        (_("Pricing"), {
            "fields": ("unit_price",)
        }),
        (_("Inventory Management"), {
            "fields": (
                "unit_size", "unit_type", "par_level", 
                "reorder_point", "reorder_quantity"
            )
        }),
        (_("Status"), {
            "fields": ("is_active",)
        }),
    )
    readonly_fields = ("total_quantity", "total_value", "below_par_level", "needs_reorder")


@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    """Admin configuration for InventoryItem model."""
    
    list_display = ("product", "location", "quantity", "value")
    list_filter = ("location", "product__category", "is_active")
    search_fields = ("product__name", "product__sku", "location__name")
    readonly_fields = ("value",)


@admin.register(InventoryTransaction)
class InventoryTransactionAdmin(admin.ModelAdmin):
    """Admin configuration for InventoryTransaction model."""
    
    list_display = (
        "transaction_id", "transaction_type", "product", 
        "location", "quantity", "performed_by", "created_at"
    )
    list_filter = ("transaction_type", "location", "performed_by", "created_at")
    search_fields = (
        "transaction_id", "product__name", "product__sku", 
        "location__name", "reference", "notes"
    )
    readonly_fields = ("transaction_id", "total_value", "created_at", "updated_at")
    date_hierarchy = "created_at"


class InventoryCountItemInline(admin.TabularInline):
    """Inline admin for InventoryCountItem model."""
    
    model = InventoryCountItem
    extra = 0
    fields = (
        "product", "expected_quantity", "counted_quantity", 
        "is_counted", "counted_by", "counted_at", "notes"
    )
    readonly_fields = ("variance", "variance_percentage")


@admin.register(InventoryCount)
class InventoryCountAdmin(admin.ModelAdmin):
    """Admin configuration for InventoryCount model."""
    
    list_display = (
        "name", "location", "status", "scheduled_date", 
        "created_by", "completed_by", "progress_percentage"
    )
    list_filter = ("status", "location", "created_by", "completed_by", "created_at")
    search_fields = ("name", "description", "notes")
    readonly_fields = (
        "count_id", "progress_percentage", "total_items", 
        "completed_items", "created_at", "updated_at"
    )
    inlines = (InventoryCountItemInline,)
    date_hierarchy = "created_at"


@admin.register(InventoryCountItem)
class InventoryCountItemAdmin(admin.ModelAdmin):
    """Admin configuration for InventoryCountItem model."""
    
    list_display = (
        "inventory_count", "product", "expected_quantity", 
        "counted_quantity", "is_counted", "variance"
    )
    list_filter = (
        "is_counted", "counted_by", "inventory_count__status", 
        "inventory_count__location"
    )
    search_fields = (
        "product__name", "product__sku", "inventory_count__name", 
        "notes"
    )
    readonly_fields = ("variance", "variance_percentage")


class OrderItemInline(admin.TabularInline):
    """Inline admin for OrderItem model."""
    
    model = OrderItem
    extra = 0
    fields = (
        "product", "quantity", "unit_price", 
        "received_quantity", "total_price", "receiving_status"
    )
    readonly_fields = ("total_price", "receiving_status")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Admin configuration for Order model."""
    
    list_display = (
        "order_number", "supplier", "status", "order_date", 
        "expected_delivery_date", "created_by", "total"
    )
    list_filter = ("status", "supplier", "created_by", "created_at")
    search_fields = ("order_number", "supplier__name", "notes")
    readonly_fields = ("subtotal", "total", "created_at", "updated_at")
    inlines = (OrderItemInline,)
    date_hierarchy = "created_at"


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """Admin configuration for OrderItem model."""
    
    list_display = (
        "order", "product", "quantity", "unit_price", 
        "received_quantity", "total_price", "is_fully_received"
    )
    list_filter = ("order__status", "order__supplier", "is_active")
    search_fields = ("product__name", "product__sku", "order__order_number")
    readonly_fields = ("total_price", "is_fully_received", "receiving_status") 