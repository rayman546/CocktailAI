"""
Tests for the inventory app API endpoints.
"""
from django.urls import reverse
from rest_framework import status
from inventory.models import Category, Supplier, Location
from core.tests.test_base import BaseAPITestCase


class CategoryAPITests(BaseAPITestCase):
    """Tests for the Category API endpoints."""
    
    def setUp(self):
        """Set up for test case."""
        super().setUp()
        self.category_list_url = reverse('api:category-list')
        # Get the ID of the first category from fixtures
        self.category = Category.objects.first()
        self.category_detail_url = reverse('api:category-detail', args=[self.category.id])
    
    def test_list_categories_as_authenticated_user(self):
        """Test that any authenticated user can list categories."""
        self.authenticate_as_regular_user()
        
        response = self.client.get(self.category_list_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should have at least 10 categories from fixtures
        self.assertGreaterEqual(len(response.data['results']), 10)
    
    def test_list_categories_as_unauthenticated_user(self):
        """Test that unauthenticated users cannot list categories."""
        response = self.client.get(self.category_list_url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_retrieve_category_as_authenticated_user(self):
        """Test that any authenticated user can retrieve a category."""
        self.authenticate_as_regular_user()
        
        response = self.client.get(self.category_detail_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.category.name)
    
    def test_create_category_as_staff(self):
        """Test that staff users can create categories."""
        self.authenticate_as_admin()
        
        payload = {
            'name': 'New Test Category',
            'description': 'A new test category created via API',
        }
        
        response = self.client.post(self.category_list_url, payload)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], payload['name'])
        self.assertEqual(response.data['description'], payload['description'])
        
        # Verify category was created in database
        self.assertTrue(Category.objects.filter(name=payload['name']).exists())
    
    def test_create_category_as_regular_user(self):
        """Test that regular users cannot create categories."""
        self.authenticate_as_regular_user()
        
        payload = {
            'name': 'Should Not Create',
            'description': 'This should not be created',
        }
        
        response = self.client.post(self.category_list_url, payload)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Verify category was not created
        self.assertFalse(Category.objects.filter(name=payload['name']).exists())
    
    def test_update_category_as_staff(self):
        """Test that staff users can update categories."""
        self.authenticate_as_admin()
        
        payload = {
            'description': 'Updated description',
        }
        
        response = self.client.patch(self.category_detail_url, payload)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['description'], payload['description'])
        
        # Verify category was updated in database
        self.category.refresh_from_db()
        self.assertEqual(self.category.description, payload['description'])
    
    def test_update_category_as_regular_user(self):
        """Test that regular users cannot update categories."""
        self.authenticate_as_regular_user()
        
        original_description = self.category.description
        
        payload = {
            'description': 'Should not update',
        }
        
        response = self.client.patch(self.category_detail_url, payload)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Verify category was not updated
        self.category.refresh_from_db()
        self.assertEqual(self.category.description, original_description)
    
    def test_delete_category_as_staff(self):
        """Test that staff users can delete categories."""
        self.authenticate_as_admin()
        
        # Create a category to delete
        category_to_delete = Category.objects.create(
            name='Category To Delete',
            description='This category will be deleted'
        )
        
        url = reverse('api:category-detail', args=[category_to_delete.id])
        
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verify category was deleted (or marked inactive)
        category_to_delete.refresh_from_db()
        self.assertFalse(category_to_delete.is_active)
    
    def test_delete_category_as_regular_user(self):
        """Test that regular users cannot delete categories."""
        self.authenticate_as_regular_user()
        
        response = self.client.delete(self.category_detail_url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Verify category still exists and is active
        self.category.refresh_from_db()
        self.assertTrue(self.category.is_active)


class SupplierAPITests(BaseAPITestCase):
    """Tests for the Supplier API endpoints."""
    
    def setUp(self):
        """Set up for test case."""
        super().setUp()
        self.supplier_list_url = reverse('api:supplier-list')
        # Get the ID of the first supplier from fixtures
        self.supplier = Supplier.objects.first()
        self.supplier_detail_url = reverse('api:supplier-detail', args=[self.supplier.id])
    
    def test_list_suppliers_as_authenticated_user(self):
        """Test that any authenticated user can list suppliers."""
        self.authenticate_as_regular_user()
        
        response = self.client.get(self.supplier_list_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should have 5 suppliers from fixtures
        self.assertEqual(len(response.data['results']), 5)
    
    def test_retrieve_supplier_as_authenticated_user(self):
        """Test that any authenticated user can retrieve a supplier."""
        self.authenticate_as_regular_user()
        
        response = self.client.get(self.supplier_detail_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.supplier.name)
    
    def test_create_supplier_as_staff(self):
        """Test that staff users can create suppliers."""
        self.authenticate_as_admin()
        
        payload = {
            'name': 'New Test Supplier',
            'contact_name': 'Test Contact',
            'email': 'contact@testsupplier.com',
            'phone': '555-987-6543',
        }
        
        response = self.client.post(self.supplier_list_url, payload)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], payload['name'])
        self.assertEqual(response.data['contact_name'], payload['contact_name'])
        
        # Verify supplier was created in database
        self.assertTrue(Supplier.objects.filter(name=payload['name']).exists())
    
    def test_create_supplier_as_regular_user(self):
        """Test that regular users cannot create suppliers."""
        self.authenticate_as_regular_user()
        
        payload = {
            'name': 'Should Not Create',
            'contact_name': 'No Create',
            'email': 'nocreate@example.com',
        }
        
        response = self.client.post(self.supplier_list_url, payload)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Verify supplier was not created
        self.assertFalse(Supplier.objects.filter(name=payload['name']).exists())


