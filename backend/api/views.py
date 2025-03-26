"""
API views for the CocktailAI project.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db import transaction
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.db.models import Q
from rest_framework import mixins
from django.db.models import Sum

# Import models and serializers
from accounts.models import User, UserPreferences
from inventory.models import (
    Category, Supplier, Location, Product, InventoryItem,
    InventoryTransaction, InventoryCount, InventoryCountItem,
    Order, OrderItem
)
from .serializers import (
    UserSerializer, UserCreateSerializer, UserPreferencesSerializer,
    CategorySerializer, SupplierSerializer, LocationSerializer,
    ProductListSerializer, ProductDetailSerializer, ProductCreateUpdateSerializer,
    InventoryItemListSerializer, InventoryItemDetailSerializer, InventoryItemCreateUpdateSerializer,
    InventoryTransactionListSerializer, InventoryTransactionDetailSerializer, 
    InventoryTransactionCreateSerializer, InventoryCountListSerializer,
    InventoryCountDetailSerializer, InventoryCountCreateUpdateSerializer,
    InventoryCountItemSerializer, InventoryCountItemUpdateSerializer,
    OrderListSerializer, OrderDetailSerializer, OrderCreateSerializer, OrderUpdateSerializer,
    OrderItemListSerializer, OrderItemDetailSerializer, OrderItemCreateUpdateSerializer
)
# Import custom permissions
from .permissions import (
    IsStaffOrReadOnly, IsOwnerOrStaffOrReadOnly, IsAdminOrReadOnly, 
    IsOwnerOrStaff, IsAuthenticatedForMethods
)
# Import utilities
from .utils import paginate_queryset, create_error_response
# Import filters
from .filters import (
    ProductFilter, InventoryItemFilter, InventoryTransactionFilter,
    OrderFilter, InventoryCountFilter,
    CategoryFilter, SupplierFilter, LocationFilter
)
from .schema import (
    extend_schema_with_auth, product_parameters, 
    inventory_item_parameters, transaction_parameters,
    inventory_parameters, order_parameters
)
from drf_spectacular.utils import (
    extend_schema, extend_schema_view, 
    OpenApiParameter, OpenApiExample, 
    OpenApiResponse, inline_serializer
)
from .docs import API_FEATURES_DOCS, FILTERING_DOCS, SORTING_DOCS, PAGINATION_DOCS

class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing users.
    
    list:
    Return a list of all users (admin only).
    
    retrieve:
    Return the given user.
    
    create:
    Create a new user.
    
    update:
    Update a user instance.
    
    partial_update:
    Partially update a user instance.
    
    destroy:
    Delete a user instance.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['is_active', 'is_staff']
    search_fields = ['username', 'email', 'first_name', 'last_name', 'company_name']
    ordering_fields = ['username', 'date_joined', 'date_updated']
    
    def get_serializer_class(self):
        """
        Return the appropriate serializer based on the action.
        """
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer
    
    def get_permissions(self):
        """
        Return appropriate permissions based on the action.
        """
        if self.action == 'create':
            # Allow anyone to register
            permission_classes = [AllowAny]
        elif self.action in ['list']:
            # Only staff can list all users
            permission_classes = [IsAdminUser]
        elif self.action == 'destroy':
            # Only admins can delete users
            permission_classes = [IsAdminUser]
        else:
            # For retrieve, update, partial_update:
            # Users can only see/update their own profile, staff can see/update any
            permission_classes = [IsOwnerOrStaff]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        """
        Filter queryset based on the user's permissions.
        """
        user = self.request.user
        
        # Admin users can see all users
        if user.is_staff:
            return User.objects.all()
        
        # Non-admin users can only see their own profile
        return User.objects.filter(id=user.id)
    
    @action(detail=True, methods=['get', 'put', 'patch'], url_path='preferences')
    def preferences(self, request, pk=None):
        """
        Retrieve or update user preferences.
        """
        user = self.get_object()
        
        # Create preferences if they don't exist
        preferences, created = UserPreferences.objects.get_or_create(user=user)
        
        if request.method == 'GET':
            serializer = UserPreferencesSerializer(preferences)
            return Response(serializer.data)
        
        # Update preferences
        serializer = UserPreferencesSerializer(preferences, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserPreferencesViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing user preferences.
    
    This viewset is only for admin use. Regular users should 
    use the /users/{id}/preferences/ endpoint instead.
    """
    queryset = UserPreferences.objects.all()
    serializer_class = UserPreferencesSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['items_per_page', 'default_view']


