# CocktailAI Improvement Checklist

## Backend Improvements

### Permissions Refinement
- [x] Standardize ownership field to `created_by` across all models
- [x] Refactor `IsOwnerOrStaffOrReadOnly` and `IsOwnerOrStaff` permissions to check only created_by
- [x] Implement more granular object-level permissions for InventoryCount and Order
- [x] Update view permissions to use the new standardized permission classes

### API Endpoint Consolidation
- [x] Remove `UserPreferencesViewSet` (meant for admin use)
- [x] Enhance `UserViewSet.preferences` action to handle all preference operations
- [x] Update URL routing to reflect the consolidated API endpoints
- [ ] Update documentation to match the new API structure

### Serializer Simplification
- [x] Create a base `ProductSerializer` that other serializers can inherit from
- [x] Refactor `ProductListSerializer`, `ProductDetailSerializer`, and `ProductCreateUpdateSerializer` to use inheritance
- [ ] Apply the same pattern to simplify serializers for Order, InventoryItem, etc.
- [x] Implement conditional field inclusion based on context or action

### InventoryTransaction Validation
- [x] Modify `validate` method in `InventoryTransactionCreateSerializer` to raise `ValidationError` for invalid quantities
- [x] Add validation to prevent negative quantities for received items
- [x] Add validation for transferred items with proper source/destination logic

### Model Field Validation
- [x] Add `MinValueValidator` for quantity fields in InventoryItem
- [x] Add validation for quantity fields in InventoryTransaction
- [ ] Add date validators to prevent future dates for order_date, received_date, etc.
- [x] Implement database-level constraints for critical fields

### Signal Optimization
- [x] Refactor `update_inventory_on_transaction` signal to use atomic transactions
- [x] Consolidate logic for positive and negative transactions
- [x] Implement proper transfer logic within the signal
- [x] Ensure all edge cases are handled correctly

### Comprehensive Documentation
- [ ] Expand API documentation using drf-spectacular
- [ ] Add detailed descriptions and examples for request/response payloads
- [ ] Document model fields thoroughly
- [ ] Add OpenApiExample and OpenApiTypes for better schema definition

## Frontend Implementation

### Core Component Setup
- [ ] Initialize React app with TypeScript and Vite
- [ ] Set up Material UI with proper theming
- [ ] Configure Redux Toolkit for state management
- [ ] Set up React Query for API data fetching
- [ ] Create basic layout structure (header, sidebar, etc.)

### Authentication Flow
- [ ] Implement login/signup screens
- [ ] Add JWT authentication handling
- [ ] Create protected routes
- [ ] Implement user profile management

### Inventory Management
- [ ] Create product listing and detail views
- [ ] Implement inventory item management
- [ ] Build inventory counting interface
- [ ] Create order management screens
- [ ] Design reporting dashboards

### User Feedback & Error Handling
- [ ] Implement loading indicators
- [ ] Add error message components
- [ ] Create notification system for success/warning/error
- [ ] Add form validation with error messaging

## Testing

### Backend Testing
- [ ] Complete tests for Menu app
- [ ] Add tests for remaining inventory models
- [ ] Add tests for API endpoints
- [ ] Test signal handlers and validators

### Frontend Testing
- [ ] Set up testing framework (React Testing Library)
- [ ] Create unit tests for components
- [ ] Write integration tests for complex features
- [ ] Test Redux logic and API interactions

### End-to-End Testing
- [ ] Set up Cypress for end-to-end testing
- [ ] Create tests for critical user flows
- [ ] Test backend-frontend integration
- [ ] Create test data fixtures

## DevOps & Deployment

### Production Deployment
- [ ] Update Docker configuration for production
- [ ] Configure static and media file handling
- [ ] Set up database backup procedures
- [ ] Configure proper environment variables

### CI/CD Pipeline
- [ ] Create GitHub Actions workflow for testing
- [ ] Implement automated deployment
- [ ] Add linting and code quality checks
- [ ] Configure notifications for pipeline status 