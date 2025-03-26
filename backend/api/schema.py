"""
Schema utilities for the CocktailAI API documentation.
"""

from drf_spectacular.utils import (
    extend_schema, extend_schema_view, 
    OpenApiParameter, OpenApiExample, 
    OpenApiResponse, inline_serializer,
    extend_schema_field, extend_schema_serializer,
    OpenApiTypes
)
from drf_spectacular.types import OpenApiTypes
from rest_framework import serializers
from typing import Dict, List, Any, Optional, Union


def common_schema_parameters() -> List[OpenApiParameter]:
    """
    Common query parameters used across multiple endpoints.
    """
    return [
        OpenApiParameter(
            name="page",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description="Page number for pagination",
            required=False,
        ),
        OpenApiParameter(
            name="page_size",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description="Number of results per page",
            required=False,
        ),
        OpenApiParameter(
            name="ordering",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Order by field (prefix with '-' for descending order)",
            required=False,
        ),
        OpenApiParameter(
            name="search",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Search term for text-based search",
            required=False,
        ),
    ]


def error_responses() -> Dict[str, OpenApiResponse]:
    """
    Common error responses used across multiple endpoints.
    """
    return {
        "400": OpenApiResponse(
            description="Bad Request - Invalid input",
            response=inline_serializer(
                name="ErrorResponse400",
                fields={
                    "error": serializers.DictField(
                        child=serializers.CharField(),
                        help_text="Error details",
                    ),
                },
            ),
        ),
        "401": OpenApiResponse(
            description="Unauthorized - Authentication credentials were not provided or are invalid",
            response=inline_serializer(
                name="ErrorResponse401",
                fields={
                    "detail": serializers.CharField(
                        help_text="Authentication credentials were not provided."
                    ),
                },
            ),
        ),
        "403": OpenApiResponse(
            description="Forbidden - You do not have permission to perform this action",
            response=inline_serializer(
                name="ErrorResponse403",
                fields={
                    "detail": serializers.CharField(
                        help_text="You do not have permission to perform this action."
                    ),
                },
            ),
        ),
        "404": OpenApiResponse(
            description="Not Found - The requested resource was not found",
            response=inline_serializer(
                name="ErrorResponse404",
                fields={
                    "detail": serializers.CharField(
                        help_text="Not found."
                    ),
                },
            ),
        ),
    }


def extend_schema_with_auth(
    *,
    summary: str,
    description: Optional[str] = None,
    tags: Optional[List[str]] = None,
    responses: Optional[Dict[str, Any]] = None,
    operation_id: Optional[str] = None,
    **kwargs
):
    """
    Extended schema decorator that includes authentication and common error responses.
    
    Args:
        summary: A short summary of the operation
        description: A verbose description of the operation
        tags: A list of tags for API documentation control
        responses: Response documentation
        operation_id: A unique identifier for the operation
        **kwargs: Additional keyword arguments passed to extend_schema
    """
    # Ensure we have responses dict
    if responses is None:
        responses = {}
    
    # Add common error responses
    for status_code, response in error_responses().items():
        if status_code not in responses:
            responses[status_code] = response
    
    # Return decorated function
    return extend_schema(
        summary=summary,
        description=description,
        tags=tags,
        responses=responses,
        operation_id=operation_id,
        **kwargs
    )


def inventory_parameters() -> List[OpenApiParameter]:
    """
    Common query parameters for inventory-related endpoints.
    """
    common_params = common_schema_parameters()
    inventory_params = [
        OpenApiParameter(
            name="is_active",
            type=OpenApiTypes.BOOL,
            location=OpenApiParameter.QUERY,
            description="Filter by active status",
            required=False,
        ),
        OpenApiParameter(
            name="created_after",
            type=OpenApiTypes.DATE,
            location=OpenApiParameter.QUERY,
            description="Filter by creation date (after specified date)",
            required=False,
        ),
        OpenApiParameter(
            name="created_before",
            type=OpenApiTypes.DATE,
            location=OpenApiParameter.QUERY,
            description="Filter by creation date (before specified date)",
            required=False,
        ),
    ]
    return common_params + inventory_params


def product_parameters() -> List[OpenApiParameter]:
    """
    Query parameters for product-related endpoints.
    """
    inventory_params = inventory_parameters()
    product_params = [
        OpenApiParameter(
            name="category",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description="Filter by category ID",
            required=False,
        ),
        OpenApiParameter(
            name="supplier",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description="Filter by supplier ID",
            required=False,
        ),
        OpenApiParameter(
            name="min_price",
            type=OpenApiTypes.NUMBER,
            location=OpenApiParameter.QUERY,
            description="Filter by minimum unit price",
            required=False,
        ),
        OpenApiParameter(
            name="max_price",
            type=OpenApiTypes.NUMBER,
            location=OpenApiParameter.QUERY,
            description="Filter by maximum unit price",
            required=False,
        ),
        OpenApiParameter(
            name="unit_type",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Filter by unit type (e.g., oz, ml, each)",
            required=False,
        ),
    ]
    return inventory_params + product_params


def inventory_item_parameters() -> List[OpenApiParameter]:
    """
    Query parameters for inventory item-related endpoints.
    """
    inventory_params = inventory_parameters()
    inventory_item_params = [
        OpenApiParameter(
            name="product",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description="Filter by product ID",
            required=False,
        ),
        OpenApiParameter(
            name="location",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description="Filter by location ID",
            required=False,
        ),
        OpenApiParameter(
            name="min_quantity",
            type=OpenApiTypes.NUMBER,
            location=OpenApiParameter.QUERY,
            description="Filter by minimum quantity",
            required=False,
        ),
        OpenApiParameter(
            name="max_quantity",
            type=OpenApiTypes.NUMBER,
            location=OpenApiParameter.QUERY,
            description="Filter by maximum quantity",
            required=False,
        ),
    ]
    return inventory_params + inventory_item_params


def transaction_parameters() -> List[OpenApiParameter]:
    """
    Query parameters for transaction-related endpoints.
    """
    inventory_params = inventory_parameters()
    transaction_params = [
        OpenApiParameter(
            name="product",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description="Filter by product ID",
            required=False,
        ),
        OpenApiParameter(
            name="location",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description="Filter by location ID",
            required=False,
        ),
        OpenApiParameter(
            name="transaction_type",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Filter by transaction type (received, sold, transferred, adjustment)",
            required=False,
        ),
        OpenApiParameter(
            name="performed_by",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description="Filter by user who performed the transaction",
            required=False,
        ),
    ]
    return inventory_params + transaction_params


def order_parameters() -> List[OpenApiParameter]:
    """
    Query parameters for order-related endpoints.
    """
    inventory_params = inventory_parameters()
    order_params = [
        OpenApiParameter(
            name="supplier",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description="Filter by supplier ID",
            required=False,
        ),
        OpenApiParameter(
            name="status",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Filter by order status (draft, pending, placed, received, cancelled)",
            required=False,
        ),
        OpenApiParameter(
            name="created_by",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description="Filter by user who created the order",
            required=False,
        ),
        OpenApiParameter(
            name="order_date_after",
            type=OpenApiTypes.DATE,
            location=OpenApiParameter.QUERY,
            description="Filter by order date (after specified date)",
            required=False,
        ),
        OpenApiParameter(
            name="order_date_before",
            type=OpenApiTypes.DATE,
            location=OpenApiParameter.QUERY,
            description="Filter by order date (before specified date)",
            required=False,
        ),
    ]
    return inventory_params + order_params 