@extend_schema_view(
    list=extend_schema_with_auth(
        summary="List all categories",
        description="Returns a list of all product categories.",
        tags=["Categories"]
    ),
    retrieve=extend_schema_with_auth(
        summary="Retrieve a category",
        description="Returns details of a specific product category.",
        tags=["Categories"]
    ),
    create=extend_schema_with_auth(
        summary="Create a new category",
        description="Create a new product category.",
        tags=["Categories"]
    ),
    update=extend_schema_with_auth(
        summary="Update a category",
        description="Updates all fields of a specific product category.",
        tags=["Categories"]
    ),
    partial_update=extend_schema_with_auth(
        summary="Partially update a category",
        description="Updates selected fields of a specific product category.",
        tags=["Categories"]
    ),
    destroy=extend_schema_with_auth(
        summary="Delete a category",
        description="Deletes a specific product category from the system.",
        tags=["Categories"]
    ),
)
class CategoryViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing product categories.
    
    Categories are used to organize products into logical groups.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsStaffOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = CategoryFilter
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at', 'updated_at']
    ordering = ['name']

    @extend_schema_with_auth(
        summary="Get products in a category",
        description="Returns a list of products in a specific category.",
        tags=["Categories"],
        parameters=product_parameters()
    )
    @action(detail=True, methods=['get'])
    def products(self, request, pk=None):
        """
        Get all products in this category.
        
        Returns a paginated list of products that belong to the specified category.
        """
        category = self.get_object()
        products = Product.objects.filter(category=category)
        
        return paginate_queryset(self, products, ProductListSerializer)