class LocationAPITests(BaseAPITestCase):
    """Tests for the Location API endpoints."""
    
    def setUp(self):
        """Set up for test case."""
        super().setUp()
        self.location_list_url = reverse('api:location-list')
        # Get the ID of the first location from fixtures
        self.location = Location.objects.first()
        self.location_detail_url = reverse('api:location-detail', args=[self.location.id])
    
    def test_list_locations_as_authenticated_user(self):
        """Test that any authenticated user can list locations."""
        self.authenticate_as_regular_user()
        
        response = self.client.get(self.location_list_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should have 6 locations from fixtures
        self.assertEqual(len(response.data['results']), 6)
    
    def test_retrieve_location_as_authenticated_user(self):
        """Test that any authenticated user can retrieve a location."""
        self.authenticate_as_regular_user()
        
        response = self.client.get(self.location_detail_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.location.name)
    
    def test_create_location_as_staff(self):
        """Test that staff users can create locations."""
        self.authenticate_as_admin()
        
        payload = {
            'name': 'New Test Location',
            'description': 'A new test location created via API',
            'is_storage': True,
            'is_service': False,
        }
        
        response = self.client.post(self.location_list_url, payload)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], payload['name'])
        self.assertEqual(response.data['description'], payload['description'])
        self.assertEqual(response.data['is_storage'], payload['is_storage'])
        self.assertEqual(response.data['is_service'], payload['is_service'])
        
        # Verify location was created in database
        self.assertTrue(Location.objects.filter(name=payload['name']).exists())
    
    def test_filter_locations_by_type(self):
        """Test filtering locations by type (storage/service)."""
        self.authenticate_as_regular_user()
        
        # Get only storage locations
        response = self.client.get(f"{self.location_list_url}?is_storage=true")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # All locations in response should have is_storage=True
        for location in response.data['results']:
            self.assertTrue(location['is_storage'])
        
        # Get only service locations
        response = self.client.get(f"{self.location_list_url}?is_service=true")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # All locations in response should have is_service=True
        for location in response.data['results']:
            self.assertTrue(location['is_service'])
    
    def test_search_locations(self):
        """Test searching locations by name."""
        self.authenticate_as_regular_user()
        
        # Create a location with a unique name for search
        Location.objects.create(
            name="UniqueSearchableName",
            description="A location with a unique name to search for"
        )
        
        response = self.client.get(f"{self.location_list_url}?search=UniqueSearchableName")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], "UniqueSearchableName") 