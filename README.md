# LoreBound - Trivia RPG Backend

[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-blue.svg)](https://postgresql.org)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://docker.com)

A production-ready FastAPI backend for the LoreBound trivia RPG game, featuring user authentication, content management, game runs, and leaderboards.

## 🎮 About LoreBound

LoreBound is an innovative trivia RPG that combines knowledge-based gameplay with role-playing game elements. Players progress through themed dungeons, answer trivia questions, collect items, and compete on leaderboards.

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     LoreBound Backend                      │
├─────────────────────────────────────────────────────────────┤
│  API Layer (FastAPI)                                       │
│  ├── Authentication (JWT + Apple Sign-In)                  │
│  ├── Content Management (Dungeons, Questions)              │
│  ├── Game Runs (Anti-cheat, Scoring)                      │
│  ├── User Profiles & Inventory                            │
│  └── Leaderboards & Statistics                            │
├─────────────────────────────────────────────────────────────┤
│  Service Layer                                             │
│  ├── AuthService (Registration, Login, JWT)               │
│  ├── ContentService (Questions, Daily Challenges)         │
│  ├── RunService (Game Logic, Anti-cheat)                  │
│  └── Background Jobs (Celery)                             │
├─────────────────────────────────────────────────────────────┤
│  Data Layer                                                │
│  ├── PostgreSQL (Users, Games, Content)                   │
│  ├── Redis (Caching, Sessions)                            │
│  └── External APIs (Trivia Questions)                     │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.11+
- PostgreSQL 15+
- Redis 7+

### Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd LoreBound
   ```

2. **Environment Setup**
   ```bash
   cd lorebound-backend
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Start with Docker**
   ```bash
   docker-compose up -d
   ```

4. **Run Database Migrations**
   ```bash
   docker-compose --profile migration run --rm migrate
   ```

5. **Access the API**
   - Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/healthz

## 🔧 Services Architecture

### Core Services

#### 🔐 Authentication Service
- **JWT-based authentication** with RSA256 signing
- **Apple Sign-In integration** for iOS users
- **Password hashing** with bcrypt
- **Token refresh** mechanism
- **User registration & login**

#### 🎯 Content Service
- **Dynamic question fetching** from external APIs
- **Dungeon & tier management**
- **Daily challenge generation**
- **Content version control**
- **Deterministic question selection**

#### 🎮 Game Run Service
- **Anti-cheat validation** with cryptographic signatures
- **Real-time score calculation**
- **Progress tracking**
- **Turn-based gameplay** support
- **Run state management**

#### 📊 Data Services
- **User profiles & progression**
- **Inventory & item management**
- **Leaderboard generation**
- **Statistics & analytics**

### Background Jobs (Celery)
- **Daily challenge generation**
- **Leaderboard updates**
- **Analytics processing**
- **Content refresh**

## 📂 Project Structure

```
lorebound-backend/
├── app/
│   ├── api/v1/routers/          # API endpoints
│   │   ├── auth.py              # Authentication endpoints
│   │   ├── content.py           # Content management
│   │   ├── runs.py              # Game run endpoints
│   │   ├── profile.py           # User profiles
│   │   └── leaderboards.py      # Leaderboards
│   ├── core/                    # Core utilities
│   │   ├── config.py            # Configuration management
│   │   ├── security.py          # JWT & password handling
│   │   ├── dependencies.py      # FastAPI dependencies
│   │   └── logging.py           # Logging configuration
│   ├── domain/                  # Domain models
│   │   ├── models.py            # SQLAlchemy models
│   │   └── enums.py             # Enumerations
│   ├── services/                # Business logic
│   │   ├── auth_service.py      # Authentication logic
│   │   ├── content_service.py   # Content management
│   │   ├── run_service.py       # Game run logic
│   │   └── apple_service.py     # Apple Sign-In
│   ├── repositories/            # Data access layer
│   │   ├── user_repo.py         # User data operations
│   │   ├── content_repo.py      # Content data operations
│   │   └── run_repo.py          # Game run data operations
│   ├── schemas/                 # Pydantic schemas
│   │   ├── auth.py              # Authentication schemas
│   │   ├── content.py           # Content schemas
│   │   └── run.py               # Game run schemas
│   ├── jobs/                    # Background jobs
│   │   ├── tasks/               # Celery tasks
│   │   └── worker.py            # Celery worker
│   └── main.py                  # FastAPI application
├── migrations/                  # Alembic database migrations
├── tests/                       # Test suite
├── scripts/                     # Utility scripts
├── secrets/                     # JWT keys & certificates
├── docker-compose.yml           # Development environment
├── Dockerfile                   # Container configuration
└── pyproject.toml              # Python dependencies
```

## 🔌 API Endpoints

### Authentication
- `POST /v1/auth/register` - User registration
- `POST /v1/auth/login` - User login
- `POST /v1/auth/apple` - Apple Sign-In
- `POST /v1/auth/refresh` - Token refresh
- `GET /v1/auth/me` - Current user info
- `POST /v1/auth/logout` - User logout

### Content Management
- `GET /v1/content/dungeons` - List dungeons
- `GET /v1/content/dungeons/{id}` - Dungeon details
- `GET /v1/content/questions` - Get questions
- `GET /v1/content/daily` - Daily challenge
- `POST /v1/content/refresh-questions` - Refresh question pool

### Game Runs
- `POST /v1/runs/start` - Start new run
- `POST /v1/runs/{id}/submit` - Submit completed run
- `GET /v1/runs/` - User's run history
- `GET /v1/runs/{id}` - Run details
- `POST /v1/runs/{id}/abandon` - Abandon run

### User Management
- `GET /v1/profile/` - User profile
- `PUT /v1/profile/` - Update profile
- `GET /v1/inventory/` - User inventory
- `POST /v1/inventory/equip` - Equip items

### Leaderboards
- `GET /v1/leaderboards/` - Global leaderboards
- `GET /v1/leaderboards/me` - User rankings

## 🛡️ Security Features

- **JWT Authentication** with RSA256 signing
- **Password hashing** with bcrypt
- **Apple Sign-In** integration with token validation
- **Anti-cheat protection** for game runs
- **Rate limiting** and request validation
- **CORS configuration** for web clients
- **Environment-based secrets** management

## 🗄️ Database Schema

### Core Tables
- **users** - User accounts and authentication
- **profiles** - User profiles and progression
- **dungeons** - Game content structure
- **questions** - Trivia questions and metadata
- **runs** - Game session records
- **scores** - Individual game scores
- **inventory** - User items and equipment
- **achievements** - User achievements
- **leaderboard_snapshots** - Cached leaderboard data

## 🔧 Configuration

### Environment Variables
```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@host:port/db
REDIS_URL=redis://localhost:6379/0

# JWT Configuration
JWT_PRIVATE_KEY_PATH=secrets/jwt_private.pem
JWT_PUBLIC_KEY_PATH=secrets/jwt_public.pem
ACCESS_TOKEN_TTL_SECONDS=900
REFRESH_TOKEN_TTL_SECONDS=1209600

# Apple Sign-In (Optional)
APPLE_TEAM_ID=your_team_id
APPLE_CLIENT_ID=your_client_id
APPLE_KEY_ID=your_key_id
APPLE_PRIVATE_KEY_PATH=secrets/apple_signin_key.p8

# Application
APP_ENV=dev|prod
DEBUG=true|false
CORS_ORIGINS=["http://localhost:3000"]
```

## 🧪 Testing

```bash
# Run all tests
python -m pytest

# Run specific test files
python -m pytest tests/test_auth.py
python -m pytest tests/test_content.py

# Run with coverage
python -m pytest --cov=app tests/

# Test authentication endpoints
python scripts/test_registration.py
```

#For Testing We are using the Pixel 9 Pro XL emulator found in Android Studio

## 📈 Monitoring & Health Checks

- **Health Endpoint**: `/healthz` - Basic health check
- **Detailed Health**: `/healthz/detailed` - Comprehensive system status
- **Metrics**: `/metrics` - Prometheus-compatible metrics
- **Database Connection**: Real-time connection testing
- **Configuration Validation**: Environment setup verification

## 🔄 Development Workflow

1. **Feature Development**
   ```bash
   # Create feature branch
   git checkout -b feature/new-feature
   
   # Make changes and test
   python -m pytest
   
   # Run the development server
   docker-compose up -d
   ```

2. **Database Changes**
   ```bash
   # Create migration
   alembic revision --autogenerate -m "Description"
   
   # Apply migration
   alembic upgrade head
   ```

3. **Testing**
   ```bash
   # Unit tests
   python -m pytest tests/
   
   # Integration tests
   python scripts/test_live_api.py
   ```

## 🚀 Deployment

### Production Checklist
- [ ] Set `APP_ENV=prod`
- [ ] Configure proper `DATABASE_URL`
- [ ] Set up JWT keys (`jwt_private.pem`, `jwt_public.pem`)
- [ ] Configure Apple Sign-In credentials (if needed)
- [ ] Set up Redis for caching
- [ ] Configure CORS origins
- [ ] Set up monitoring and logging
- [ ] Run database migrations
- [ ] Set up SSL/TLS certificates

### Docker Deployment
```bash
# Build production image
docker build -t lorebound-backend .

# Run with production environment
docker-compose -f docker-compose.prod.yml up -d
```


## 🔗 Related Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Celery Documentation](https://docs.celeryproject.org/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)



