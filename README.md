# SetLogs

A backend service for logging workouts, exercises, sets, and tracking progression. Built with FastAPI, PostgreSQL, and Redis to demonstrate real backend engineering and system design skills.

## Features

- **User Management**: Registration, authentication, and profile management
- **Exercise Catalog**: Create, update, and manage exercises with versioning
- **Workout Tracking**: Log workout sessions with sets, reps, and weights
- **Progress Reports**: On-demand summaries and progression tracking
- **Data Integrity**: Idempotency keys, optimistic locking, and audit trails
- **Performance**: Redis caching, database indexing, and load testing
- **Observability**: Structured logging, Prometheus metrics, and health checks

## Tech Stack

- **API**: FastAPI
- **Database**: PostgreSQL with SQLAlchemy and Alembic migrations
- **Cache**: Redis
- **Authentication**: JWT (access + refresh tokens)
- **Containerization**: Docker Compose
- **Code Quality**: Black, Ruff, isort, mypy
- **Testing**: pytest
- **CI/CD**: GitHub Actions

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.12+ (for local development)

### Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd SetLog
   ```

2. **Copy environment variables**
   ```bash
   cp .env.example .env
   ```

3. **Start the services**
   ```bash
   make run
   ```

4. **Verify the setup**
   ```bash
   curl http://localhost:8000/health
   ```

### Available Commands

| Command | Description |
|---------|-------------|
| `make run` | Start all services (API, PostgreSQL, Redis) |
| `make stop` | Stop all services |
| `make clean` | Stop services and remove volumes |
| `make test` | Run tests in Docker environment |
| `make ci-test` | Run tests directly (for CI) |
| `make lint` | Run code formatting and linting |
| `make ci-lint` | Run linting in check mode (CI safe) |
| `make seed` | Load demo data (when available) |
| `make bench` | Run performance benchmarks (when available) |

## Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:password@database:5432/setlogs` | Yes |
| `REDIS_URL` | Redis connection string | `redis://redis:6379` | Yes |
| `SECRET_KEY` | JWT secret key | `your-secret-key` | Yes |
| `ALGORITHM` | JWT algorithm | `HS256` | No |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token expiration | `30` | No |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token expiration | `7` | No |

## Development Workflow

### Local Development

1. **Start services**: `make run`
2. **Make changes** to your code
3. **Run linting**: `make lint` (formats code automatically)
4. **Run tests**: `make test`
5. **Stop services**: `make stop`

### Code Quality

- **Pre-commit hooks** automatically format code on commit
- **CI pipeline** runs linting and tests on every push/PR
- **Code formatting** uses Black, isort, and Ruff
- **Type checking** uses mypy

### Database Management

- **Migrations**: Managed with Alembic
- **Seeding**: Use `make seed` to load demo data
- **Backup**: Automated daily backups (when implemented)

## API Documentation

Once the API is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Project Structure

```
SetLog/
├── app/                    # Application code
│   ├── __init__.py
│   ├── main.py            # FastAPI application
│   ├── models/            # Database models
│   ├── api/               # API routes
│   └── services/          # Business logic
├── tests/                 # Test files
├── migrations/            # Alembic migrations
├── docker-compose.yaml    # Development environment
├── docker-compose.prod.yml # Production environment
├── requirements.txt       # Dependencies
├── requirements-dev.txt   # Development dependencies
├── requirements-ci.txt    # CI dependencies
├── .env.example          # Environment variables template
└── Makefile              # Development commands
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## License

This project is for portfolio purposes.