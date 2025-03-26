"""
Tests for the inventory app models.
"""
from django.test import TestCase
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from inventory.models import Category, Supplier, Location, Product
from core.tests.test_base import BaseTestCase


class CategoryModelTests(BaseTestCase):
    """Tests for the Category model."""
    
    def test_create_category(self):
        """Test creating a new category."""
        category = Category.objects.create(
            name="Test Category",
            description="A test category for inventory items",
        )
        
        self.assertEqual(category.name, "Test Category")
        self.assertEqual(category.description, "A test category for inventory items")
        self.assertTrue(category.is_active)
        self.assertIsNone(category.parent)
    
    def test_create_subcategory(self):
        """Test creating a subcategory with a parent category."""
        parent_category = Category.objects.create(
            name="Parent Category",
            description="A parent category",
        )
        
        subcategory = Category.objects.create(
            name="Subcategory",
            description="A subcategory",
            parent=parent_category
        )
        
        self.assertEqual(subcategory.parent, parent_category)
        self.assertEqual(subcategory.name, "Subcategory")
    
    def test_category_string_representation(self):
        """Test the string representation of a category."""
        category = Category.objects.create(
            name="String Test Category",
        )
        
        self.assertEqual(str(category), "String Test Category")
    
    def test_subcategory_string_representation(self):
        """Test the string representation of a subcategory."""
        parent = Category.objects.create(name="Parent")
        subcategory = Category.objects.create(
            name="Child",
            parent=parent
        )
        
        self.assertEqual(str(subcategory), "Parent > Child")
    
    def test_category_unique_name(self):
        """Test that category names are unique."""
        Category.objects.create(name="Unique Category")
        
        with self.assertRaises(IntegrityError):
            Category.objects.create(name="Unique Category")
    
    def test_get_subcategories(self):
        """Test getting all subcategories of a category."""
        parent = Category.objects.create(name="Parent Category")
        child1 = Category.objects.create(name="Child 1", parent=parent)
        child2 = Category.objects.create(name="Child 2", parent=parent)
        
        subcategories = parent.subcategories.all()
        
        self.assertEqual(subcategories.count(), 2)
        self.assertIn(child1, subcategories)
        self.assertIn(child2, subcategories)


class SupplierModelTests(BaseTestCase):
    """Tests for the Supplier model."""
    
    def test_create_supplier(self):
        """Test creating a new supplier."""
        supplier = Supplier.objects.create(
            name="Test Supplier",
            contact_name="John Contact",
            email="contact@supplier.com",
            phone="555-123-4567",
            address="123 Supplier St, City, ST 12345",
            website="https://supplier.com",
            notes="This is a test supplier"
        )
        
        self.assertEqual(supplier.name, "Test Supplier")
        self.assertEqual(supplier.contact_name, "John Contact")
        self.assertEqual(supplier.email, "contact@supplier.com")
        self.assertEqual(supplier.phone, "555-123-4567")
        self.assertEqual(supplier.address, "123 Supplier St, City, ST 12345")
        self.assertEqual(supplier.website, "https://supplier.com")
        self.assertEqual(supplier.notes, "This is a test supplier")
        self.assertTrue(supplier.is_active)
    
    def test_supplier_required_fields(self):
        """Test that supplier name is required."""
        with self.assertRaises(IntegrityError):
            Supplier.objects.create(name=None)
    
    def test_supplier_string_representation(self):
        """Test the string representation of a supplier."""
        supplier = Supplier.objects.create(
            name="String Test Supplier",
        )
        
        self.assertEqual(str(supplier), "String Test Supplier")
    
    def test_supplier_unique_name(self):
        """Test that supplier names are unique."""
        Supplier.objects.create(name="Unique Supplier")
        
        with self.assertRaises(IntegrityError):
            Supplier.objects.create(name="Unique Supplier")
    
    def test_supplier_with_products(self):
        """Test supplier with associated products."""
        supplier = Supplier.objects.create(name="Product Supplier")
        category = Category.objects.create(name="Product Category")
        
        product1 = Product.objects.create(
            name="Product 1",
            sku="SKU-001",
            category=category,
            supplier=supplier,
            unit_price=10.99,
            unit_size=750,
            unit_type="bottle"
        )
        
        product2 = Product.objects.create(
            name="Product 2",
            sku="SKU-002",
            category=category,
            supplier=supplier,
            unit_price=15.99,
            unit_size=750,
            unit_type="bottle"
        )
        
        supplier_products = supplier.products.all()
        
        self.assertEqual(supplier_products.count(), 2)
        self.assertIn(product1, supplier_products)
        self.assertIn(product2, supplier_products)


