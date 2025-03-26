# CocktailAI Backend

This is the backend for the CocktailAI application, a beverage program optimization platform for bar inventory management.

## Setup

1. Clone the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`
4. Install requirements: `pip install -r requirements.txt`
5. Run migrations: `python manage.py migrate`
6. Start the development server: `python manage.py runserver`

## Demo Data

The application comes with fixture data to help you get started with testing and development. 
To load all demo data at once, run:

```bash
python manage.py load_demo_data
```

To clear the database before loading data, add the `--flush` flag:

```bash
python manage.py load_demo_data --flush
```

### Available Fixtures

The demo data includes:

- **Users**: Admin user account
- **Inventory**: Categories, suppliers, locations, products, inventory items, and transactions
- **Menu**: Recipe categories, recipes with ingredients, and menus

## API Documentation

API documentation is available at `/api/docs/` when the server is running.

## Running Tests

Run tests with:

```bash
python manage.py test
```

## Contributors

- CocktailAI Development Team 