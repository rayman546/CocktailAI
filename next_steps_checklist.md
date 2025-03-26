# CocktailAI Next Steps Checklist

## Completed Tasks ✅

### Serializer Simplification
- [x] Examine the current InventoryItem serializers
- [x] Create base InventoryItemSerializer with core fields
- [x] Refactor InventoryItemListSerializer and InventoryItemDetailSerializer
- [x] Implement conditional field inclusion based on context
- [x] Update ViewSets to use consolidated serializer

### InventoryTransaction Serializer Updates
- [x] Update InventoryTransactionCreateSerializer to include destination_location field
- [x] Add validation for destination_location based on transaction type
- [x] Update related serializers that represent inventory transactions
- [x] Update ViewSets to use consolidated serializer

### Order Serializer Refactoring
- [x] Examine the current Order serializers
- [x] Create base OrderSerializer with core fields
- [x] Refactor OrderListSerializer and OrderDetailSerializer
- [x] Implement conditional field inclusion based on context
- [x] Update ViewSets to use consolidated serializer

### Model Field Validation
- [x] Add validation for date fields in Order model
- [x] Add validation for date fields in InventoryCount model
- [x] Create custom validators for date fields
- [x] Implement model-level validation through clean methods
- [x] Add transaction_date field with validator to InventoryTransaction model

## Remaining Tasks

### Migration Creation and Application
- [ ] Run migrations for inventory model changes:
  ```
  # Inside Docker container
  python manage.py makemigrations inventory
  python manage.py migrate
  ```

### Additional Field Validations
- [x] Review remaining fields for potential validation needs
- [x] Add validators for email fields
- [x] Add validators for phone number fields
- [x] Add validators for price/cost fields

## API Documentation

### DRF Spectacular Integration
- [x] Install and configure drf-spectacular if not already present
- [x] Configure basic settings for OpenAPI schema generation
- [x] Add schema_view to urls.py for Swagger UI and ReDoc

### Model and Endpoint Documentation
- [x] Add or update docstrings to all models with field descriptions
- [ ] Add or update docstrings to all viewsets with endpoint descriptions
- [ ] Add operation descriptions to viewset methods
- [ ] Document authentication requirements for each endpoint

### Examples and Schemas
- [x] Add OpenApiExample instances for common requests
- [x] Add OpenApiExample instances for responses
- [ ] Define custom OpenApiTypes where needed
- [x] Document possible error responses

### Custom Schema Improvements
- [x] Enhance the schema with validator information
- [x] Document the field validation rules
- [x] Add explanatory examples for the new validators 
- [x] Create documentation sections for common error cases

## Frontend Implementation Setup

### Project Initialization
- [ ] Set up React application with TypeScript and Vite
- [ ] Configure eslint and prettier
- [ ] Set up folder structure following project guidelines
- [ ] Install essential dependencies (React, React Router, Material UI, Redux Toolkit, React Query)

### Authentication Components
- [ ] Create Login component
- [ ] Create Signup component
- [ ] Create ForgotPassword component
- [ ] Implement JWT authentication handling

### Layout Components
- [ ] Create AppLayout component with responsive design
- [ ] Create Header component
- [ ] Create Sidebar/Navigation component
- [ ] Create Footer component

### Core Feature Components
- [ ] Create initial Dashboard view
- [ ] Set up routes and protected routes
- [ ] Create basic forms for main data models
- [ ] Design initial UI for inventory management 