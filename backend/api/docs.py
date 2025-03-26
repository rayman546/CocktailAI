"""
Documentation module for the CocktailAI API.

This module contains documentation about API features, including filtering, sorting, and pagination.
These docs are designed to be included in the Swagger/OpenAPI documentation.
"""

from drf_spectacular.utils import extend_schema_field, extend_schema_serializer, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from rest_framework import serializers

# Field Validation Documentation

VALIDATION_DOCS = """
# Field Validation

The CocktailAI API implements robust field validation to ensure data integrity.
This document outlines the validation rules applied to different field types.

## Date Validation

### No Future Dates

Many date fields cannot accept dates in the future:

- `order_date` in Order
- `actual_delivery_date` in Order
- `completed_date` in InventoryCount
- `counted_at` in InventoryCountItem
- `transaction_date` in InventoryTransaction

Example error response:
```json
{
  "order_date": ["2024-12-31 is in the future. This field cannot accept future dates."]
}
```

### Date Sequence Validation

Date fields that represent a sequence of events are validated to ensure logical order:

- In Order model: `expected_delivery_date` and `actual_delivery_date` cannot be before `order_date`
- In InventoryCount model: `scheduled_date` cannot be after `completed_date`

Example error response:
```json
{
  "expected_delivery_date": ["Expected delivery date cannot be before the order date."]
}
```

## Contact Information Validation

### Email Validation

Email fields are validated for proper format:

- `email` in Supplier model
- `email` in User model

Example error response:
```json
{
  "email": ["invalid-email is not a valid email address."]
}
```

### Phone Number Validation

Phone numbers are validated for proper format and length:

- `phone` in Supplier model
- `phone_number` in User model

Format accepts international codes, parentheses, spaces, and hyphens. Must have between 7-15 digits.

Example error response:
```json
{
  "phone": ["12345 is not a valid phone number. Must have between 7 and 15 digits."]
}
```

## Numeric Value Validation

### Currency/Price Validation

All price and currency fields must be non-negative:

- `unit_price` in Product model
- `shipping_cost`, `tax`, `discount` in Order model
- `unit_price` in OrderItem model

Example error response:
```json
{
  "unit_price": ["Value cannot be less than 0."]
}
```

### Quantity Validation

Quantity fields have specific validation rules:

- Most quantity fields must be non-negative
- For InventoryTransaction, the sign depends on transaction_type:
  - Positive for 'received' transactions
  - Negative for 'sold' and 'transferred' transactions

Example error response:
```json
{
  "quantity": ["Quantity must be negative for sold transactions."]
}
```

## Transaction-Specific Validation

InventoryTransaction model has specialized validation:

- For 'transferred' transactions, destination_location is required
- destination_location must be different from source location
- Quantity sign must match transaction type (positive/negative)

Example error response:
```json
{
  "destination_location": ["Destination location is required for transfers."]
}
```
"""

# Filtering Documentation

FILTERING_DOCS = """
# Filtering

The CocktailAI API supports advanced filtering capabilities across all endpoints. 
Filters can be applied as query parameters to narrow down results.

## Basic Filtering

Basic filtering can be done by providing exact match parameters:

```
/api/products/?category=1&is_active=true
```

## Advanced Filtering

Many endpoints support advanced filtering options:

### Range Filters

Range filters allow filtering by numeric ranges:

```
/api/products/?min_price=10&max_price=50
/api/inventory-items/?min_quantity=5&max_quantity=100
```

### Date Filters

Date filters allow filtering by date ranges:

```
/api/orders/?created_after=2023-01-01&created_before=2023-12-31
/api/inventory-transactions/?created_after=2023-01-01T00:00:00Z
```

### Text Search

A global text search is available on all endpoints using the `search` parameter:

```
/api/products/?search=vodka
/api/suppliers/?search=acme
```

This performs a case-insensitive search across multiple relevant fields.

### Relationship Filters

You can filter by related object fields:

```
/api/products/?category_name=spirits
/api/inventory-items/?product_name=vodka
```

### Boolean Filters

Some endpoints support boolean filters for special conditions:

```
/api/categories/?has_products=true
/api/suppliers/?has_orders=false
```

## Operators

The following operators are supported for field lookups:

- Exact match: `field=value`
- Contains (case-insensitive): `field__icontains=value`
- Greater than or equal: `field__gte=value`
- Less than or equal: `field__lte=value`
- In list: `field__in=value1,value2,value3`
- Is null: `field__isnull=true`

Example:

```
/api/products/?name__icontains=vodka&unit_price__gte=20
```
"""

