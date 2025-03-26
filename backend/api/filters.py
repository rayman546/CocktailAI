"""
Filter classes for the CocktailAI API.
"""

import django_filters
from django.db.models import Q
from inventory.models import (
    Product, InventoryItem, InventoryTransaction, InventoryCount, Order,
    Category, Supplier, Location
)


class CategoryFilter(django_filters.FilterSet):
    """
    Filter for categories with advanced filtering options.
    """
    search = django_filters.CharFilter(method='search_filter')
    created_after = django_filters.DateFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateFilter(field_name='created_at', lookup_expr='lte')
    updated_after = django_filters.DateFilter(field_name='updated_at', lookup_expr='gte')
    updated_before = django_filters.DateFilter(field_name='updated_at', lookup_expr='lte')
    has_products = django_filters.BooleanFilter(method='filter_has_products')
    
    class Meta:
        model = Category
        fields = {
            'name': ['exact', 'icontains'],
            'parent': ['exact', 'isnull'],
            'is_active': ['exact'],
        }
    
    def search_filter(self, queryset, name, value):
        """
        Search across multiple fields.
        """
        return queryset.filter(
            Q(name__icontains=value) |
            Q(description__icontains=value)
        )
    
    def filter_has_products(self, queryset, name, value):
        """
        Filter categories that have products.
        """
        if value:
            return queryset.filter(products__isnull=False).distinct()
        else:
            return queryset.filter(products__isnull=True).distinct()


class SupplierFilter(django_filters.FilterSet):
    """
    Filter for suppliers with advanced filtering options.
    """
    search = django_filters.CharFilter(method='search_filter')
    created_after = django_filters.DateFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateFilter(field_name='created_at', lookup_expr='lte')
    updated_after = django_filters.DateFilter(field_name='updated_at', lookup_expr='gte')
    updated_before = django_filters.DateFilter(field_name='updated_at', lookup_expr='lte')
    has_products = django_filters.BooleanFilter(method='filter_has_products')
    has_orders = django_filters.BooleanFilter(method='filter_has_orders')
    
    class Meta:
        model = Supplier
        fields = {
            'name': ['exact', 'icontains'],
            'contact_name': ['exact', 'icontains'],
            'email': ['exact', 'icontains'],
            'phone': ['exact', 'icontains'],
            'is_active': ['exact'],
        }
    
    def search_filter(self, queryset, name, value):
        """
        Search across multiple fields.
        """
        return queryset.filter(
            Q(name__icontains=value) |
            Q(contact_name__icontains=value) |
            Q(email__icontains=value) |
            Q(phone__icontains=value) |
            Q(address__icontains=value) |
            Q(notes__icontains=value)
        )
    
    def filter_has_products(self, queryset, name, value):
        """
        Filter suppliers that have products.
        """
        if value:
            return queryset.filter(products__isnull=False).distinct()
        else:
            return queryset.filter(products__isnull=True).distinct()
    
    def filter_has_orders(self, queryset, name, value):
        """
        Filter suppliers that have orders.
        """
        if value:
            return queryset.filter(orders__isnull=False).distinct()
        else:
            return queryset.filter(orders__isnull=True).distinct()


class LocationFilter(django_filters.FilterSet):
    """
    Filter for locations with advanced filtering options.
    """
    search = django_filters.CharFilter(method='search_filter')
    created_after = django_filters.DateFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateFilter(field_name='created_at', lookup_expr='lte')
    updated_after = django_filters.DateFilter(field_name='updated_at', lookup_expr='gte')
    updated_before = django_filters.DateFilter(field_name='updated_at', lookup_expr='lte')
    has_inventory = django_filters.BooleanFilter(method='filter_has_inventory')
    
    class Meta:
        model = Location
        fields = {
            'name': ['exact', 'icontains'],
            'location_type': ['exact', 'in'],
            'is_active': ['exact'],
        }
    
    def search_filter(self, queryset, name, value):
        """
        Search across multiple fields.
        """
        return queryset.filter(
            Q(name__icontains=value) |
            Q(description__icontains=value) |
            Q(address__icontains=value)
        )
    
    def filter_has_inventory(self, queryset, name, value):
        """
        Filter locations that have inventory.
        """
        if value:
            return queryset.filter(inventory_items__isnull=False).distinct()
        else:
            return queryset.filter(inventory_items__isnull=True).distinct()


class ProductFilter(django_filters.FilterSet):
    """
    Filter for products with advanced filtering options.
    """
    min_price = django_filters.NumberFilter(field_name='unit_price', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='unit_price', lookup_expr='lte')
    min_quantity = django_filters.NumberFilter(field_name='total_quantity', lookup_expr='gte')
    max_quantity = django_filters.NumberFilter(field_name='total_quantity', lookup_expr='lte')
    search = django_filters.CharFilter(method='search_filter')
    created_after = django_filters.DateFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateFilter(field_name='created_at', lookup_expr='lte')
    category_name = django_filters.CharFilter(field_name='category__name', lookup_expr='icontains')
    supplier_name = django_filters.CharFilter(field_name='supplier__name', lookup_expr='icontains')
    
    class Meta:
        model = Product
        fields = {
            'name': ['exact', 'icontains'],
            'sku': ['exact', 'icontains'],
            'barcode': ['exact', 'icontains'],
            'category': ['exact'],
            'supplier': ['exact'],
            'unit_type': ['exact'],
            'is_active': ['exact'],
        }
    
    def search_filter(self, queryset, name, value):
        """
        Search across multiple fields.
        """
        return queryset.filter(
            Q(name__icontains=value) |
            Q(sku__icontains=value) |
            Q(barcode__icontains=value) |
            Q(description__icontains=value) |
            Q(category__name__icontains=value) |
            Q(supplier__name__icontains=value)
        )