class LocationModelTests(BaseTestCase):
    """Tests for the Location model."""
    
    def test_create_location(self):
        """Test creating a new location."""
        location = Location.objects.create(
            name="Test Location",
            description="A test location for inventory items",
            is_storage=True,
            is_service=False
        )
        
        self.assertEqual(location.name, "Test Location")
        self.assertEqual(location.description, "A test location for inventory items")
        self.assertTrue(location.is_storage)
        self.assertFalse(location.is_service)
        self.assertTrue(location.is_active)
    
    def test_location_string_representation(self):
        """Test the string representation of a location."""
        location = Location.objects.create(
            name="String Test Location",
        )
        
        self.assertEqual(str(location), "String Test Location")
    
    def test_location_unique_name(self):
        """Test that location names are unique."""
        Location.objects.create(name="Unique Location")
        
        with self.assertRaises(IntegrityError):
            Location.objects.create(name="Unique Location")
    
    def test_location_with_inventory_items(self):
        """Test location with associated inventory items."""
        location = Location.objects.create(name="Inventory Location")
        supplier = Supplier.objects.create(name="Product Supplier")
        category = Category.objects.create(name="Product Category")
        
        product = Product.objects.create(
            name="Test Product",
            sku="SKU-003",
            category=category,
            supplier=supplier,
            unit_price=12.99,
            unit_size=750,
            unit_type="bottle"
        )
        
        # Create inventory items associated with the location
        from inventory.models import InventoryItem
        
        item1 = InventoryItem.objects.create(
            product=product,
            location=location,
            quantity=10.0,
            status="in_stock"
        )
        
        item2 = InventoryItem.objects.create(
            product=product,
            location=location,
            quantity=5.0,
            status="allocated"
        )
        
        location_items = location.inventory_items.all()
        
        self.assertEqual(location_items.count(), 2)
        self.assertIn(item1, location_items)
        self.assertIn(item2, location_items)
    
    def test_location_total_inventory_value(self):
        """Test calculating the total inventory value for a location."""
        location = Location.objects.create(name="Value Test Location")
        supplier = Supplier.objects.create(name="Value Test Supplier")
        category = Category.objects.create(name="Value Test Category")
        
        product1 = Product.objects.create(
            name="Value Product 1",
            sku="VAL-001",
            category=category,
            supplier=supplier,
            unit_price=10.00,
            unit_size=750,
            unit_type="bottle"
        )
        
        product2 = Product.objects.create(
            name="Value Product 2",
            sku="VAL-002",
            category=category,
            supplier=supplier,
            unit_price=20.00,
            unit_size=750,
            unit_type="bottle"
        )
        
        from inventory.models import InventoryItem
        
        InventoryItem.objects.create(
            product=product1,
            location=location,
            quantity=5.0,
            status="in_stock"
        )
        
        InventoryItem.objects.create(
            product=product2,
            location=location,
            quantity=3.0,
            status="in_stock"
        )
        
        # Total value should be (5 * 10.00) + (3 * 20.00) = 50 + 60 = 110
        total_value = sum(item.total_value for item in location.inventory_items.all())
        
        self.assertEqual(total_value, 110.0) 