"""
API serializers for the CocktailAI project.
"""

from rest_framework import serializers

# Import models as they are created
# Example:
# from inventory.models import Product, Category, Supplier
# from accounts.models import User

# Import models
from accounts.models import User, UserPreferences
from inventory.models import Category, Supplier, Location, Product, InventoryItem, InventoryTransaction, InventoryCount, InventoryCountItem, Order, OrderItem

# Serializer classes will be added here as models are created
# Example:
# class CategorySerializer(serializers.ModelSerializer):
#     """
#     Serializer for the Category model.
#     """
#     class Meta:
#         model = Category
#         fields = ['id', 'name', 'description', 'is_active', 'created_at', 'updated_at']
#         read_only_fields = ['created_at', 'updated_at']
#
# class SupplierSerializer(serializers.ModelSerializer):
#     """
#     Serializer for the Supplier model.
#     """
#     class Meta:
#         model = Supplier
#         fields = ['id', 'name', 'contact_name', 'email', 'phone', 'address', 'is_active', 'created_at', 'updated_at']
#         read_only_fields = ['created_at', 'updated_at']
#
# class ProductSerializer(serializers.ModelSerializer):
#     """
#     Serializer for the Product model.
#     """
#     category = CategorySerializer(read_only=True)
#     category_id = serializers.PrimaryKeyRelatedField(
#         queryset=Category.objects.all(),
#         source='category',
#         write_only=True
#     )
#     supplier = SupplierSerializer(read_only=True)
#     supplier_id = serializers.PrimaryKeyRelatedField(
#         queryset=Supplier.objects.all(),
#         source='supplier',
#         write_only=True
#     )
#
#     class Meta:
#         model = Product
#         fields = [
#             'id', 'name', 'sku', 'description', 'category', 'category_id',
#             'supplier', 'supplier_id', 'unit_price', 'unit_size', 'unit_type',
#             'par_level', 'reorder_point', 'is_active', 'created_at', 'updated_at'
#         ]
#         read_only_fields = ['created_at', 'updated_at']

class UserPreferencesSerializer(serializers.ModelSerializer):
    """
    Serializer for the UserPreferences model.
    """
    class Meta:
        model = UserPreferences
        fields = [
            'id', 'items_per_page', 'default_view', 
            'low_stock_alerts', 'order_status_notifications', 'inventory_count_reminders',
            'date_format', 'time_format', 'timezone'
        ]

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the User model.
    """
    preferences = UserPreferencesSerializer(read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'phone_number', 'position', 'bio', 'profile_image',
            'notification_email', 'notification_sms', 'dark_mode',
            'company_name', 'location', 'date_updated', 'preferences'
        ]
        read_only_fields = ['date_updated']
        extra_kwargs = {'password': {'write_only': True}}

class UserCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating User instances.
    Handles password hashing.
    """
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password_confirm = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'password', 'password_confirm',
            'first_name', 'last_name', 'phone_number', 'position',
            'company_name', 'location'
        ]

    def validate(self, data):
        """
        Check that the passwords match.
        """
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({"password_confirm": "Passwords do not match."})
        return data

    def create(self, validated_data):
        """
        Create and return a new user with encrypted password.
        """
        # Remove password_confirm from validated data
        validated_data.pop('password_confirm', None)
        
        # Create the user with create_user to handle password hashing
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            phone_number=validated_data.get('phone_number', ''),
            position=validated_data.get('position', ''),
            company_name=validated_data.get('company_name', ''),
            location=validated_data.get('location', '')
        )
        
        return user

