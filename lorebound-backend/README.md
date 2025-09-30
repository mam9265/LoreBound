# LoreBound Backend

Production-ready FastAPI backend for LoreBound, a mobile trivia RPG game.

## Features

- **FastAPI** with async/await support
- **PostgreSQL** with SQLAlchemy 2.x (async)
- **Redis** for caching and leaderboards
- **JWT Authentication** with RS256 + Apple Sign-In support
- **Anti-cheat** game run verification with HMAC signatures
- **Real-time Leaderboards** using Redis sorted sets
- **Background Jobs** with Celery
- **Docker Compose** development environment
- **Comprehensive Testing** with pytest
- **Code Quality** with ruff, black, mypy

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local development)
- Poetry (for dependency management)

### Environment Setup

1. Clone the repository
2. Copy environment configuration:
   ```bash
   cp .env.example .env
   ```
3. Generate JWT keys (for development):
   ```bash
   mkdir -p secrets
   # Generate RS256 key pair
   openssl genrsa -out secrets/jwt_private.pem 2048
   openssl rsa -in secrets/jwt_private.pem -pubout -out secrets/jwt_public.pem
   ```

### Docker Development

Start all services:
```bash
make up
```

This will start:
- **API Server** on http://localhost:8000
- **PostgreSQL** on localhost:5432
- **Redis** on localhost:6379
- **Celery Worker** for background jobs

View logs:
```bash
make logs
```

Stop services:
```bash
make down
```

### API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/healthz

## Development

### Local Setup

Install dependencies:
```bash
make install
```

Run locally (requires PostgreSQL and Redis running):
```bash
make dev
```

### Code Quality

Format code:
```bash
make fmt
```

Run linting:
```bash
make lint
```

Run tests:
```bash
make test
```

### Database

Run migrations:
```bash
make migrate
```

Load seed data:
```bash
make seed
```

### Available Make Commands

- `make up` - Start all services
- `make down` - Stop all services  
- `make logs` - View logs
- `make test` - Run tests
- `make lint` - Run linting
- `make fmt` - Format code
- `make migrate` - Run database migrations
- `make seed` - Load seed data
- `make clean` - Clean up containers and volumes

## API Endpoints

### Authentication
- `POST /v1/auth/register` - Register new user
- `POST /v1/auth/login` - Login with email/password
- `POST /v1/auth/apple` - Sign in with Apple
- `POST /v1/auth/refresh` - Refresh access token
- `GET /v1/auth/me` - Get current user

### Content
- `GET /v1/content/dungeons` - List dungeons
- `GET /v1/content/dungeons/{id}` - Get dungeon details
- `GET /v1/content/questions` - Get questions (deterministic)
- `GET /v1/content/daily` - Get daily challenge

### Game Runs
- `POST /v1/runs/start` - Start new run
- `POST /v1/runs/submit` - Submit completed run

### Leaderboards
- `GET /v1/leaderboards` - Get leaderboard
- `GET /v1/leaderboards/me` - Get user rank

### Profile & Inventory
- `GET /v1/profile` - Get user profile
- `PUT /v1/profile` - Update profile
- `GET /v1/inventory` - Get inventory
- `POST /v1/inventory/equip` - Equip item

### Configuration
- `GET /v1/config` - Get game config and feature flags

## Architecture

```
app/
├── core/           # Configuration, security, dependencies
├── api/v1/         # API endpoints and routers
├── domain/         # Business entities and enums
├── schemas/        # Pydantic models for validation
├── repositories/   # Database access layer
├── services/       # Business logic layer
├── jobs/           # Background tasks
├── middleware/     # Custom middleware
└── main.py         # FastAPI application factory
```

## Security

- **JWT Tokens**: RS256 algorithm with rotating refresh tokens
- **Password Hashing**: bcrypt with salt
- **Rate Limiting**: Per-endpoint rate limits
- **CORS**: Configurable origins
- **Anti-cheat**: HMAC-verified game run submissions
- **Apple Sign-In**: Token verification with Apple's JWKs

## Game Features

### Anti-cheat System
Game runs use server-side verification:
1. Client starts run, receives seed and session token
2. Each turn is HMAC-signed with turn data
3. Server replays run using same seed to verify timing and answers
4. Aggregate signature prevents tampering

### Leaderboards
Real-time rankings using Redis sorted sets:
- **Daily**: Reset at midnight UTC
- **Weekly**: Monday-Sunday cycles  
- **All-time**: Persistent rankings

### Daily Challenges
- Generated at midnight UTC with unique seed
- Rotates through dungeon categories
- Special modifiers for variety

## Deployment

### Environment Variables

Key configuration (see `.env.example`):
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string  
- `JWT_PRIVATE_KEY_PATH` - Path to RS256 private key
- `APPLE_TEAM_ID`, `APPLE_CLIENT_ID` - Apple Sign-In config
- `SENTRY_DSN` - Error tracking (optional)

### Production Deployment

The application is containerized and ready for deployment on:
- **AWS ECS/Fargate** 
- **Google Cloud Run**
- **Kubernetes**
- **Docker Swarm**

Key considerations:
- Use managed PostgreSQL and Redis services
- Store secrets in secure secret management
- Configure proper logging and monitoring
- Set up health checks and auto-scaling

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Run `make lint` and `make test`
5. Submit a pull request

