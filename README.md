# Django Starter Kit
A production-ready backend foundation built with Django and Django REST Framework, implementing Clean Architecture, modular design, and Docker-based development environments.

Technology Stack:
- Python 3.12
- Django & Django REST Framework
- PostgreSQL
- Docker & Poetry

## Overview
This repository provides a structured backend architecture with:
- Clean Architecture principles
- Modular feature-based structure (Django apps)
- Separation of concerns (API, services, selectors, models)
- Production-ready Docker setup
- Database migrations
- Testable use cases

The goal is to provide a scalable and maintainable backend foundation that can be reused across multiple services.

### Architecture
This project follows Clean Architecture principles, adapted for Django.
Layers are separated to ensure:
- Business logic is independent of HTTP request handling
- High testability
- Clear separation of concerns

Architecture layers:

    API / Presentation Layer (Views, Serializers, URLs)
            ↓
    Application / Service Layer (Services, Selectors)
            ↓
    Data Access / Domain Layer (Models, Repositories)

### Project Structure

    ├── apps
    │   ├── generics                                            # Shared core/generic utilities
    │   │   ├── exceptions.py                                     # Custom application exceptions
    │   │   ├── middleware                                        # Custom Django middlewares
    │   │   │   ├── correlation_id_middleware.py                     # Injects correlation IDs for request tracking
    │   │   │   ├── current_user_middleware.py                       # Attaches current user to async threads
    │   │   │   ├── device_middleware.py                             # Device fingerprinting and tracking
    │   │   │   ├── exception_handler.py                             # Global exception catching and formatting
    │   │   │   ├── ip_whitelist_middleware.py                       # IP-based access control
    │   │   │   └── logging_middleware.py                            # Request/Response logging
    │   │   ├── mixins.py                                       # Reusable model/view mixins
    │   │   ├── permissions.py                                  # Custom DRF permission classes
    │   │   ├── responses.py                                    # Standardized API response formatters
    │   │   └── utils                                           # Helper utility functions
    │   │       ├── json_formatter.py                              # Custom JSON encoding formatting
    │   │       ├── logging_filters.py                             # Filters for sanitizing log outputs
    │   │       └── token_utils.py                                 # JWT/Token generation and parsing
    │   └── users                                               # Users module
    │       ├── admin.py                                          # Django admin panel configurations
    │       ├── api                                               # Controllers Layer
    │       │   ├── auth_views.py                                    # Authentication endpoints (Login)
    │       │   ├── profile_views.py                                 # User profile management endpoints
    │       │   ├── role_views.py                                    # RBAC Role management endpoints
    │       │   ├── schemas.py                                       # OpenAPI documentation schemas
    │       │   ├── urls.py                                          # API route definitions
    │       │   └── user_views.py                                    # User CRUD operations endpoints
    │       ├── constants.py                                    # Module-specific constants and enums
    │       ├── __init__.py                                     # Python package marker
    │       ├── models.py                                       # Data Access / Entities Layer
    │       ├── selectors                                       # Application Layer (Read Logic)
    │       │   ├── auth_selectors.py                                # Queries related to authentication
    │       │   ├── role_selectors.py                                # Queries for roles and permissions
    │       │   └── user_selectors.py                                # Queries for fetching user details
    │       ├── serializers                                     # Request validation (DTOs)
    │       │   ├── auth_serializer.py                               # Login/Registration validation
    │       │   ├── profile_serializer.py                            # Profile update validation
    │       │   ├── role_serializer.py                               # Role/Permission validation
    │       │   └── user_serializer.py                               # User CRUD validation
    │       ├── services                                        # Application Layer (Write Logic)
    │       │   ├── auth_service.py                                  # Login/Auth token generation logic
    │       │   ├── profile_service.py                               # Logic for modifying user profiles
    │       │   ├── role_service.py                                  # Logic for role assignment/creation
    │       │   └── user_service.py                                  # Logic for creating/updating users
    │       ├── signals.py                                      # Django signals (event hooks)
    │       └── tests                                           # Unit & Integration Tests
    │           ├── factories                                        # Model factories for testing
    │           │   └── user_factory.py                              # Test data generator for Users
    │           └── test_user_api.py                                 # API endpoint tests
    ├── config                                                  # Global config and entrypoints
    │   ├── asgi.py                                             # ASGI config for async servers
    │   ├── celery.py                                           # Celery background tasks config
    │   ├── __init__.py                                         # Python package marker
    │   ├── settings                                            # Django configuration settings
    │   │   ├── base.py                                         # Shared/Common settings
    │   │   └── develop.py                                      # Development environment settings
    │   ├── urls.py                                             # Root URL configuration
    │   ├── utils.py                                            # Configuration utilities
    │   └── wsgi.py                                             # WSGI config for sync servers
    ├── docker-compose.local.yml                                # Development environment config
    ├── docker-compose.yml                                      # Base Docker environment config
    ├── Dockerfile                                              # Docker build instructions
    ├── dump.rdb                                                # Local Redis database dump
    ├── logs                                                    # Application log files
    │   └── app.log                                             # Main application log
    ├── manage.py                                               # Django management script
    ├── poetry.lock                                             # Locked dependency versions
    ├── pyproject.toml                                          # Project metadata and dependencies
    ├── pytest.ini                                              # Pytest configuration settings
    ├── README.md                                               # Project documentation
    ├── requirements.txt                                        # Fallback requirements file
    └── start.sh                                                # Docker entrypoint script

