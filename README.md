# Budget Tracker API

A comprehensive personal finance management API built with FastAPI, featuring user authentication, transaction tracking, budget management, and financial analytics.

## Features

- **User Management**: Secure user registration and authentication with JWT tokens
- **Category Management**: Organize transactions with customizable categories
- **Transaction Tracking**: Record income, expenses, and transfers with detailed metadata
- **Budget Management**: Set and monitor budgets with progress tracking
- **Security**: JWT authentication with refresh tokens, password hashing, rate limiting
- **Database**: PostgreSQL with async SQLAlchemy and Alembic migrations
- **API Documentation**: Automatic OpenAPI/Swagger documentation
- **Docker Support**: Container-ready with Docker Compose configuration

## Technology Stack

- **Framework**: FastAPI 0.104+
- **Database**: PostgreSQL with AsyncPG driver  
- **ORM**: SQLAlchemy 2.0 with async support
- **Authentication**: JWT with refresh tokens, bcrypt password hashing
- **Validation**: Pydantic v2 schemas with advanced validation
- **Migrations**: Alembic for database schema management
- **Testing**: Pytest with async support
- **Rate Limiting**: SlowAPI for request rate limiting
- **CORS**: Configurable cross-origin resource sharing

## Quick Start

### Using Docker (Recommended)

1. **Clone and setup**:
   ```bash
   git clone <repository-url>
   cd budget-tracker-backend
   cp .env.example .env
   ```

2. **Start services**:
   ```bash
   docker-compose up -d
   ```

3. **Access the API**:
   - API: http://localhost:8000
   - Documentation: http://localhost:8000/docs
   - Database: localhost:5432

### Manual Setup

1. **Prerequisites**:
   - Python 3.11+
   - PostgreSQL 13+
   - pip or poetry

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment setup**:
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials
   ```

4. **Database setup**:
   ```bash
   # Create database
   createdb budget_tracker
   
   # Run migrations
   alembic upgrade head
   ```

5. **Start the server**:
   ```bash
   uvicorn app.main:app --reload
   ```

## API Endpoints

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - User login
- `POST /auth/refresh` - Refresh access token
- `POST /auth/logout` - User logout

### User Management
- `GET /users/me` - Get current user profile
- `PUT /users/me` - Update user profile
- `DELETE /users/me` - Deactivate user account

### Categories
- `POST /categories/` - Create category
- `GET /categories/` - List user categories
- `GET /categories/{id}` - Get specific category
- `PUT /categories/{id}` - Update category
- `DELETE /categories/{id}` - Delete category

### Transactions
- `POST /transactions/` - Create transaction
- `GET /transactions/` - List transactions (with filters)
- `GET /transactions/{id}` - Get specific transaction
- `PUT /transactions/{id}` - Update transaction
- `DELETE /transactions/{id}` - Delete transaction

### Budgets
- `POST /budgets/` - Create budget
- `GET /budgets/` - List budgets (with filters)
- `GET /budgets/{id}` - Get specific budget
- `GET /budgets/{id}/progress` - Get budget progress
- `PUT /budgets/{id}` - Update budget
- `DELETE /budgets/{id}` - Delete budget

## Configuration

Environment variables (see `.env.example`):

```env
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/budget_tracker

# JWT Settings
SECRET_KEY=your-very-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Security
BCRYPT_ROUNDS=12

# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60

# CORS
CORS_ORIGINS=["http://localhost:3000"]
```

## Database Schema

### Core Entities
- **Users**: User accounts with authentication
- **Categories**: Transaction categorization with colors/icons
- **Transactions**: Financial transactions (income/expense/transfer)
- **Budgets**: Budget tracking with period-based limits
- **RefreshTokens**: JWT refresh token management

### Key Features
- UUID primary keys for all entities
- Decimal precision for financial amounts
- Audit timestamps (created_at, updated_at)
- Proper foreign key relationships with cascading
- Enum types for transaction types and budget periods

## Security Features

- **Authentication**: JWT access tokens with short expiration
- **Refresh Tokens**: Secure token rotation with revocation
- **Password Security**: bcrypt hashing with configurable rounds
- **Rate Limiting**: Request throttling per IP address
- **Input Validation**: Comprehensive Pydantic validation
- **CORS Protection**: Configurable allowed origins
- **Error Handling**: Secure error messages without data leakage

## Testing

Run the test suite:

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html
```

## Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

## Development

### Project Structure
```
budget-tracker-backend/
├── app/
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration settings
│   ├── database.py          # Database connection
│   ├── models/              # SQLAlchemy models
│   ├── schemas/             # Pydantic schemas
│   ├── api/                 # API route handlers
│   ├── core/                # Authentication & security
│   └── utils/               # Utility functions
├── alembic/                 # Database migrations
├── tests/                   # Test files
├── docker-compose.yml       # Docker services
└── requirements.txt         # Python dependencies
```

### Code Quality
- Type hints throughout codebase
- Async/await pattern for database operations
- Comprehensive error handling
- Input validation and sanitization
- Security best practices
- RESTful API design

## Production Deployment

### Security Checklist
- [ ] Change default SECRET_KEY
- [ ] Use environment variables for sensitive data
- [ ] Configure proper CORS origins
- [ ] Set up HTTPS/TLS
- [ ] Configure rate limiting
- [ ] Set up monitoring and logging
- [ ] Regular security updates

### Performance
- [ ] Configure connection pooling
- [ ] Set up database indexing
- [ ] Implement caching (Redis)
- [ ] Configure reverse proxy (nginx)
- [ ] Set up load balancing if needed

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality  
5. Run the test suite
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For questions or issues:
- Create an issue on GitHub
- Check the API documentation at `/docs`
- Review the test files for usage examples