# Inventory serializers
class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer for the Category model.
    """
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class SupplierSerializer(serializers.ModelSerializer):
    """
    Serializer for the Supplier model.
    """
    class Meta:
        model = Supplier
        fields = [
            'id', 'name', 'contact_name', 'email', 'phone', 
            'address', 'website', 'notes', 'is_active', 
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class LocationSerializer(serializers.ModelSerializer):
    """
    Serializer for the Location model.
    """
    class Meta:
        model = Location
        fields = [
            'id', 'name', 'description', 'is_storage', 
            'is_service', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

# Additional inventory serializers will be added here 

# Product serializers
class ProductSerializer(serializers.ModelSerializer):
    """
    Base serializer for Product instances.
    Handles all product operations with conditional field inclusion
    based on context or action.
    """
    # Fields for list view
    category_name = serializers.ReadOnlyField(source='category.name')
    supplier_name = serializers.ReadOnlyField(source='supplier.name')
    total_quantity = serializers.ReadOnlyField()
    total_value = serializers.ReadOnlyField()
    below_par_level = serializers.ReadOnlyField()
    needs_reorder = serializers.ReadOnlyField()
    
    # Fields for detail view
    category = serializers.SerializerMethodField()
    supplier = serializers.SerializerMethodField()
    category_id = serializers.PrimaryKeyRelatedField(
        source='category',
        queryset=Category.objects.all(),
        write_only=True,
        required=False
    )
    supplier_id = serializers.PrimaryKeyRelatedField(
        source='supplier',
        queryset=Supplier.objects.all(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'sku', 'description', 'barcode', 'image',
            'category', 'category_id', 'category_name', 
            'supplier', 'supplier_id', 'supplier_name',
            'unit_price', 'unit_size', 'unit_type',
            'par_level', 'reorder_point', 'reorder_quantity',
            'notes', 'total_quantity', 'total_value', 
            'below_par_level', 'needs_reorder',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def __init__(self, *args, **kwargs):
        """
        Initialize the serializer with dynamic field sets based on context.
        """
        super().__init__(*args, **kwargs)
        
        # Get the request context to determine which fields to include
        request = self.context.get('request')
        if not request:
            return
            
        # For list action, exclude detailed fields
        if self.context.get('view') and self.context['view'].action == 'list':
            self.fields.pop('description', None)
            self.fields.pop('notes', None)
            
        # For create/update actions, use simplified representation of category and supplier
        if request.method in ['POST', 'PUT', 'PATCH']:
            self.fields.pop('category', None)
            self.fields.pop('supplier', None)
            self.fields.pop('category_name', None)
            self.fields.pop('supplier_name', None)
            self.fields.pop('total_quantity', None)
            self.fields.pop('total_value', None)
            self.fields.pop('below_par_level', None)
            self.fields.pop('needs_reorder', None)
        else:  # For GET requests
            self.fields.pop('category_id', None)
            self.fields.pop('supplier_id', None)
    
    def get_category(self, obj):
        """
        Return the full CategorySerializer representation for detail view.
        """
        # Only return detailed category in detail view
        if self.context.get('view') and self.context['view'].action == 'retrieve':
            return CategorySerializer(obj.category).data
        return obj.category_id
        
    def get_supplier(self, obj):
        """
        Return the full SupplierSerializer representation for detail view.
        """
        # Only return detailed supplier in detail view
        if self.context.get('view') and self.context['view'].action == 'retrieve':
            return SupplierSerializer(obj.supplier).data
        return obj.supplier_id


# Keeping these aliases for backward compatibility during transition
ProductListSerializer = ProductSerializer
ProductDetailSerializer = ProductSerializer
ProductCreateUpdateSerializer = ProductSerializer


# InventoryItem serializers
class InventoryItemSerializer(serializers.ModelSerializer):
    """
    Base serializer for InventoryItem instances.
    Handles all inventory item operations with conditional field inclusion
    based on context or action.
    """
    # Fields for list view
    product_name = serializers.ReadOnlyField(source='product.name')
    location_name = serializers.ReadOnlyField(source='location.name')
    value = serializers.ReadOnlyField()
    
    # Fields for detail view
    product = serializers.SerializerMethodField()
    location = serializers.SerializerMethodField()
    product_id = serializers.PrimaryKeyRelatedField(
        source='product',
        queryset=Product.objects.all(),
        write_only=True
    )
    location_id = serializers.PrimaryKeyRelatedField(
        source='location',
        queryset=Location.objects.all(),
        write_only=True
    )
    
    class Meta:
        model = InventoryItem
        fields = [
            'id', 'product', 'product_id', 'product_name', 
            'location', 'location_id', 'location_name',
            'quantity', 'value', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def __init__(self, *args, **kwargs):
        """
        Initialize the serializer with dynamic field sets based on context.
        """
        super().__init__(*args, **kwargs)
        
        # Get the request context to determine which fields to include
        request = self.context.get('request')
        if not request:
            return
            
        # For create/update actions, use simplified representation
        if request.method in ['POST', 'PUT', 'PATCH']:
            self.fields.pop('product', None)
            self.fields.pop('location', None)
            self.fields.pop('product_name', None)
            self.fields.pop('location_name', None)
            self.fields.pop('value', None)
        else:  # For GET requests
            self.fields.pop('product_id', None)
            self.fields.pop('location_id', None)

    def get_product(self, obj):
        """
        Return the full ProductSerializer representation for detail view.
        """
        # Only return detailed product in detail view
        if self.context.get('view') and self.context['view'].action == 'retrieve':
            return ProductSerializer(obj.product).data
        return obj.product_id
        
    def get_location(self, obj):
        """
        Return the full LocationSerializer representation for detail view.
        """
        # Only return detailed location in detail view
        if self.context.get('view') and self.context['view'].action == 'retrieve':
            return LocationSerializer(obj.location).data
        return obj.location_id
    
    def validate(self, data):
        """
        Validate that the product-location combination is unique.
        """
        product = data.get('product')
        location = data.get('location')
        
        # Check if we're creating a new object or updating an existing one
        instance = self.instance
        
        # If instance is None, we're creating a new object
        if instance is None:
            if InventoryItem.objects.filter(product=product, location=location).exists():
                raise serializers.ValidationError(
                    {"non_field_errors": "An inventory item for this product and location already exists."}
                )
                
        # If instance is not None, we're updating an existing object
        else:
            # If we're changing the product or location
            if (product != instance.product or location != instance.location):
                if InventoryItem.objects.filter(product=product, location=location).exists():
                    raise serializers.ValidationError(
                        {"non_field_errors": "An inventory item for this product and location already exists."}
                    )
        
        return data


# Keeping these aliases for backward compatibility during transition
InventoryItemListSerializer = InventoryItemSerializer
InventoryItemDetailSerializer = InventoryItemSerializer
InventoryItemCreateUpdateSerializer = InventoryItemSerializer


# InventoryTransaction serializers
class InventoryTransactionSerializer(serializers.ModelSerializer):
    """
    Base serializer for InventoryTransaction instances.
    Handles all inventory transaction operations with conditional field inclusion
    based on context or action.
    """
    # Fields for list view
    product_name = serializers.ReadOnlyField(source='product.name')
    location_name = serializers.ReadOnlyField(source='location.name')
    destination_location_name = serializers.ReadOnlyField(source='destination_location.name')
    transaction_type_display = serializers.ReadOnlyField(source='get_transaction_type_display')
    performed_by_username = serializers.ReadOnlyField(source='performed_by.username')
    total_value = serializers.ReadOnlyField()
    
    # Fields for detail view
    product = serializers.SerializerMethodField()
    location = serializers.SerializerMethodField()
    destination_location = serializers.SerializerMethodField()
    performed_by = serializers.SerializerMethodField()
    
    # Write-only fields for related objects
    product_id = serializers.PrimaryKeyRelatedField(
        source='product',
        queryset=Product.objects.all(),
        write_only=True
    )
    location_id = serializers.PrimaryKeyRelatedField(
        source='location',
        queryset=Location.objects.all(),
        write_only=True
    )
    destination_location_id = serializers.PrimaryKeyRelatedField(
        source='destination_location',
        queryset=Location.objects.all(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = InventoryTransaction
        fields = [
            'id', 'transaction_id', 'transaction_type', 'transaction_type_display',
            'product', 'product_id', 'product_name', 
            'location', 'location_id', 'location_name',
            'destination_location', 'destination_location_id', 'destination_location_name',
            'quantity', 'unit_price', 'reference', 'notes', 
            'performed_by', 'performed_by_username', 'total_value',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['transaction_id', 'created_at', 'updated_at']

    def __init__(self, *args, **kwargs):
        """
        Initialize the serializer with dynamic field sets based on context.
        """
        super().__init__(*args, **kwargs)
        
        # Get the request context to determine which fields to include
        request = self.context.get('request')
        if not request:
            return
            
        # For list action, exclude detailed fields
        if self.context.get('view') and self.context['view'].action == 'list':
            self.fields.pop('notes', None)
            
        # For create/update actions, use simplified representation
        if request.method in ['POST', 'PUT', 'PATCH']:
            self.fields.pop('product', None)
            self.fields.pop('location', None)
            self.fields.pop('destination_location', None)
            self.fields.pop('performed_by', None)
            self.fields.pop('product_name', None)
            self.fields.pop('location_name', None)
            self.fields.pop('destination_location_name', None)
            self.fields.pop('transaction_type_display', None)
            self.fields.pop('performed_by_username', None)
            self.fields.pop('total_value', None)
        else:  # For GET requests
            self.fields.pop('product_id', None)
            self.fields.pop('location_id', None)
            self.fields.pop('destination_location_id', None)

    def get_product(self, obj):
        """Return the full ProductSerializer representation for detail view."""
        if self.context.get('view') and self.context['view'].action == 'retrieve':
            return ProductSerializer(obj.product).data
        return obj.product_id
        
    def get_location(self, obj):
        """Return the full LocationSerializer representation for detail view."""
        if self.context.get('view') and self.context['view'].action == 'retrieve':
            return LocationSerializer(obj.location).data
        return obj.location_id
        
    def get_destination_location(self, obj):
        """Return the full LocationSerializer representation for the destination location."""
        if obj.destination_location and self.context.get('view') and self.context['view'].action == 'retrieve':
            return LocationSerializer(obj.destination_location).data
        return None
    
    def get_performed_by(self, obj):
        """Return the full UserSerializer representation for performed_by."""
        if self.context.get('view') and self.context['view'].action == 'retrieve':
            return UserSerializer(obj.performed_by).data
        return obj.performed_by_id
        
    def validate(self, data):
        """
        Validate transaction data based on transaction type.
        
        - For 'sold' and 'transferred' transactions: quantity must be negative
        - For 'received' and 'adjustment' transactions: quantity must be positive
        - For 'transferred' transactions: destination_location must be provided
        """
        transaction_type = data.get('transaction_type')
        quantity = data.get('quantity')
        destination_location = data.get('destination_location')
        
        # For 'sold' and 'transferred' transactions, quantity should be negative
        if transaction_type in ['sold', 'transferred'] and quantity >= 0:
            raise serializers.ValidationError({
                "quantity": f"Quantity must be negative for {transaction_type} transactions."
            })
            
        # For 'received' transactions, quantity should be positive
        elif transaction_type == 'received' and quantity <= 0:
            raise serializers.ValidationError({
                "quantity": "Quantity must be positive for received transactions."
            })
            
        # Validate transfer operations
        if transaction_type == 'transferred':
            # Ensure destination_location is provided for transfers
            if not destination_location:
                raise serializers.ValidationError({
                    "destination_location_id": "Destination location is required for transfers."
                })
            
            # Ensure destination_location is not the same as source location
            location = data.get('location')
            if destination_location == location:
                raise serializers.ValidationError({
                    "destination_location_id": "Destination location must be different from source location."
                })
            
        return data


# Keeping these aliases for backward compatibility during transition
InventoryTransactionListSerializer = InventoryTransactionSerializer
InventoryTransactionDetailSerializer = InventoryTransactionSerializer
InventoryTransactionCreateSerializer = InventoryTransactionSerializer


# InventoryCount serializers
class InventoryCountItemSerializer(serializers.ModelSerializer):
    """
    Serializer for InventoryCountItem instances.
    """
    product_name = serializers.ReadOnlyField(source='product.name')
    variance = serializers.ReadOnlyField()
    variance_percentage = serializers.ReadOnlyField()
    counted_by_username = serializers.SerializerMethodField()
    
    class Meta:
        model = InventoryCountItem
        fields = [
            'id', 'product', 'product_name', 'expected_quantity',
            'counted_quantity', 'is_counted', 'variance', 'variance_percentage',
            'counted_by', 'counted_by_username', 'counted_at', 'notes'
        ]
        read_only_fields = ['expected_quantity', 'counted_at']
        
    def get_counted_by_username(self, obj):
        """Get the username of the user who counted this item."""
        if obj.counted_by:
            return obj.counted_by.username
        return None


class InventoryCountListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing InventoryCount instances.
    """
    location_name = serializers.ReadOnlyField(source='location.name')
    status_display = serializers.ReadOnlyField(source='get_status_display')
    created_by_username = serializers.ReadOnlyField(source='created_by.username')
    completed_by_username = serializers.SerializerMethodField()
    progress_percentage = serializers.ReadOnlyField()
    
    class Meta:
        model = InventoryCount
        fields = [
            'id', 'count_id', 'name', 'location', 'location_name',
            'status', 'status_display', 'scheduled_date', 'completed_date',
            'created_by', 'created_by_username', 'completed_by', 'completed_by_username',
            'progress_percentage', 'total_items', 'completed_items',
            'created_at'
        ]
        read_only_fields = ['count_id', 'created_at', 'progress_percentage', 
                           'total_items', 'completed_items']
                           
    def get_completed_by_username(self, obj):
        """Get the username of the user who completed this count."""
        if obj.completed_by:
            return obj.completed_by.username
        return None


class InventoryCountDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for detailed InventoryCount information.
    """
    location = LocationSerializer(read_only=True)
    created_by = UserSerializer(read_only=True)
    completed_by = UserSerializer(read_only=True)
    status_display = serializers.ReadOnlyField(source='get_status_display')
    count_items = InventoryCountItemSerializer(many=True, read_only=True)
    progress_percentage = serializers.ReadOnlyField()
    total_items = serializers.ReadOnlyField()
    completed_items = serializers.ReadOnlyField()
    
    class Meta:
        model = InventoryCount
        fields = [
            'id', 'count_id', 'name', 'description', 'location',
            'status', 'status_display', 'scheduled_date', 'completed_date',
            'created_by', 'completed_by', 'notes', 'progress_percentage',
            'total_items', 'completed_items', 'count_items',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['count_id', 'created_at', 'updated_at', 
                           'progress_percentage', 'total_items', 'completed_items']


class InventoryCountCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and updating InventoryCount instances.
    """
    class Meta:
        model = InventoryCount
        fields = [
            'name', 'description', 'location', 'status',
            'scheduled_date', 'completed_date', 'created_by',
            'completed_by', 'notes', 'is_active'
        ]
        
    def validate(self, data):
        """
        Validate inventory count data.
        """
        status = data.get('status')
        completed_date = data.get('completed_date')
        completed_by = data.get('completed_by')
        
        # If status is 'completed', check that completed_date and completed_by are provided
        if status == 'completed':
            if not completed_date:
                raise serializers.ValidationError(
                    {"completed_date": "A completed date is required when status is 'completed'."}
                )
            if not completed_by:
                raise serializers.ValidationError(
                    {"completed_by": "A completed by user is required when status is 'completed'."}
                )
                
        # If completed_date or completed_by is provided, status should be 'completed'
        elif completed_date or completed_by:
            if status != 'completed':
                raise serializers.ValidationError(
                    {"status": "Status must be 'completed' when completed_date or completed_by is provided."}
                )
                
        return data


class InventoryCountItemUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating InventoryCountItem instances (for counting).
    """
    class Meta:
        model = InventoryCountItem
        fields = [
            'counted_quantity', 'is_counted', 'counted_by', 'notes'
        ]
        
    def validate(self, data):
        """
        Validate inventory count item data.
        """
        is_counted = data.get('is_counted', self.instance.is_counted if self.instance else False)
        counted_quantity = data.get('counted_quantity', self.instance.counted_quantity if self.instance else None)
        counted_by = data.get('counted_by', self.instance.counted_by if self.instance else None)
        
        # If is_counted is True, counted_quantity and counted_by must be provided
        if is_counted:
            if counted_quantity is None:
                raise serializers.ValidationError(
                    {"counted_quantity": "A counted quantity is required when marking as counted."}
                )
            if counted_by is None:
                raise serializers.ValidationError(
                    {"counted_by": "A counted by user is required when marking as counted."}
                )
                
        return data
        
    def update(self, instance, validated_data):
        """
        Update and return an existing InventoryCountItem instance.
        """
        # If marking as counted, set the counted_at timestamp
        if validated_data.get('is_counted') and not instance.is_counted:
            from django.utils import timezone
            validated_data['counted_at'] = timezone.now()
            
        return super().update(instance, validated_data) 

# Order serializers
class OrderItemSerializer(serializers.ModelSerializer):
    """
    Base serializer for OrderItem instances.
    Handles all order item operations with conditional field inclusion
    based on context or action.
    """
    # Fields for list view
    product_name = serializers.ReadOnlyField(source='product.name')
    total_price = serializers.ReadOnlyField()
    is_fully_received = serializers.ReadOnlyField()
    receiving_status = serializers.ReadOnlyField()
    
    # Fields for detail view
    product = serializers.SerializerMethodField()
    
    class Meta:
        model = OrderItem
        fields = [
            'id', 'product', 'product_name', 'quantity', 'unit_price',
            'received_quantity', 'notes', 'total_price', 'is_fully_received',
            'receiving_status', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def __init__(self, *args, **kwargs):
        """
        Initialize the serializer with dynamic field sets based on context.
        """
        super().__init__(*args, **kwargs)
        
        # Get the request context to determine which fields to include
        request = self.context.get('request')
        if not request:
            return
            
        # For list action, exclude detailed fields
        if self.context.get('view') and self.context['view'].action == 'list':
            self.fields.pop('notes', None)
            self.fields.pop('created_at', None)
            self.fields.pop('updated_at', None)
            
        # For create/update actions, use simplified representation
        if request.method in ['POST', 'PUT', 'PATCH']:
            self.fields.pop('product_name', None)
            self.fields.pop('total_price', None)
            self.fields.pop('is_fully_received', None)
            self.fields.pop('receiving_status', None)
    
    def get_product(self, obj):
        """Return the full ProductSerializer representation for detail view."""
        if self.context.get('view') and self.context['view'].action in ['retrieve', 'detail']:
            return ProductSerializer(obj.product).data
        return obj.product_id
    
    def validate(self, data):
        """
        Validate that the order-product combination is unique.
        """
        order = self.context.get('order')
        product = data.get('product')
        
        if not order:
            raise serializers.ValidationError(
                {"order": "Order is required for creating/updating order items."}
            )
        
        # Check if we're creating a new object or updating an existing one
        instance = self.instance
        
        # If instance is None, we're creating a new object
        if instance is None:
            if OrderItem.objects.filter(order=order, product=product).exists():
                raise serializers.ValidationError(
                    {"product": "This product is already in the order."}
                )
                
        # If instance is not None, we're updating an existing object
        else:
            # If we're changing the product
            if product != instance.product:
                if OrderItem.objects.filter(order=order, product=product).exists():
                    raise serializers.ValidationError(
                        {"product": "This product is already in the order."}
                    )
                    
        return data


class OrderSerializer(serializers.ModelSerializer):
    """
    Base serializer for Order instances.
    Handles all order operations with conditional field inclusion
    based on context or action.
    """
    # Fields for list view
    supplier_name = serializers.ReadOnlyField(source='supplier.name')
    status_display = serializers.ReadOnlyField(source='get_status_display')
    created_by_username = serializers.ReadOnlyField(source='created_by.username')
    updated_by_username = serializers.SerializerMethodField()
    subtotal = serializers.ReadOnlyField()
    total = serializers.ReadOnlyField()
    item_count = serializers.SerializerMethodField()
    
    # Fields for detail view
    supplier = serializers.SerializerMethodField()
    created_by = serializers.SerializerMethodField()
    updated_by = serializers.SerializerMethodField()
    items = serializers.SerializerMethodField()
    
    # Write-only fields
    supplier_id = serializers.PrimaryKeyRelatedField(
        source='supplier',
        queryset=Supplier.objects.all(),
        write_only=True
    )
    items_data = OrderItemSerializer(many=True, required=False, write_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'supplier', 'supplier_id', 'supplier_name',
            'status', 'status_display', 'order_date', 'expected_delivery_date',
            'actual_delivery_date', 'shipping_cost', 'tax', 'discount', 'notes',
            'created_by', 'created_by_username', 'updated_by', 'updated_by_username',
            'subtotal', 'total', 'item_count', 'items', 'items_data',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['order_number', 'created_at', 'updated_at']
    
    def __init__(self, *args, **kwargs):
        """
        Initialize the serializer with dynamic field sets based on context.
        """
        super().__init__(*args, **kwargs)
        
        # Get the request context to determine which fields to include
        request = self.context.get('request')
        if not request:
            return
            
        # For list action, exclude detailed fields
        if self.context.get('view') and self.context['view'].action == 'list':
            self.fields.pop('notes', None)
            self.fields.pop('shipping_cost', None)
            self.fields.pop('tax', None)
            self.fields.pop('discount', None)
            self.fields.pop('items', None)
            
        # For create/update actions, use simplified representation
        if request.method in ['POST', 'PUT', 'PATCH']:
            self.fields.pop('supplier', None)
            self.fields.pop('supplier_name', None)
            self.fields.pop('status_display', None)
            self.fields.pop('created_by', None)
            self.fields.pop('created_by_username', None)
            self.fields.pop('updated_by', None)
            self.fields.pop('updated_by_username', None)
            self.fields.pop('subtotal', None)
            self.fields.pop('total', None)
            self.fields.pop('item_count', None)
            self.fields.pop('items', None)
        else:  # For GET requests
            self.fields.pop('supplier_id', None)
            self.fields.pop('items_data', None)
    
    def get_supplier(self, obj):
        """Return the full SupplierSerializer representation for detail view."""
        if self.context.get('view') and self.context['view'].action == 'retrieve':
            return SupplierSerializer(obj.supplier).data
        return obj.supplier_id
    
    def get_created_by(self, obj):
        """Return the full UserSerializer representation for created_by."""
        if self.context.get('view') and self.context['view'].action == 'retrieve':
            return UserSerializer(obj.created_by).data if obj.created_by else None
        return obj.created_by_id if obj.created_by else None
    
    def get_updated_by(self, obj):
        """Return the full UserSerializer representation for updated_by."""
        if self.context.get('view') and self.context['view'].action == 'retrieve':
            return UserSerializer(obj.updated_by).data if obj.updated_by else None
        return obj.updated_by_id if obj.updated_by else None
    
    def get_updated_by_username(self, obj):
        """Get the username of the user who updated this order."""
        if obj.updated_by:
            return obj.updated_by.username
        return None
    
    def get_item_count(self, obj):
        """Get the number of items in this order."""
        return obj.items.count()
    
    def get_items(self, obj):
        """Return OrderItemSerializer instances for all items in this order."""
        # Only return items in detail view
        if self.context.get('view') and self.context['view'].action == 'retrieve':
            return OrderItemSerializer(obj.items.all(), many=True, context=self.context).data
        return None
    
    def validate(self, data):
        """
        Validate order data based on status.
        """
        status = data.get('status', self.instance.status if self.instance else None)
        order_date = data.get('order_date', self.instance.order_date if self.instance else None)
        actual_delivery_date = data.get('actual_delivery_date', 
                                      self.instance.actual_delivery_date if self.instance else None)
        
        # If status is 'placed', order_date is required
        if status == 'placed' and not order_date:
            raise serializers.ValidationError(
                {"order_date": "Order date is required when status is 'placed'."}
            )
            
        # If status is 'received', actual_delivery_date is required
        if status == 'received' and not actual_delivery_date:
            raise serializers.ValidationError(
                {"actual_delivery_date": "Actual delivery date is required when status is 'received'."}
            )
            
        return data
    
    def create(self, validated_data):
        """
        Create and return a new Order instance with OrderItems.
        """
        items_data = validated_data.pop('items_data', [])
        
        # Generate an order number if not provided
        if not validated_data.get('order_number'):
            import uuid
            validated_data['order_number'] = f"ORD-{uuid.uuid4().hex[:8].upper()}"
        
        # Create the order
        order = Order.objects.create(**validated_data)
        
        # Create order items
        for item_data in items_data:
            OrderItem.objects.create(order=order, **item_data)
            
        return order
    
    def update(self, instance, validated_data):
        """
        Update and return an existing Order instance with OrderItems.
        """
        items_data = validated_data.pop('items_data', None)
        
        # Update the order fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # If items_data is provided, update or create order items
        if items_data is not None:
            # Optional: Update or create order items
            # This is a simplified approach; in a real application,
            # you might want to handle updates to existing items and deletions
            instance.items.all().delete()
            for item_data in items_data:
                OrderItem.objects.create(order=instance, **item_data)
        
        return instance


# Keeping these aliases for backward compatibility during transition
OrderItemListSerializer = OrderItemSerializer
OrderItemDetailSerializer = OrderItemSerializer
OrderItemCreateUpdateSerializer = OrderItemSerializer
OrderListSerializer = OrderSerializer
OrderDetailSerializer = OrderSerializer
OrderCreateSerializer = OrderSerializer
OrderUpdateSerializer = OrderSerializer 