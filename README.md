# CocktailAI

CocktailAI is an AI-powered beverage program optimization platform for bar inventory management. It transforms inventory management from a time-consuming accounting exercise to a strategic profit-driving tool for bars and restaurants.

## Features

- User Authentication and Profiles
- Inventory Management
- Recipe Management (future phase)
- Menu Engineering (future phase)
- Dashboard and Reporting
- POS Integration (future phase)

## Technology Stack

- **Backend**: Django with Django REST Framework
- **Frontend**: React with TypeScript
- **Database**: PostgreSQL
- **Containerization**: Docker with Docker Compose
- **UI Framework**: Material UI
- **State Management**: Redux Toolkit + React Query

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Git

### Installation

1. Clone the repository
```bash
git clone https://github.com/yourusername/cocktailai.git
cd cocktailai
```

2. Create environment files
```bash
cp .env.example .env
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
```

3. Start the application
```bash
docker-compose up -d
```

4. Access the application
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/api
- Admin interface: http://localhost:8000/admin

## Development

### Backend

The backend is built with Django and Django REST Framework. To run it separately:

```bash
cd backend
docker-compose up -d db
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### Frontend

The frontend is built with React and TypeScript. To run it separately:

```bash
cd frontend
npm install
npm run dev
```

## License

[MIT](LICENSE) 