### Layer Responsibilities

- API / Presentation Layer
    Handles HTTP requests and responses.
  - Django REST Framework views/viewsets
  - Request validation (Serializers)
  - Response formatting

- Service & Selector Layer
    Contains application business logic.
  - Services: Handle "write" operations (Create, Update, Delete) and complex workflows.
  - Selectors: Handle "read" operations (Fetch data without modifying it).
  - Business rules are enforced here, keeping models and views thin.

- Domain & Data Access Layer
  Defines core data structures and database interactions.
  - Django Models (Entities + Adapters)
  - Custom managers or querysets

### Installation Guide

Explain how to run the project locally.

1. Clone the repository:
   ```bash
   git clone https://github.com/company-name/project-name.git
   cd project-name
   ```

2. Create a virtual environment and install dependencies:
   Using Poetry (Recommended):
   ```bash
   poetry install
   poetry shell
   ```
   Or using pip:
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. Run migrations:
   ```bash
   python manage.py makemigrations --settings=config.settings.env
   python manage.py migrate --settings=config.settings.env
   ```

4. Run application:
   ```bash
   python manage.py runserver --settings=config.settings.env
   redis-server
   celery -A config.celery worker --loglevel=info
   ```

Application will be available at:
`http://localhost:8000`

Swagger documentation (if configured via drf-spectacular):
`http://localhost:8000/api/schema/swagger-ui/`

Running with Docker:
```bash
docker-compose up --build
```

In local environment run:
```bash
docker-compose -f docker-compose.yml -f docker-compose.local.yml up --build
```

### Environment Configuration
Configuration is managed in the `config/settings/` directory.

Environment variables should be defined using `.env`.
Copy `.env.example` to `.env` and fill in the values.

### Database Migrations
Migrations are managed using Django's built-in migration system.
Migrations are stored in each app's `migrations` directory.

Create new migration:
```bash
python manage.py makemigrations --settings=config.settings.env
```

Apply migrations:
```bash
python manage.py migrate --settings=config.settings.env
```

### Testing
Tests are stored in the `tests` directory within each app.

Run tests using pytest:
```bash
pytest
```

Run specific tests:
```bash
pytest apps/users/tests/
```

### Why This Architecture?
Benefits:
- Scalable for large applications
- Clear code boundaries
- High testability
- "Fat services, thin views" pattern prevents logic duplication 
- Easy onboarding for teams
