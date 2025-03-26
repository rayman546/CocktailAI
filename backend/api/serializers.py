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
class ProductListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing Product instances.
    """
    category_name = serializers.ReadOnlyField(source='category.name')
    supplier_name = serializers.ReadOnlyField(source='supplier.name')
    total_quantity = serializers.ReadOnlyField()
    total_value = serializers.ReadOnlyField()
    below_par_level = serializers.ReadOnlyField()
    needs_reorder = serializers.ReadOnlyField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'sku', 'barcode', 'image',
            'category', 'category_name', 'supplier', 'supplier_name',
            'unit_price', 'unit_size', 'unit_type',
            'par_level', 'reorder_point', 'reorder_quantity',
            'total_quantity', 'total_value', 'below_par_level', 'needs_reorder',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class ProductDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for detailed Product information.
    """
    category = CategorySerializer(read_only=True)
    supplier = SupplierSerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        source='category',
        queryset=Category.objects.all(),
        write_only=True
    )
    supplier_id = serializers.PrimaryKeyRelatedField(
        source='supplier',
        queryset=Supplier.objects.all(),
        write_only=True
    )
    total_quantity = serializers.ReadOnlyField()
    total_value = serializers.ReadOnlyField()
    below_par_level = serializers.ReadOnlyField()
    needs_reorder = serializers.ReadOnlyField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'sku', 'description', 'barcode', 'image',
            'category', 'category_id', 'supplier', 'supplier_id',
            'unit_price', 'unit_size', 'unit_type',
            'par_level', 'reorder_point', 'reorder_quantity',
            'notes', 'total_quantity', 'total_value', 
            'below_par_level', 'needs_reorder',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class ProductCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and updating Product instances.
    """
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'sku', 'description', 'barcode', 'image',
            'category', 'supplier', 'unit_price', 'unit_size', 'unit_type',
            'par_level', 'reorder_point', 'reorder_quantity', 'notes',
            'is_active'
        ]


# InventoryItem serializers
class InventoryItemListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing InventoryItem instances.
    """
    product_name = serializers.ReadOnlyField(source='product.name')
    location_name = serializers.ReadOnlyField(source='location.name')
    value = serializers.ReadOnlyField()
    
    class Meta:
        model = InventoryItem
        fields = [
            'id', 'product', 'product_name', 'location', 'location_name',
            'quantity', 'value', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class InventoryItemDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for detailed InventoryItem information.
    """
    product = ProductListSerializer(read_only=True)
    location = LocationSerializer(read_only=True)
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
    value = serializers.ReadOnlyField()
    
    class Meta:
        model = InventoryItem
        fields = [
            'id', 'product', 'product_id', 'location', 'location_id',
            'quantity', 'value', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class InventoryItemCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and updating InventoryItem instances.
    """
    class Meta:
        model = InventoryItem
        fields = [
            'id', 'product', 'location', 'quantity', 'is_active'
        ]
        
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

# InventoryTransaction serializers
class InventoryTransactionListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing InventoryTransaction instances.
    """
    product_name = serializers.ReadOnlyField(source='product.name')
    location_name = serializers.ReadOnlyField(source='location.name')
    transaction_type_display = serializers.ReadOnlyField(source='get_transaction_type_display')
    performed_by_username = serializers.ReadOnlyField(source='performed_by.username')
    total_value = serializers.ReadOnlyField()
    
    class Meta:
        model = InventoryTransaction
        fields = [
            'id', 'transaction_id', 'transaction_type', 'transaction_type_display',
            'product', 'product_name', 'location', 'location_name',
            'quantity', 'unit_price', 'reference', 'performed_by', 
            'performed_by_username', 'total_value', 'created_at'
        ]
        read_only_fields = ['transaction_id', 'created_at']


class InventoryTransactionDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for detailed InventoryTransaction information.
    """
    product = ProductListSerializer(read_only=True)
    location = LocationSerializer(read_only=True)
    performed_by = UserSerializer(read_only=True)
    transaction_type_display = serializers.ReadOnlyField(source='get_transaction_type_display')
    total_value = serializers.ReadOnlyField()
    
    class Meta:
        model = InventoryTransaction
        fields = [
            'id', 'transaction_id', 'transaction_type', 'transaction_type_display',
            'product', 'location', 'quantity', 'unit_price', 
            'reference', 'notes', 'performed_by', 'total_value',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['transaction_id', 'created_at', 'updated_at']


class InventoryTransactionCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating InventoryTransaction instances.
    """
    class Meta:
        model = InventoryTransaction
        fields = [
            'transaction_type', 'product', 'location', 
            'quantity', 'unit_price', 'reference', 'notes', 'performed_by'
        ]
        
    def validate(self, data):
        """
        Validate transaction data.
        """
        transaction_type = data.get('transaction_type')
        quantity = data.get('quantity')
        
        # For 'sold' and 'transferred' transactions, quantity should be negative
        if transaction_type in ['sold', 'transferred'] and quantity > 0:
            data['quantity'] = -abs(quantity)
            
        # For 'received' transactions, quantity should be positive
        elif transaction_type == 'received' and quantity < 0:
            data['quantity'] = abs(quantity)
            
        return data


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
class OrderItemListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing OrderItem instances.
    """
    product_name = serializers.ReadOnlyField(source='product.name')
    total_price = serializers.ReadOnlyField()
    is_fully_received = serializers.ReadOnlyField()
    receiving_status = serializers.ReadOnlyField()
    
    class Meta:
        model = OrderItem
        fields = [
            'id', 'product', 'product_name', 'quantity', 'unit_price',
            'received_quantity', 'total_price', 'is_fully_received',
            'receiving_status', 'is_active'
        ]


class OrderItemDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for detailed OrderItem information.
    """
    product = ProductListSerializer(read_only=True)
    total_price = serializers.ReadOnlyField()
    is_fully_received = serializers.ReadOnlyField()
    receiving_status = serializers.ReadOnlyField()
    
    class Meta:
        model = OrderItem
        fields = [
            'id', 'product', 'quantity', 'unit_price', 'received_quantity',
            'notes', 'total_price', 'is_fully_received', 'receiving_status',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class OrderItemCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and updating OrderItem instances.
    """
    class Meta:
        model = OrderItem
        fields = [
            'product', 'quantity', 'unit_price', 'received_quantity',
            'notes', 'is_active'
        ]
        
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


class OrderListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing Order instances.
    """
    supplier_name = serializers.ReadOnlyField(source='supplier.name')
    status_display = serializers.ReadOnlyField(source='get_status_display')
    created_by_username = serializers.ReadOnlyField(source='created_by.username')
    updated_by_username = serializers.SerializerMethodField()
    subtotal = serializers.ReadOnlyField()
    total = serializers.ReadOnlyField()
    item_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'supplier', 'supplier_name',
            'status', 'status_display', 'order_date', 'expected_delivery_date',
            'actual_delivery_date', 'created_by', 'created_by_username',
            'updated_by', 'updated_by_username', 'subtotal', 'total',
            'item_count', 'created_at'
        ]
        read_only_fields = ['order_number', 'created_at']
        
    def get_updated_by_username(self, obj):
        """Get the username of the user who updated this order."""
        if obj.updated_by:
            return obj.updated_by.username
        return None
        
    def get_item_count(self, obj):
        """Get the number of items in this order."""
        return obj.items.count()


class OrderDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for detailed Order information.
    """
    supplier = SupplierSerializer(read_only=True)
    created_by = UserSerializer(read_only=True)
    updated_by = UserSerializer(read_only=True)
    status_display = serializers.ReadOnlyField(source='get_status_display')
    items = OrderItemListSerializer(many=True, read_only=True)
    subtotal = serializers.ReadOnlyField()
    total = serializers.ReadOnlyField()
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'supplier', 'status', 'status_display',
            'order_date', 'expected_delivery_date', 'actual_delivery_date',
            'shipping_cost', 'tax', 'discount', 'notes', 'subtotal', 'total',
            'created_by', 'updated_by', 'items', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['order_number', 'created_at', 'updated_at']


class OrderCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating Order instances.
    """
    items = OrderItemCreateUpdateSerializer(many=True, required=False)
    
    class Meta:
        model = Order
        fields = [
            'supplier', 'status', 'order_date', 'expected_delivery_date',
            'shipping_cost', 'tax', 'discount', 'notes', 'created_by',
            'updated_by', 'items', 'is_active'
        ]
        
    def validate(self, data):
        """
        Validate order data based on status.
        """
        status = data.get('status')
        order_date = data.get('order_date')
        
        # If status is 'placed', order_date is required
        if status == 'placed' and not order_date:
            raise serializers.ValidationError(
                {"order_date": "Order date is required when status is 'placed'."}
            )
            
        # If status is 'received', actual_delivery_date is required
        if status == 'received' and not data.get('actual_delivery_date'):
            raise serializers.ValidationError(
                {"actual_delivery_date": "Actual delivery date is required when status is 'received'."}
            )
            
        return data
        
    def create(self, validated_data):
        """
        Create and return a new Order instance with OrderItems.
        """
        items_data = validated_data.pop('items', [])
        
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


class OrderUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating Order instances.
    """
    class Meta:
        model = Order
        fields = [
            'supplier', 'status', 'order_date', 'expected_delivery_date',
            'actual_delivery_date', 'shipping_cost', 'tax', 'discount',
            'notes', 'updated_by', 'is_active'
        ]
        
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