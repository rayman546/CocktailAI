"""
Models for the inventory app.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.core.validators import MinValueValidator
from .validators import no_future_date_validator, date_not_before_validator, date_before_today_validator
import uuid
from django.utils import timezone


class BaseModel(models.Model):
    """
    Base model for all inventory models.
    
    Includes common fields and functionality.
    """
    
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated At"), auto_now=True)
    is_active = models.BooleanField(_("Active"), default=True)
    
    class Meta:
        abstract = True


class Category(BaseModel):
    """
    Product category model.
    
    Used to categorize products (e.g., Spirits, Beer, Wine, etc.)
    """
    
    name = models.CharField(_("Name"), max_length=100, unique=True)
    description = models.TextField(_("Description"), blank=True)
    
    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")
        ordering = ["name"]
    
    def __str__(self):
        """Return the category name."""
        return self.name


class Supplier(BaseModel):
    """
    Supplier model for product vendors.
    
    This model represents companies or individuals that supply products to the business.
    It stores contact information and related details about suppliers.
    
    Fields:
        name (CharField): The name of the supplier (max length: 255 chars).
        contact_name (CharField): Name of the primary contact person (optional, max length: 255 chars).
        email (EmailField): Email address for the supplier/contact (optional, validated with email_validator).
        phone (CharField): Phone number (optional, max length: 20 chars, validated with phone_number_validator).
        address (TextField): Physical address of the supplier (optional).
        website (URLField): Supplier's website URL (optional).
        notes (TextField): Additional information about the supplier (optional).
    
    Validators:
        - email: Must be a valid email format (email_validator)
        - phone: Must be a valid phone number format (phone_number_validator)
    """
    
    name = models.CharField(_("Name"), max_length=255)
    contact_name = models.CharField(_("Contact Name"), max_length=255, blank=True)
    email = models.EmailField(
        _("Email"), 
        blank=True,
        validators=[email_validator]
    )
    phone = models.CharField(
        _("Phone"), 
        max_length=20, 
        blank=True,
        validators=[phone_number_validator]
    )
    address = models.TextField(_("Address"), blank=True)
    website = models.URLField(_("Website"), blank=True)
    notes = models.TextField(_("Notes"), blank=True)
    
    class Meta:
        verbose_name = _("Supplier")
        verbose_name_plural = _("Suppliers")
        ordering = ["name"]
    
    def __str__(self):
        """Return the supplier name."""
        return self.name


class Location(BaseModel):
    """
    Location model for storing inventory in different places.
    
    Used to track inventory across different bars, storage areas, etc.
    """
    
    name = models.CharField(_("Name"), max_length=100)
    description = models.TextField(_("Description"), blank=True)
    is_storage = models.BooleanField(_("Is Storage Location"), default=False)
    is_service = models.BooleanField(_("Is Service Location"), default=False)
    
    class Meta:
        verbose_name = _("Location")
        verbose_name_plural = _("Locations")
        ordering = ["name"]
    
    def __str__(self):
        """Return the location name."""
        return self.name


class Product(BaseModel):
    """
    Product model for inventory items.
    
    This model represents inventory products that can be bought, sold, and tracked.
    It includes information about pricing, classification, supplier, and inventory management.
    
    Fields:
        name (CharField): The name of the product (max length: 255 chars).
        sku (CharField): Stock Keeping Unit identifier (optional, max length: 50 chars).
        description (TextField): Detailed description of the product (optional).
        image (ImageField): Product image file (optional).
        barcode (CharField): UPC/EAN barcode for the product (optional, max length: 100 chars).
        category (ForeignKey): Product category reference.
        supplier (ForeignKey): Supplier reference.
        unit_price (DecimalField): Price per unit, validated to be non-negative.
        unit_size (DecimalField): Size of the unit (e.g., 750ml for a standard wine bottle), must be positive.
        unit_type (CharField): Type of unit (bottle, can, keg, etc.).
        par_level (DecimalField): Target inventory level to maintain, must be non-negative.
        reorder_point (DecimalField): Inventory level at which to reorder, must be non-negative.
        reorder_quantity (DecimalField): Quantity to reorder when reorder_point is reached, must be positive.
        notes (TextField): Additional information about the product (optional).
    
    Validators:
        - unit_price: Must be non-negative (MinValueValidator and currency_validator)
        - unit_size: Must be positive (MinValueValidator)
        - par_level: Must be non-negative (MinValueValidator)
        - reorder_point: Must be non-negative (MinValueValidator)
        - reorder_quantity: Must be positive (MinValueValidator)
    
    Properties:
        total_quantity: Sum of the product quantity across all locations.
        total_value: Total inventory value of the product (quantity * unit_price).
        below_par_level: Whether the total quantity is less than the par_level.
        needs_reorder: Whether the total quantity is less than or equal to the reorder_point.
    """
    
    UNIT_TYPE_CHOICES = [
        ("bottle", _("Bottle")),
        ("can", _("Can")),
        ("keg", _("Keg")),
        ("case", _("Case")),
        ("box", _("Box")),
        ("each", _("Each")),
        ("weight", _("Weight")),
        ("volume", _("Volume")),
    ]
    
    # Basic information
    name = models.CharField(_("Name"), max_length=255)
    sku = models.CharField(_("SKU"), max_length=50, blank=True)
    description = models.TextField(_("Description"), blank=True)
    image = models.ImageField(_("Image"), upload_to="products/", blank=True, null=True)
    barcode = models.CharField(_("Barcode"), max_length=100, blank=True)
    
    # Classification
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="products",
        verbose_name=_("Category")
    )
    
    # Supplier information
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.PROTECT,
        related_name="products",
        verbose_name=_("Supplier")
    )
    
    # Pricing
    unit_price = models.DecimalField(
        _("Unit Price"),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0), currency_validator()]
    )
    
    # Inventory management
    unit_size = models.DecimalField(
        _("Unit Size"),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text=_("Size of the unit (e.g., 750ml for a standard wine bottle)")
    )
    unit_type = models.CharField(
        _("Unit Type"),
        max_length=20,
        choices=UNIT_TYPE_CHOICES,
        default="bottle"
    )
    par_level = models.DecimalField(
        _("Par Level"),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        default=0,
        help_text=_("Target inventory level to maintain")
    )
    reorder_point = models.DecimalField(
        _("Reorder Point"),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        default=0,
        help_text=_("Inventory level at which to reorder")
    )
    reorder_quantity = models.DecimalField(
        _("Reorder Quantity"),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        default=1,
        help_text=_("Quantity to reorder when reorder point is reached")
    )
    
    # Additional information
    notes = models.TextField(_("Notes"), blank=True)
    
    class Meta:
        verbose_name = _("Product")
        verbose_name_plural = _("Products")
        ordering = ["name"]
        unique_together = [["supplier", "sku"]]
    
    def __str__(self):
        """Return the product name."""
        return self.name
    
    @property
    def total_quantity(self):
        """Calculate total quantity across all locations."""
        return sum(item.quantity for item in self.inventory_items.all())
    
    @property
    def total_value(self):
        """Calculate total inventory value."""
        return self.total_quantity * self.unit_price
    
    @property
    def below_par_level(self):
        """Check if total quantity is below par level."""
        return self.total_quantity < self.par_level
    
    @property
    def needs_reorder(self):
        """Check if total quantity is at or below reorder point."""
        return self.total_quantity <= self.reorder_point


class InventoryItem(BaseModel):
    """
    InventoryItem model to track product quantities at specific locations.
    """
    
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="inventory_items",
        verbose_name=_("Product")
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.CASCADE,
        related_name="inventory_items",
        verbose_name=_("Location")
    )
    quantity = models.DecimalField(
        _("Quantity"),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        default=0
    )
    
    class Meta:
        verbose_name = _("Inventory Item")
        verbose_name_plural = _("Inventory Items")
        unique_together = [["product", "location"]]
    
    def __str__(self):
        """Return product and location information."""
        return f"{self.product.name} at {self.location.name}: {self.quantity}"
    
    @property
    def value(self):
        """Calculate the value of this inventory item."""
        return self.quantity * self.product.unit_price


class InventoryTransaction(BaseModel):
    """
    InventoryTransaction model to track changes in inventory.
    
    This model records all inventory movements including receiving products,
    selling products, transferring between locations, adjustments, and inventory counts.
    
    Fields:
        transaction_id (UUIDField): Unique identifier for the transaction (auto-generated).
        transaction_type (CharField): Type of transaction (received, sold, transferred, adjustment, count).
        transaction_date (DateField): Date when the transaction occurred (defaults to now, cannot be in future).
        product (ForeignKey): Reference to the product being transacted.
        location (ForeignKey): Location where the transaction occurred (source location for transfers).
        destination_location (ForeignKey): Destination location for transfer transactions (optional).
        quantity (DecimalField): Quantity of product involved in the transaction 
                              (positive for received/adjustment, negative for sold/transferred).
        unit_price (DecimalField): Unit price at the time of transaction (must be non-negative).
        reference (CharField): Reference number or identifier for the transaction (optional, max length: 100 chars).
        performed_by (ForeignKey): User who performed the transaction.
        notes (TextField): Additional information about the transaction (optional).
    
    Validators:
        - quantity: Must be positive for 'received' transactions and negative for 'sold' and 'transferred' transactions.
        - unit_price: Must be non-negative (MinValueValidator).
        - transaction_date: Cannot be in the future (no_future_date_validator).
    
    Model-level validation:
        - For 'transferred' transactions, destination_location is required.
        - destination_location must be different from the source location for transfers.
        - Appropriate quantity sign validation based on transaction_type.
    """
    
    TRANSACTION_TYPE_CHOICES = [
        ("received", _("Received")),
        ("sold", _("Sold")),
        ("transferred", _("Transferred")),
        ("adjustment", _("Adjustment")),
        ("count", _("Inventory Count")),
    ]
    
    transaction_id = models.UUIDField(
        _("Transaction ID"),
        default=uuid.uuid4,
        editable=False,
        unique=True
    )
    transaction_type = models.CharField(
        _("Transaction Type"),
        max_length=20,
        choices=TRANSACTION_TYPE_CHOICES
    )
    transaction_date = models.DateField(
        _("Transaction Date"),
        default=timezone.now,
        validators=[no_future_date_validator],
        help_text=_("Date when the transaction occurred")
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="transactions",
        verbose_name=_("Product")
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.PROTECT,
        related_name="transactions",
        verbose_name=_("Location")
    )
    destination_location = models.ForeignKey(
        Location,
        on_delete=models.PROTECT,
        related_name="incoming_transactions",
        verbose_name=_("Destination Location"),
        null=True,
        blank=True,
        help_text=_("For transfers, the location where the product is being moved to")
    )
    quantity = models.DecimalField(
        _("Quantity"),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text=_("For transfers and sales, use negative values")
    )
    unit_price = models.DecimalField(
        _("Unit Price"),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        default=0
    )
    reference = models.CharField(_("Reference"), max_length=255, blank=True)
    notes = models.TextField(_("Notes"), blank=True)
    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="inventory_transactions",
        verbose_name=_("Performed By")
    )
    
    class Meta:
        verbose_name = _("Inventory Transaction")
        verbose_name_plural = _("Inventory Transactions")
        ordering = ["-created_at"]
    
    def __str__(self):
        """Return transaction information."""
        return f"{self.get_transaction_type_display()} - {self.product.name}: {self.quantity}"
    
    @property
    def total_value(self):
        """Calculate the total value of this transaction."""
        return abs(self.quantity) * self.unit_price
    
    def clean(self):
        """
        Validate transaction data based on type.
        """
        from django.core.exceptions import ValidationError
        
        # Ensure destination_location is set for transfers
        if self.transaction_type == "transferred" and not self.destination_location:
            raise ValidationError({"destination_location": _("Destination location is required for transfers.")})
            
        # Ensure destination_location is not the same as source location
        if self.transaction_type == "transferred" and self.destination_location == self.location:
            raise ValidationError({"destination_location": _("Destination location must be different from source location.")})
            
        # Ensure quantity is negative for sold and transferred transactions
        if self.transaction_type in ["sold", "transferred"] and self.quantity >= 0:
            raise ValidationError({"quantity": _(f"Quantity must be negative for {self.get_transaction_type_display()} transactions.")})
            
        # Ensure quantity is positive for received transactions
        if self.transaction_type == "received" and self.quantity <= 0:
            raise ValidationError({"quantity": _("Quantity must be positive for received transactions.")})


class InventoryCount(BaseModel):
    """
    InventoryCount model for physical inventory counting sessions.
    """
    
    STATUS_CHOICES = [
        ("in_progress", _("In Progress")),
        ("completed", _("Completed")),
        ("cancelled", _("Cancelled")),
    ]
    
    count_id = models.UUIDField(
        _("Count ID"),
        default=uuid.uuid4,
        editable=False,
        unique=True
    )
    name = models.CharField(_("Name"), max_length=255)
    description = models.TextField(_("Description"), blank=True)
    location = models.ForeignKey(
        Location,
        on_delete=models.PROTECT,
        related_name="inventory_counts",
        verbose_name=_("Location")
    )
    status = models.CharField(
        _("Status"),
        max_length=20,
        choices=STATUS_CHOICES,
        default="in_progress"
    )
    scheduled_date = models.DateField(_("Scheduled Date"), null=True, blank=True)
    completed_date = models.DateTimeField(
        _("Completed Date"), 
        null=True, 
        blank=True,
        validators=[no_future_date_validator]
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_inventory_counts",
        verbose_name=_("Created By")
    )
    completed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="completed_inventory_counts",
        verbose_name=_("Completed By"),
        null=True,
        blank=True
    )
    notes = models.TextField(_("Notes"), blank=True)
    
    class Meta:
        verbose_name = _("Inventory Count")
        verbose_name_plural = _("Inventory Counts")
        ordering = ["-created_at"]
    
    def __str__(self):
        """Return count information."""
        return f"{self.name} ({self.location.name}) - {self.get_status_display()}"
    
    @property
    def total_items(self):
        """Get the total number of items in this count."""
        return self.count_items.count()
    
    @property
    def completed_items(self):
        """Get the number of completed items in this count."""
        return self.count_items.filter(is_counted=True).count()
    
    @property
    def progress_percentage(self):
        """Calculate the percentage of completed items."""
        if self.total_items == 0:
            return 0
        return int((self.completed_items / self.total_items) * 100)
    
    def clean(self):
        """
        Validate inventory count data.
        """
        from django.core.exceptions import ValidationError
        
        # If completed_date is provided, ensure it's not in the future
        if self.completed_date:
            no_future_date_validator(self.completed_date)
        
        # If scheduled_date and completed_date are both provided, ensure scheduled_date is not after completed_date
        if self.scheduled_date and self.completed_date:
            completed_date = self.completed_date
            if isinstance(completed_date, datetime):
                completed_date = completed_date.date()
                
            if self.scheduled_date > completed_date:
                raise ValidationError({
                    "scheduled_date": _("Scheduled date cannot be after completed date.")
                })


class InventoryCountItem(BaseModel):
    """
    InventoryCountItem model for individual items in a counting session.
    """
    
    inventory_count = models.ForeignKey(
        InventoryCount,
        on_delete=models.CASCADE,
        related_name="count_items",
        verbose_name=_("Inventory Count")
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="count_items",
        verbose_name=_("Product")
    )
    expected_quantity = models.DecimalField(
        _("Expected Quantity"),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        default=0
    )
    counted_quantity = models.DecimalField(
        _("Counted Quantity"),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        null=True,
        blank=True
    )
    is_counted = models.BooleanField(_("Is Counted"), default=False)
    counted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="counted_items",
        verbose_name=_("Counted By"),
        null=True,
        blank=True
    )
    counted_at = models.DateTimeField(
        _("Counted At"), 
        null=True, 
        blank=True,
        validators=[no_future_date_validator]
    )
    notes = models.TextField(_("Notes"), blank=True)
    
    class Meta:
        verbose_name = _("Inventory Count Item")
        verbose_name_plural = _("Inventory Count Items")
        ordering = ["product__name"]
        unique_together = [["inventory_count", "product"]]
    
    def __str__(self):
        """Return count item information."""
        return f"{self.product.name} - {self.inventory_count.name}"
    
    @property
    def variance(self):
        """Calculate the variance between expected and counted quantities."""
        if self.is_counted and self.counted_quantity is not None:
            return self.counted_quantity - self.expected_quantity
        return None
    
    @property
    def variance_percentage(self):
        """Calculate the variance percentage."""
        if self.is_counted and self.counted_quantity is not None and self.expected_quantity > 0:
            return (self.variance / self.expected_quantity) * 100
        return None


class Order(BaseModel):
    """
    Order model for purchase orders to suppliers.
    
    This model tracks orders placed to suppliers for inventory replenishment.
    It includes order status, dates, financial information, and related order details.
    
    Fields:
        order_number (CharField): Unique identifier for the order (max length: 50 chars).
        supplier (ForeignKey): Reference to the supplier this order is placed with.
        status (CharField): Current status of the order (draft, pending, placed, received, cancelled).
        order_date (DateField): Date when the order was placed (optional, cannot be in the future).
        expected_delivery_date (DateField): Expected date of delivery (optional).
        actual_delivery_date (DateField): Date when the order was actually received (optional, cannot be in the future).
        shipping_cost (DecimalField): Cost of shipping (optional, must be non-negative).
        tax (DecimalField): Tax amount for the order (optional, must be non-negative).
        discount (DecimalField): Discount amount for the order (optional, must be non-negative).
        notes (TextField): Additional information about the order (optional).
        created_by (ForeignKey): User who created the order.
        updated_by (ForeignKey): User who last updated the order (optional).
    
    Validators:
        - order_date: Cannot be in the future (no_future_date_validator)
        - actual_delivery_date: Cannot be in the future (no_future_date_validator)
        - shipping_cost: Must be non-negative (MinValueValidator and currency_validator)
        - tax: Must be non-negative (MinValueValidator and currency_validator)
        - discount: Must be non-negative (MinValueValidator and currency_validator)
    
    Model-level validation:
        - If status is 'placed', order_date is required
        - If status is 'received', actual_delivery_date is required
        - expected_delivery_date cannot be before order_date
        - actual_delivery_date cannot be before order_date
    
    Properties:
        subtotal: Sum of all order items' total prices.
        total: subtotal + shipping_cost + tax - discount.
    """
    
    STATUS_CHOICES = [
        ("draft", _("Draft")),
        ("pending", _("Pending")),
        ("placed", _("Placed")),
        ("received", _("Received")),
        ("cancelled", _("Cancelled")),
    ]
    
    order_number = models.CharField(_("Order Number"), max_length=50, unique=True)
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.PROTECT,
        related_name="orders",
        verbose_name=_("Supplier")
    )
    status = models.CharField(
        _("Status"),
        max_length=20,
        choices=STATUS_CHOICES,
        default="draft"
    )
    order_date = models.DateField(
        _("Order Date"), 
        null=True, 
        blank=True,
        validators=[no_future_date_validator]
    )
    expected_delivery_date = models.DateField(_("Expected Delivery Date"), null=True, blank=True)
    actual_delivery_date = models.DateField(
        _("Actual Delivery Date"), 
        null=True, 
        blank=True,
        validators=[no_future_date_validator]
    )
    shipping_cost = models.DecimalField(
        _("Shipping Cost"),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0), currency_validator()],
        default=0
    )
    tax = models.DecimalField(
        _("Tax"),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0), currency_validator()],
        default=0
    )
    discount = models.DecimalField(
        _("Discount"),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0), currency_validator()],
        default=0
    )
    notes = models.TextField(_("Notes"), blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_orders",
        verbose_name=_("Created By")
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="updated_orders",
        verbose_name=_("Updated By"),
        null=True,
        blank=True
    )
    
    class Meta:
        verbose_name = _("Order")
        verbose_name_plural = _("Orders")
        ordering = ["-created_at"]
    
    def __str__(self):
        """Return order information."""
        return f"Order #{self.order_number} - {self.supplier.name}"
    
    @property
    def subtotal(self):
        """Calculate the subtotal of all order items."""
        return sum(item.total_price for item in self.items.all())
    
    @property
    def total(self):
        """Calculate the total order cost including shipping, tax, and discount."""
        return self.subtotal + self.shipping_cost + self.tax - self.discount
    
    def clean(self):
        """
        Validate order data based on status and dates.
        """
        from django.core.exceptions import ValidationError
        
        # If status is 'placed', order_date is required and should not be in the future
        if self.status == 'placed' and not self.order_date:
            raise ValidationError({
                "order_date": _("Order date is required when status is 'placed'.")
            })
        
        # If order_date is provided, it should not be in the future
        if self.order_date:
            no_future_date_validator(self.order_date)
            
        # If actual_delivery_date is provided, it should not be in the future
        if self.actual_delivery_date:
            no_future_date_validator(self.actual_delivery_date)
            
        # If order_date and expected_delivery_date are both provided,
        # ensure expected_delivery_date is not before order_date
        if self.order_date and self.expected_delivery_date:
            if self.expected_delivery_date < self.order_date:
                raise ValidationError({
                    "expected_delivery_date": _("Expected delivery date cannot be before the order date.")
                })
                
        # If order_date and actual_delivery_date are both provided,
        # ensure actual_delivery_date is not before order_date
        if self.order_date and self.actual_delivery_date:
            if self.actual_delivery_date < self.order_date:
                raise ValidationError({
                    "actual_delivery_date": _("Actual delivery date cannot be before the order date.")
                })
                
        # If status is 'received', actual_delivery_date is required
        if self.status == 'received' and not self.actual_delivery_date:
            raise ValidationError({
                "actual_delivery_date": _("Actual delivery date is required when status is 'received'.")
            })


class OrderItem(BaseModel):
    """
    OrderItem model for individual items in an order.
    """
    
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name=_("Order")
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="order_items",
        verbose_name=_("Product")
    )
    quantity = models.DecimalField(
        _("Quantity"),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    unit_price = models.DecimalField(
        _("Unit Price"),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0), currency_validator()]
    )
    received_quantity = models.DecimalField(
        _("Received Quantity"),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        default=0
    )
    notes = models.TextField(_("Notes"), blank=True)
    
    class Meta:
        verbose_name = _("Order Item")
        verbose_name_plural = _("Order Items")
        ordering = ["product__name"]
        unique_together = [["order", "product"]]
    
    def __str__(self):
        """Return order item information."""
        return f"{self.product.name} ({self.quantity}) - Order #{self.order.order_number}"
    
    @property
    def total_price(self):
        """Calculate the total price for this item."""
        return self.quantity * self.unit_price
    
    @property
    def is_fully_received(self):
        """Check if the item has been fully received."""
        return self.received_quantity >= self.quantity
    
    @property
    def receiving_status(self):
        """Return the receiving status of the item."""
        if self.received_quantity == 0:
            return _("Not Received")
        elif self.is_fully_received:
            return _("Fully Received")
        else:
            return _("Partially Received") 