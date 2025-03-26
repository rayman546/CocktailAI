"""
Utility functions for the CocktailAI API.
"""

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from collections import OrderedDict


class StandardResultsSetPagination(PageNumberPagination):
    """
    Standard pagination for the API.
    """
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class SmallResultsSetPagination(PageNumberPagination):
    """
    Smaller pagination for nested resources.
    """
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50


def paginate_queryset(queryset, request, serializer_class):
    """
    Paginate a queryset and return a standardized response.
    
    Args:
        queryset: The queryset to paginate
        request: The request object
        serializer_class: The serializer class to use
        
    Returns:
        A paginated response with standardized format
    """
    paginator = SmallResultsSetPagination()
    page = paginator.paginate_queryset(queryset, request)
    
    if page is not None:
        serializer = serializer_class(page, many=True)
        return paginator.get_paginated_response(serializer.data)
    
    # If pagination is not needed
    serializer = serializer_class(queryset, many=True)
    return Response(serializer.data)


def create_error_response(message, code=None, status=400):
    """
    Create a standardized error response.
    
    Args:
        message: Error message
        code: Error code
        status: HTTP status code
        
    Returns:
        Response with standardized error format
    """
    error_data = {
        'error': {
            'message': message,
        }
    }
    
    if code:
        error_data['error']['code'] = code
        
    return Response(error_data, status=status)


def filter_queryset_by_user(queryset, user, ownership_field='created_by'):
    """
    Filter a queryset based on user permissions.
    
    Args:
        queryset: The queryset to filter
        user: The user making the request
        ownership_field: The field to check for ownership
        
    Returns:
        Filtered queryset
    """
    # Staff can see all
    if user.is_staff:
        return queryset
    
    # Regular users can only see their own
    filter_kwargs = {ownership_field: user}
    return queryset.filter(**filter_kwargs) 