@extend_schema_view(
    list=extend_schema_with_auth(
        summary="List all suppliers",
        description="Returns a list of all suppliers.",
        tags=["Suppliers"]
    ),
    retrieve=extend_schema_with_auth(
        summary="Retrieve a supplier",
        description="Returns details of a specific supplier.",
        tags=["Suppliers"]
    ),
    create=extend_schema_with_auth(
        summary="Create a new supplier",
        description="Create a new supplier.",
        tags=["Suppliers"]
    ),
    update=extend_schema_with_auth(
        summary="Update a supplier",
        description="Updates all fields of a specific supplier.",
        tags=["Suppliers"]
    ),
    partial_update=extend_schema_with_auth(
        summary="Partially update a supplier",
        description="Updates selected fields of a specific supplier.",
        tags=["Suppliers"]
    ),
    destroy=extend_schema_with_auth(
        summary="Delete a supplier",
        description="Deletes a specific supplier from the system.",
        tags=["Suppliers"]
    ),
)
class SupplierViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing suppliers.
    
    Suppliers are vendors that provide products to the bar inventory.
    """
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    permission_classes = [IsStaffOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = SupplierFilter
    search_fields = ['name', 'contact_name', 'email', 'phone', 'address']
    ordering_fields = ['name', 'created_at', 'updated_at']
    ordering = ['name']

    @extend_schema_with_auth(
        summary="Get products from a supplier",
        description="Returns a list of products available from a specific supplier.",
        tags=["Suppliers"],
        parameters=product_parameters()
    )
    @action(detail=True, methods=['get'])
    def products(self, request, pk=None):
        """
        Get all products from this supplier.
        
        Returns a paginated list of products that are provided by the specified supplier.
        """
        supplier = self.get_object()
        products = Product.objects.filter(supplier=supplier)
        
        return paginate_queryset(self, products, ProductListSerializer)

    @extend_schema_with_auth(
        summary="Get orders for a supplier",
        description="Returns a list of orders placed with a specific supplier.",
        tags=["Suppliers"],
        parameters=order_parameters()
    )
    @action(detail=True, methods=['get'])
    def orders(self, request, pk=None):
        """
        Get all orders for this supplier.
        
        Returns a paginated list of orders placed with the specified supplier.
        """
        supplier = self.get_object()
        orders = Order.objects.filter(supplier=supplier)
        
        return paginate_queryset(self, orders, OrderSerializer)


@extend_schema_view(
    list=extend_schema_with_auth(
        summary="List all locations",
        description="Returns a list of all inventory locations.",
        tags=["Locations"]
    ),
    retrieve=extend_schema_with_auth(
        summary="Retrieve a location",
        description="Returns details of a specific inventory location.",
        tags=["Locations"]
    ),
    create=extend_schema_with_auth(
        summary="Create a new location",
        description="Create a new inventory location.",
        tags=["Locations"]
    ),
    update=extend_schema_with_auth(
        summary="Update a location",
        description="Updates all fields of a specific inventory location.",
        tags=["Locations"]
    ),
    partial_update=extend_schema_with_auth(
        summary="Partially update a location",
        description="Updates selected fields of a specific inventory location.",
        tags=["Locations"]
    ),
    destroy=extend_schema_with_auth(
        summary="Delete a location",
        description="Deletes a specific inventory location from the system.",
        tags=["Locations"]
    ),
)
class LocationViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing inventory locations.
    
    Locations represent physical places where inventory is stored,
    such as bars, storerooms, or warehouses.
    """
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    permission_classes = [IsStaffOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = LocationFilter
    search_fields = ['name', 'description', 'address']
    ordering_fields = ['name', 'created_at', 'updated_at']
    ordering = ['name']

    @extend_schema_with_auth(
        summary="Get inventory at a location",
        description="Returns a list of inventory items stored at a specific location.",
        tags=["Locations"],
        parameters=inventory_item_parameters()
    )
    @action(detail=True, methods=['get'])
    def inventory(self, request, pk=None):
        """
        Get all inventory items at this location.
        
        Returns a paginated list of inventory items stored at the specified location.
        """
        location = self.get_object()
        items = InventoryItem.objects.filter(location=location)
        
        return paginate_queryset(self, items, InventoryItemListSerializer)

    @extend_schema_with_auth(
        summary="Get inventory counts for a location",
        description="Returns a list of inventory count sessions for a specific location.",
        tags=["Locations"],
        parameters=inventory_parameters()
    )
    @action(detail=True, methods=['get'])
    def inventory_counts(self, request, pk=None):
        """
        Get all inventory counts for this location.
        
        Returns a paginated list of inventory count sessions for the specified location.
        """
        location = self.get_object()
        counts = InventoryCount.objects.filter(location=location)
        
        return paginate_queryset(self, counts, InventoryCountSerializer)

    @extend_schema_with_auth(
        summary="Get transactions at a location",
        description="Returns a list of inventory transactions that occurred at a specific location.",
        tags=["Locations"],
        parameters=transaction_parameters()
    )
    @action(detail=True, methods=['get'])
    def transactions(self, request, pk=None):
        """
        Get all inventory transactions for this location.
        
        Returns a paginated list of inventory transactions that occurred at the specified location.
        """
        location = self.get_object()
        transactions = InventoryTransaction.objects.filter(
            inventory_item__location=location
        ).order_by('-created_at')
        
        return paginate_queryset(self, transactions, InventoryTransactionListSerializer)


@extend_schema_view(
    list=extend_schema_with_auth(
        summary="List all user profiles",
        description="Returns a list of all user profiles.",
        tags=["Users"]
    ),
    retrieve=extend_schema_with_auth(
        summary="Retrieve a user profile",
        description="Returns details of a specific user profile.",
        tags=["Users"]
    ),
    update=extend_schema_with_auth(
        summary="Update a user profile",
        description="Updates all fields of a specific user profile.",
        tags=["Users"]
    ),
    partial_update=extend_schema_with_auth(
        summary="Partially update a user profile",
        description="Updates selected fields of a specific user profile.",
        tags=["Users"]
    ),
)
class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing user profiles.
    
    User profiles contain additional information about system users,
    including roles and preferences.
    """
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsOwnerOrStaff]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['is_active', 'is_staff', 'is_superuser']
    search_fields = ['user__username', 'user__email', 'user__first_name', 'user__last_name']
    ordering_fields = ['user__username', 'user__date_joined', 'user__last_login']
    http_method_names = ['get', 'put', 'patch', 'head', 'options']  # No POST or DELETE

    def get_queryset(self):
        """
        Filter queryset based on permissions.
        
        Staff users can see all profiles, regular users can only see their own.
        """
        user = self.request.user
        if user.is_staff:
            return UserProfile.objects.all()
        return UserProfile.objects.filter(user=user)

@extend_schema_view(
    list=extend_schema_with_auth(
        summary="List all inventory items",
        description="Returns a list of all inventory items across all locations.",
        tags=["Inventory"],
        parameters=inventory_item_parameters()
    ),
    retrieve=extend_schema_with_auth(
        summary="Retrieve an inventory item",
        description="Returns details of a specific inventory item.",
        tags=["Inventory"]
    ),
    create=extend_schema_with_auth(
        summary="Create a new inventory item",
        description="Create a new inventory item in a specific location.",
        tags=["Inventory"]
    ),
    update=extend_schema_with_auth(
        summary="Update an inventory item",
        description="Updates all fields of a specific inventory item.",
        tags=["Inventory"]
    ),
    partial_update=extend_schema_with_auth(
        summary="Partially update an inventory item",
        description="Updates selected fields of a specific inventory item.",
        tags=["Inventory"]
    ),
    destroy=extend_schema_with_auth(
        summary="Delete an inventory item",
        description="Deletes a specific inventory item from the system.",
        tags=["Inventory"]
    ),
)
class InventoryItemViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing inventory items.
    
    Inventory items represent the physical stock of products at specific locations.
    """
    queryset = InventoryItem.objects.all()
    permission_classes = [IsStaffOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = InventoryItemFilter
    search_fields = ['product__name', 'location__name']
    ordering_fields = ['product__name', 'location__name', 'quantity', 'created_at', 'updated_at']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return InventoryItemDetailSerializer
        return InventoryItemListSerializer

    @extend_schema_with_auth(
        summary="Get transactions for an inventory item",
        description="Returns a list of inventory transactions for a specific inventory item.",
        tags=["Inventory"],
        parameters=transaction_parameters()
    )
    @action(detail=True, methods=['get'])
    def transactions(self, request, pk=None):
        """
        Get the transaction history for this inventory item.
        
        Returns a paginated list of inventory transactions for the specified inventory item.
        """
        inventory_item = self.get_object()
        transactions = inventory_item.transactions.all().order_by('-created_at')
        
        return paginate_queryset(self, transactions, InventoryTransactionListSerializer)

@extend_schema_view(
    list=extend_schema_with_auth(
        summary="List all inventory transactions",
        description="Returns a list of all inventory transactions.",
        tags=["Transactions"],
        parameters=transaction_parameters()
    ),
    retrieve=extend_schema_with_auth(
        summary="Retrieve an inventory transaction",
        description="Returns details of a specific inventory transaction.",
        tags=["Transactions"]
    ),
    create=extend_schema_with_auth(
        summary="Create a new inventory transaction",
        description="Create a new inventory transaction.",
        tags=["Transactions"]
    ),
    update=extend_schema_with_auth(
        summary="Update an inventory transaction",
        description="Updates all fields of a specific inventory transaction.",
        tags=["Transactions"]
    ),
    partial_update=extend_schema_with_auth(
        summary="Partially update an inventory transaction",
        description="Updates selected fields of a specific inventory transaction.",
        tags=["Transactions"]
    ),
    destroy=extend_schema_with_auth(
        summary="Delete an inventory transaction",
        description="Deletes a specific inventory transaction from the system.",
        tags=["Transactions"]
    ),
)
class InventoryTransactionViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing inventory transactions.
    
    Inventory transactions record changes to inventory items, including
    receiving, selling, transferring, and adjusting stock.
    """
    queryset = InventoryTransaction.objects.all()
    permission_classes = [IsOwnerOrStaffOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = InventoryTransactionFilter
    search_fields = ['inventory_item__product__name', 'notes']
    ordering_fields = ['created_at', 'quantity', 'transaction_type']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return InventoryTransactionDetailSerializer
        return InventoryTransactionListSerializer
    
    def perform_create(self, serializer):
        serializer.save(performed_by=self.request.user)

@extend_schema_view(
    list=extend_schema_with_auth(
        summary="List all inventory counts",
        description="Returns a list of all inventory counts.",
        tags=["Inventory Counts"],
        parameters=inventory_parameters()
    ),
    retrieve=extend_schema_with_auth(
        summary="Retrieve an inventory count",
        description="Returns details of a specific inventory count.",
        tags=["Inventory Counts"]
    ),
    create=extend_schema_with_auth(
        summary="Create a new inventory count",
        description="Create a new inventory count session.",
        tags=["Inventory Counts"]
    ),
    update=extend_schema_with_auth(
        summary="Update an inventory count",
        description="Updates all fields of a specific inventory count.",
        tags=["Inventory Counts"]
    ),
    partial_update=extend_schema_with_auth(
        summary="Partially update an inventory count",
        description="Updates selected fields of a specific inventory count.",
        tags=["Inventory Counts"]
    ),
    destroy=extend_schema_with_auth(
        summary="Delete an inventory count",
        description="Deletes a specific inventory count from the system.",
        tags=["Inventory Counts"]
    ),
)
class InventoryCountViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing inventory counts.
    
    Inventory counts are sessions where the physical inventory is counted
    and reconciled with the system records.
    """
    queryset = InventoryCount.objects.all()
    permission_classes = [IsOwnerOrStaffOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = InventoryCountFilter
    search_fields = ['name', 'location__name', 'notes']
    ordering_fields = ['created_at', 'count_date', 'status']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return InventoryCountDetailSerializer
        return InventoryCountSerializer
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @extend_schema_with_auth(
        summary="Get uncounted items for an inventory count",
        description="Returns a list of items that haven't been counted yet in this count session.",
        tags=["Inventory Counts"]
    )
    @action(detail=True, methods=['get'])
    def uncounted_items(self, request, pk=None):
        """
        Get items that haven't been counted yet in this count session.
        
        Returns a paginated list of inventory count items that haven't been marked as counted.
        """
        inventory_count = self.get_object()
        uncounted_items = inventory_count.count_items.filter(is_counted=False)
        
        return paginate_queryset(self, uncounted_items, InventoryCountItemSerializer)

@extend_schema_view(
    list=extend_schema_with_auth(
        summary="List all orders",
        description="Returns a list of all orders.",
        tags=["Orders"],
        parameters=order_parameters()
    ),
    retrieve=extend_schema_with_auth(
        summary="Retrieve an order",
        description="Returns details of a specific order.",
        tags=["Orders"]
    ),
    create=extend_schema_with_auth(
        summary="Create a new order",
        description="Create a new order to a supplier.",
        tags=["Orders"]
    ),
    update=extend_schema_with_auth(
        summary="Update an order",
        description="Updates all fields of a specific order.",
        tags=["Orders"]
    ),
    partial_update=extend_schema_with_auth(
        summary="Partially update an order",
        description="Updates selected fields of a specific order.",
        tags=["Orders"]
    ),
    destroy=extend_schema_with_auth(
        summary="Delete an order",
        description="Deletes a specific order from the system.",
        tags=["Orders"]
    ),
)
class OrderViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing supplier orders.
    
    Orders represent purchasing requests to suppliers for restocking inventory.
    """
    queryset = Order.objects.all()
    permission_classes = [IsOwnerOrStaffOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = OrderFilter
    search_fields = ['supplier__name', 'notes', 'reference_number']
    ordering_fields = ['created_at', 'order_date', 'status', 'total_cost']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return OrderDetailSerializer
        return OrderSerializer
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @extend_schema_with_auth(
        summary="Mark order as placed",
        description="Updates the order status to 'placed' and records the order date.",
        tags=["Orders"]
    )
    @action(detail=True, methods=['post'])
    def place(self, request, pk=None):
        """
        Mark an order as placed with the supplier.
        
        Updates the order status to 'placed' and records the order date.
        """
        order = self.get_object()
        
        if order.status != 'draft' and order.status != 'pending':
            return Response(
                {"error": "Only draft or pending orders can be placed"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        order.status = 'placed'
        order.order_date = timezone.now().date()
        order.save()
        
        return Response(OrderDetailSerializer(order).data)

    @extend_schema_with_auth(
        summary="Mark order as received",
        description="Updates the order status to 'received' and creates inventory transactions.",
        tags=["Orders"]
    )
    @action(detail=True, methods=['post'])
    def receive(self, request, pk=None):
        """
        Mark an order as received and update inventory.
        
        Updates the order status to 'received', creates inventory transactions 
        for each item, and updates inventory quantities.
        """
        order = self.get_object()
        
        if order.status != 'placed':
            return Response(
                {"error": "Only placed orders can be received"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        with transaction.atomic():
            for item in order.items.all():
                # Get or create inventory item
                inventory_item, created = InventoryItem.objects.get_or_create(
                    product=item.product,
                    location=order.delivery_location,
                    defaults={'quantity': 0}
                )
                
                # Create transaction
                InventoryTransaction.objects.create(
                    inventory_item=inventory_item,
                    quantity=item.quantity,
                    transaction_type='received',
                    notes=f"Received from order #{order.id}",
                    performed_by=request.user
                )
                
                # Update inventory quantity
                inventory_item.quantity += item.quantity
                inventory_item.save()
            
            order.status = 'received'
            order.received_date = timezone.now().date()
            order.save()
        
        return Response(OrderDetailSerializer(order).data)

# Viewset classes will be added here as models and serializers are created
# Example:
# class ProductViewSet(viewsets.ModelViewSet):
#     """
#     API endpoint for managing products.
#     """
#     queryset = Product.objects.all()
#     serializer_class = ProductSerializer
#     permission_classes = [IsAuthenticated]
#     filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
#     filterset_fields = ['category', 'supplier', 'is_active']
#     search_fields = ['name', 'sku', 'description']
#     ordering_fields = ['name', 'created_at', 'updated_at', 'price'] 

@extend_schema_view(
    list=extend_schema_with_auth(
        summary="List all products",
        description="Returns a list of all products in the inventory.",
        tags=["Products"],
        parameters=product_parameters()
    ),
    retrieve=extend_schema_with_auth(
        summary="Retrieve a product",
        description="Returns details of a specific product.",
        tags=["Products"]
    ),
    create=extend_schema_with_auth(
        summary="Create a new product",
        description="Create a new product in the inventory.",
        tags=["Products"]
    ),
    update=extend_schema_with_auth(
        summary="Update a product",
        description="Updates all fields of a specific product.",
        tags=["Products"]
    ),
    partial_update=extend_schema_with_auth(
        summary="Partially update a product",
        description="Updates selected fields of a specific product.",
        tags=["Products"]
    ),
    destroy=extend_schema_with_auth(
        summary="Delete a product",
        description="Deletes a specific product from the system.",
        tags=["Products"]
    ),
)
class ProductViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing products.
    
    Products represent items that can be stocked in the inventory.
    """
    queryset = Product.objects.all()
    permission_classes = [IsStaffOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ['name', 'sku', 'description', 'barcode', 'category__name', 'supplier__name']
    ordering_fields = ['name', 'category__name', 'supplier__name', 'unit_price', 'created_at', 'updated_at']
    ordering = ['name']
    
    def get_serializer_class(self):
        """
        Return the appropriate serializer based on the action.
        """
        if self.action == 'retrieve':
            return ProductDetailSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return ProductCreateUpdateSerializer
        return ProductListSerializer

    @extend_schema_with_auth(
        summary="Get inventory items for a product",
        description="Returns a list of inventory items for a specific product across all locations.",
        tags=["Products"],
        parameters=inventory_item_parameters()
    )
    @action(detail=True, methods=['get'])
    def inventory(self, request, pk=None):
        """
        Get all inventory items for this product.
        
        Returns a paginated list of inventory items for the specified product across all locations.
        """
        product = self.get_object()
        items = InventoryItem.objects.filter(product=product)
        
        return paginate_queryset(self, items, InventoryItemListSerializer)

    @extend_schema_with_auth(
        summary="Get transactions for a product",
        description="Returns a list of inventory transactions for a specific product.",
        tags=["Products"],
        parameters=transaction_parameters()
    )
    @action(detail=True, methods=['get'])
    def transactions(self, request, pk=None):
        """
        Get all transactions for this product.
        
        Returns a paginated list of inventory transactions for the specified product.
        """
        product = self.get_object()
        transactions = InventoryTransaction.objects.filter(
            inventory_item__product=product
        ).order_by('-created_at')
        
        return paginate_queryset(self, transactions, InventoryTransactionListSerializer)

class APIDocs(viewsets.ViewSet):
    """
    ViewSet for API documentation endpoints.
    """
    permission_classes = [AllowAny]
    
    @extend_schema(
        summary="API Features Documentation",
        description="Documentation for all API features, including filtering, sorting, and pagination",
        responses={200: {"type": "string", "format": "markdown"}},
        tags=["Documentation"]
    )
    def features(self, request):
        """
        Documentation for all API features, including filtering, sorting, and pagination.
        """
        return Response({"documentation": API_FEATURES_DOCS})
    
    @extend_schema(
        summary="API Filtering Documentation",
        description="Documentation for API filtering capabilities",
        responses={200: {"type": "string", "format": "markdown"}},
        tags=["Documentation"]
    )
    def filtering(self, request):
        """
        Documentation for API filtering capabilities.
        """
        return Response({"documentation": FILTERING_DOCS})
    
    @extend_schema(
        summary="API Sorting Documentation",
        description="Documentation for API sorting capabilities",
        responses={200: {"type": "string", "format": "markdown"}},
        tags=["Documentation"]
    )
    def sorting(self, request):
        """
        Documentation for API sorting capabilities.
        """
        return Response({"documentation": SORTING_DOCS})
    
    @extend_schema(
        summary="API Pagination Documentation",
        description="Documentation for API pagination capabilities",
        responses={200: {"type": "string", "format": "markdown"}},
        tags=["Documentation"]
    )
    def pagination(self, request):
        """
        Documentation for API pagination capabilities.
        """
        return Response({"documentation": PAGINATION_DOCS}) 