# Sorting Documentation

SORTING_DOCS = """
# Sorting

All list endpoints support sorting through the `ordering` parameter.

## Basic Sorting

To sort by a field in ascending order:

```
/api/products/?ordering=name
```

## Reverse Sorting

To sort in descending order, prefix the field with a dash (`-`):

```
/api/products/?ordering=-created_at
```

## Multiple Sort Fields

You can sort by multiple fields by separating them with commas:

```
/api/products/?ordering=category__name,-unit_price
```

This sorts by category name (ascending), then by unit price (descending).

## Available Sort Fields

Each endpoint defines which fields can be used for sorting via the `ordering_fields` parameter.
Common sortable fields include:

- `name`: Sort by name
- `created_at`: Sort by creation date
- `updated_at`: Sort by last update date
- `price`/`unit_price`: Sort by price (where applicable)
- `quantity`: Sort by quantity (where applicable)

Additional fields may be available for specific endpoints.
"""

# Pagination Documentation

PAGINATION_DOCS = """
# Pagination

All list endpoints in the CocktailAI API are paginated by default.

## Default Pagination

By default, endpoints return 20 items per page.

## Page-Based Pagination

The API uses page-based pagination with the following query parameters:

- `page`: The page number (1-based indexing)
- `page_size`: Number of items per page (max 100)

Example:

```
/api/products/?page=2&page_size=50
```

## Pagination Response Format

Paginated responses include the following metadata:

```json
{
  "count": 100,           // Total number of items
  "next": "http://...",   // URL to the next page (null if none)
  "previous": "http://...", // URL to the previous page (null if none)
  "results": [...]        // Array of items for the current page
}
```

## Nested Endpoints

Nested resource endpoints (accessed via detail actions) use a smaller pagination
size of 10 items per page by default.

Examples of nested endpoints:

```
/api/products/{id}/inventory/
/api/categories/{id}/products/
/api/locations/{id}/inventory/
```
"""

# Combined API Features Documentation

API_FEATURES_DOCS = f"""
# API Features

The CocktailAI API provides a rich set of features for interacting with the data.

{FILTERING_DOCS}

{SORTING_DOCS}

{PAGINATION_DOCS}

{VALIDATION_DOCS}
"""

# Schema extensions for documentation

def get_api_features_example():
    """
    Get an example of API features for the OpenAPI schema.
    """
    return OpenApiExample(
        name="api-features",
        summary="API Features Documentation",
        description=API_FEATURES_DOCS,
        value={"message": "See description for full API features documentation"}
    )

def get_filtering_example():
    """
    Get an example of filtering capabilities for the OpenAPI schema.
    """
    return OpenApiExample(
        name="filtering",
        summary="Filtering Documentation",
        description=FILTERING_DOCS,
        value={"message": "See description for full filtering documentation"}
    )

def get_sorting_example():
    """
    Get an example of sorting capabilities for the OpenAPI schema.
    """
    return OpenApiExample(
        name="sorting",
        summary="Sorting Documentation",
        description=SORTING_DOCS,
        value={"message": "See description for full sorting documentation"}
    )

def get_pagination_example():
    """
    Get an example of pagination capabilities for the OpenAPI schema.
    """
    return OpenApiExample(
        name="pagination",
        summary="Pagination Documentation",
        description=PAGINATION_DOCS,
        value={"message": "See description for full pagination documentation"}
    )

def get_validation_example():
    """
    Get an example of field validation rules for the OpenAPI schema.
    """
    return OpenApiExample(
        name="validation",
        summary="Field Validation Documentation",
        description=VALIDATION_DOCS,
        value={"message": "See description for full validation documentation"}
    ) 