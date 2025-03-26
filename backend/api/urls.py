"""
API URLs for the CocktailAI project.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView
from drf_spectacular.utils import extend_schema

# Import viewsets
from .views import (
    UserViewSet, UserPreferencesViewSet, CategoryViewSet, 
    SupplierViewSet, LocationViewSet, ProductViewSet,
    InventoryItemViewSet, InventoryTransactionViewSet,
    InventoryCountViewSet, OrderViewSet,
    UserPreferencesAPIView,
    InventoryCountItemAPIView,
    APIDocs
)

# Create a router and register viewsets
router = DefaultRouter()

# User management
router.register('users', UserViewSet)
router.register('user-preferences', UserPreferencesViewSet)

# Inventory base models
router.register('categories', CategoryViewSet)
router.register('suppliers', SupplierViewSet)
router.register('locations', LocationViewSet)

# Products and inventory
router.register('products', ProductViewSet)
router.register('inventory-items', InventoryItemViewSet)
router.register('inventory-transactions', InventoryTransactionViewSet)

# Inventory counts
router.register('inventory-counts', InventoryCountViewSet)

# Orders
router.register('orders', OrderViewSet)

# JWT token views with better OpenAPI documentation
token_obtain_pair = extend_schema(
    summary="Obtain JWT token",
    description="Obtain a JSON Web Token for authentication by providing username and password.",
    tags=["Authentication"]
)(TokenObtainPairView.as_view())

token_refresh = extend_schema(
    summary="Refresh JWT token",
    description="Refresh an expired JSON Web Token to get a new access token.",
    tags=["Authentication"]
)(TokenRefreshView.as_view())

token_verify = extend_schema(
    summary="Verify JWT token",
    description="Verify that a JSON Web Token is valid.",
    tags=["Authentication"]
)(TokenVerifyView.as_view())

urlpatterns = [
    # Authentication endpoints
    path('token/', token_obtain_pair, name='token_obtain_pair'),
    path('token/refresh/', token_refresh, name='token_refresh'),
    path('token/verify/', token_verify, name='token_verify'),
    
    # User preferences
    path('users/<int:user_id>/preferences/', UserPreferencesAPIView.as_view(), name='user-preferences'),
    
    # Inventory count items
    path('inventory-counts/<int:count_id>/items/', InventoryCountItemAPIView.as_view(), name='inventory-count-items'),
    path('inventory-counts/<int:count_id>/items/<int:pk>/', InventoryCountItemAPIView.as_view(), name='inventory-count-item-detail'),
    
    # Documentation endpoints
    path('docs/features/', APIDocs.as_view({'get': 'features'}), name='api-features-docs'),
    path('docs/filtering/', APIDocs.as_view({'get': 'filtering'}), name='api-filtering-docs'),
    path('docs/sorting/', APIDocs.as_view({'get': 'sorting'}), name='api-sorting-docs'),
    path('docs/pagination/', APIDocs.as_view({'get': 'pagination'}), name='api-pagination-docs'),
    
    # Include router URLs
    path('', include(router.urls)),
] 