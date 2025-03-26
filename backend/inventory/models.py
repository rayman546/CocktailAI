"""
Models for the inventory app.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.core.validators import MinValueValidator
import uuid


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
    """
    
    name = models.CharField(_("Name"), max_length=255)
    contact_name = models.CharField(_("Contact Name"), max_length=255, blank=True)
    email = models.EmailField(_("Email"), blank=True)
    phone = models.CharField(_("Phone"), max_length=20, blank=True)
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
        validators=[MinValueValidator(0)]
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
    quantity = models.DecimalField(
        _("Quantity"),
        max_digits=10,
        decimal_places=2
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
    completed_date = models.DateTimeField(_("Completed Date"), null=True, blank=True)
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
    counted_at = models.DateTimeField(_("Counted At"), null=True, blank=True)
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
    order_date = models.DateField(_("Order Date"), null=True, blank=True)
    expected_delivery_date = models.DateField(_("Expected Delivery Date"), null=True, blank=True)
    actual_delivery_date = models.DateField(_("Actual Delivery Date"), null=True, blank=True)
    shipping_cost = models.DecimalField(
        _("Shipping Cost"),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        default=0
    )
    tax = models.DecimalField(
        _("Tax"),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        default=0
    )
    discount = models.DecimalField(
        _("Discount"),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
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
        validators=[MinValueValidator(0)]
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