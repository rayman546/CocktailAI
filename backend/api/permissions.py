"""
Custom permission classes for the CocktailAI API.
"""

from rest_framework import permissions


class IsStaffOrReadOnly(permissions.BasePermission):
    """
    Permission to allow only staff members to modify objects.
    Non-authenticated users have no access.
    Authenticated non-staff users have read-only access.
    """
    
    def has_permission(self, request, view):
        # Authenticate the user
        if not request.user or not request.user.is_authenticated:
            return False
            
        # Allow GET, HEAD, OPTIONS requests for authenticated users
        if request.method in permissions.SAFE_METHODS:
            return True
            
        # Allow write operations only for staff
        return request.user.is_staff


class IsOwnerOrStaffOrReadOnly(permissions.BasePermission):
    """
    Permission to allow owners or staff to modify objects.
    Non-authenticated users have no access.
    Authenticated non-owner, non-staff users have read-only access.
    
    Standardized to check created_by field for ownership.
    """
    
    def has_permission(self, request, view):
        # Authenticate the user
        if not request.user or not request.user.is_authenticated:
            return False
            
        # Allow GET, HEAD, OPTIONS requests for authenticated users
        if request.method in permissions.SAFE_METHODS:
            return True
            
        # Create operations pass to has_object_permission
        if view.action == 'create':
            return True
            
        # Update/Delete pass to has_object_permission
        return True
    
    def has_object_permission(self, request, view, obj):
        # Allow GET, HEAD, OPTIONS requests for authenticated users
        if request.method in permissions.SAFE_METHODS:
            return True
            
        # Staff can do anything
        if request.user.is_staff:
            return True
            
        # Standardized ownership check - prioritize created_by
        if hasattr(obj, 'created_by'):
            return obj.created_by == request.user
        # Fallback to other ownership fields if created_by doesn't exist
        elif hasattr(obj, 'performed_by'):
            return obj.performed_by == request.user
        elif hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'owner'):
            return obj.owner == request.user
            
        # If no ownership field found, deny permission
        return False


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Permission to allow only admin users to modify sensitive objects.
    Non-authenticated users have no access.
    Non-admin authenticated users have read-only access.
    """
    
    def has_permission(self, request, view):
        # Authenticate the user
        if not request.user or not request.user.is_authenticated:
            return False
            
        # Allow GET, HEAD, OPTIONS requests for authenticated users
        if request.method in permissions.SAFE_METHODS:
            return True
            
        # Allow write operations only for admin
        return request.user.is_superuser


class IsOwnerOrStaff(permissions.BasePermission):
    """
    Permission to allow only owners or staff access.
    Objects are completely restricted from non-owners or non-staff.
    
    Standardized to check created_by field for ownership.
    """
    
    def has_permission(self, request, view):
        # Authenticate the user
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Staff can do anything
        if request.user.is_staff:
            return True
            
        # Standardized ownership check - prioritize created_by
        if hasattr(obj, 'created_by'):
            return obj.created_by == request.user
        # Fallback to other ownership fields if created_by doesn't exist
        elif hasattr(obj, 'performed_by'):
            return obj.performed_by == request.user
        elif hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'owner'):
            return obj.owner == request.user
            
        # If no ownership field found, deny permission
        return False


class IsInventoryCountParticipant(permissions.BasePermission):
    """
    Permission for inventory count participants.
    
    Allows:
    - Staff to do anything
    - Created_by user to do anything
    - Completed_by user to update only when status is in_progress
    - Others with read-only access if authenticated
    """
    
    def has_permission(self, request, view):
        # Authenticate the user
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Allow GET, HEAD, OPTIONS requests for authenticated users
        if request.method in permissions.SAFE_METHODS:
            return True
            
        # Staff can do anything
        if request.user.is_staff:
            return True
            
        # Creator can do anything
        if obj.created_by == request.user:
            return True
            
        # Assigned counter can only update when in progress
        if obj.completed_by == request.user and obj.status == 'in_progress':
            if request.method in ['PUT', 'PATCH']:
                return True
                
        return False


class IsOrderParticipant(permissions.BasePermission):
    """
    Permission for order participants.
    
    Allows:
    - Staff to do anything
    - Created_by user to do anything
    - Updated_by user to update only when status is not cancelled
    - Others with read-only access if authenticated
    """
    
    def has_permission(self, request, view):
        # Authenticate the user
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Allow GET, HEAD, OPTIONS requests for authenticated users
        if request.method in permissions.SAFE_METHODS:
            return True
            
        # Staff can do anything
        if request.user.is_staff:
            return True
            
        # Creator can do anything
        if obj.created_by == request.user:
            return True
            
        # Assigned updater can only modify when not cancelled
        if obj.updated_by == request.user and obj.status != 'cancelled':
            if request.method in ['PUT', 'PATCH']:
                return True
                
        return False


class IsAuthenticatedForMethods(permissions.BasePermission):
    """
    Permission to allow only authenticated users for specific HTTP methods,
    and public access for others.
    """
    
    def __init__(self, authenticated_methods=None):
        self.authenticated_methods = authenticated_methods or ['POST', 'PUT', 'PATCH', 'DELETE']
    
    def has_permission(self, request, view):
        # Allow any access for non-authenticated methods
        if request.method not in self.authenticated_methods:
            return True
            
        # Require authentication for authenticated methods
        return request.user and request.user.is_authenticated 