class InventoryItemFilter(django_filters.FilterSet):
    """
    Filter for inventory items with advanced filtering options.
    """
    min_quantity = django_filters.NumberFilter(field_name='quantity', lookup_expr='gte')
    max_quantity = django_filters.NumberFilter(field_name='quantity', lookup_expr='lte')
    search = django_filters.CharFilter(method='search_filter')
    created_after = django_filters.DateFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateFilter(field_name='created_at', lookup_expr='lte')
    product_name = django_filters.CharFilter(field_name='product__name', lookup_expr='icontains')
    location_name = django_filters.CharFilter(field_name='location__name', lookup_expr='icontains')
    
    class Meta:
        model = InventoryItem
        fields = {
            'product': ['exact'],
            'location': ['exact'],
            'is_active': ['exact'],
        }
    
    def search_filter(self, queryset, name, value):
        """
        Search across multiple fields.
        """
        return queryset.filter(
            Q(product__name__icontains=value) |
            Q(product__sku__icontains=value) |
            Q(product__barcode__icontains=value) |
            Q(location__name__icontains=value)
        )


class InventoryTransactionFilter(django_filters.FilterSet):
    """
    Filter for inventory transactions with advanced filtering options.
    """
    min_quantity = django_filters.NumberFilter(field_name='quantity', lookup_expr='gte')
    max_quantity = django_filters.NumberFilter(field_name='quantity', lookup_expr='lte')
    min_unit_price = django_filters.NumberFilter(field_name='unit_price', lookup_expr='gte')
    max_unit_price = django_filters.NumberFilter(field_name='unit_price', lookup_expr='lte')
    min_total_value = django_filters.NumberFilter(field_name='total_value', lookup_expr='gte')
    max_total_value = django_filters.NumberFilter(field_name='total_value', lookup_expr='lte')
    search = django_filters.CharFilter(method='search_filter')
    created_after = django_filters.DateFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateFilter(field_name='created_at', lookup_expr='lte')
    product_name = django_filters.CharFilter(field_name='inventory_item__product__name', lookup_expr='icontains')
    location_name = django_filters.CharFilter(field_name='inventory_item__location__name', lookup_expr='icontains')
    
    class Meta:
        model = InventoryTransaction
        fields = {
            'inventory_item': ['exact'],
            'inventory_item__product': ['exact'],
            'inventory_item__location': ['exact'],
            'transaction_type': ['exact', 'in'],
            'performed_by': ['exact'],
            'is_active': ['exact'],
        }
    
    def search_filter(self, queryset, name, value):
        """
        Search across multiple fields.
        """
        return queryset.filter(
            Q(inventory_item__product__name__icontains=value) |
            Q(inventory_item__location__name__icontains=value) |
            Q(reference__icontains=value) |
            Q(notes__icontains=value)
        )


class OrderFilter(django_filters.FilterSet):
    """
    Filter for orders with advanced filtering options.
    """
    min_total_cost = django_filters.NumberFilter(field_name='total_cost', lookup_expr='gte')
    max_total_cost = django_filters.NumberFilter(field_name='total_cost', lookup_expr='lte')
    search = django_filters.CharFilter(method='search_filter')
    created_after = django_filters.DateFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateFilter(field_name='created_at', lookup_expr='lte')
    order_date_after = django_filters.DateFilter(field_name='order_date', lookup_expr='gte')
    order_date_before = django_filters.DateFilter(field_name='order_date', lookup_expr='lte')
    received_date_after = django_filters.DateFilter(field_name='received_date', lookup_expr='gte')
    received_date_before = django_filters.DateFilter(field_name='received_date', lookup_expr='lte')
    supplier_name = django_filters.CharFilter(field_name='supplier__name', lookup_expr='icontains')
    
    class Meta:
        model = Order
        fields = {
            'supplier': ['exact'],
            'status': ['exact', 'in'],
            'created_by': ['exact'],
            'is_active': ['exact'],
            'reference_number': ['exact', 'icontains'],
        }
    
    def search_filter(self, queryset, name, value):
        """
        Search across multiple fields.
        """
        return queryset.filter(
            Q(reference_number__icontains=value) |
            Q(supplier__name__icontains=value) |
            Q(notes__icontains=value)
        )


class InventoryCountFilter(django_filters.FilterSet):
    """
    Filter for inventory counts with advanced filtering options.
    """
    search = django_filters.CharFilter(method='search_filter')
    created_after = django_filters.DateFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateFilter(field_name='created_at', lookup_expr='lte')
    scheduled_after = django_filters.DateFilter(field_name='scheduled_date', lookup_expr='gte')
    scheduled_before = django_filters.DateFilter(field_name='scheduled_date', lookup_expr='lte')
    completed_after = django_filters.DateFilter(field_name='completed_date', lookup_expr='gte')
    completed_before = django_filters.DateFilter(field_name='completed_date', lookup_expr='lte')
    location_name = django_filters.CharFilter(field_name='location__name', lookup_expr='icontains')
    
    class Meta:
        model = InventoryCount
        fields = {
            'location': ['exact'],
            'status': ['exact', 'in'],
            'created_by': ['exact'],
            'completed_by': ['exact'],
            'is_active': ['exact'],
            'count_id': ['exact', 'icontains'],
        }
    
    def search_filter(self, queryset, name, value):
        """
        Search across multiple fields.
        """
        return queryset.filter(
            Q(name__icontains=value) |
            Q(description__icontains=value) |
            Q(notes__icontains=value) |
            Q(count_id__icontains=value) |
            Q(location__name__icontains=value)
        ) 