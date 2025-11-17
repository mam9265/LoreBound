# LoreBound Backend Architecture Overview

## System Overview

LoreBound is a trivia RPG game backend built with FastAPI, featuring a comprehensive game management system with user progression, dungeon-based gameplay, inventory management, and competitive leaderboards.

## Technology Stack

- **Framework**: FastAPI 0.104.0+ with async/await
- **Database**: PostgreSQL with SQLAlchemy 2.0 (async)
- **Caching**: Redis for session management and caching
- **Authentication**: JWT with RS256 + Apple Sign-In integration
- **Task Queue**: Celery with Redis broker
- **Monitoring**: Sentry for error tracking, Prometheus metrics
- **Deployment**: Docker containers with docker-compose

## Architecture Patterns

- **Repository Pattern**: Database operations abstracted through repositories
- **Domain-Driven Design**: Clear separation of domain models, schemas, and business logic
- **Dependency Injection**: FastAPI's dependency system for database sessions and auth
- **Clean Architecture**: Layered approach with clear boundaries

---

## 🟢 IMPLEMENTED COMPONENTS

### 1. Core Infrastructure ✅

#### Database Layer
- **SQLAlchemy Models**: Complete domain model definitions
  - User management (Users, Profiles)
  - Game content (Dungeons, Questions, Items)
  - Gameplay (Runs, Scores)
  - Social features (Achievements, Leaderboards)
- **Connection Management**: Async engine with connection pooling
- **Migration Support**: Alembic integration for schema management

#### Configuration Management ✅
- **Environment-based Settings**: Pydantic Settings with validation
- **Secret Management**: JWT keys, API keys, database credentials
- **Feature Flags**: Database-driven feature toggles
- **Multi-environment Support**: Development, staging, production configs

#### Security Infrastructure ✅
- **JWT Implementation**: RS256 with public/private key pairs
- **Apple Sign-In**: Complete integration setup
- **CORS Configuration**: Configurable origins for web clients
- **Input Validation**: Pydantic schemas with comprehensive validation

### 2. Data Models & Schemas ✅

#### User System
```python
# Complete user management models
- User: Core authentication and account data
- Profile: Game progression (level, XP, avatar)
- UserAchievement: Progress tracking
```

#### Game Content
```python
# Rich content system
- Dungeon: Trivia categories with modifiers
- DungeonTier: Floor-based progression
- Question: Multi-choice questions with difficulty
- Item: Equipment with stats and rarity
```

#### Gameplay & Scoring
```python
# Comprehensive game session tracking
- Run: Game sessions with anti-cheat signatures
- Score: Per-floor scoring with time tracking
- DailyChallenge: Time-limited challenges
```

### 3. Repository Layer ✅

#### User Repository (`user_repo.py`)
- ✅ User CRUD operations
- ✅ Authentication lookups (email, Apple ID)
- ✅ Profile management
- ✅ XP and leveling system
- ✅ Status management

#### Run Repository (`run_repo.py`)
- ✅ Game session management
- ✅ Score recording and retrieval
- ✅ User performance analytics
- ✅ Daily run tracking
- ✅ Leaderboard data aggregation

#### Content Repository (`content_repo.py`)
- ✅ Dungeon and question management
- ✅ Content versioning
- ✅ Question filtering by difficulty
- ✅ Daily challenge generation

#### Inventory Repository (`inventory_repo.py`)
- ✅ Item ownership tracking
- ✅ Equipment management
- ✅ Item acquisition and rewards

#### Leaderboard Repository (`leaderboard_repo.py`)
- ✅ Score ranking calculations
- ✅ Time-scoped leaderboards (daily, weekly, all-time)
- ✅ User rank calculations
- ✅ Snapshot management for performance

### 4. API Structure ✅

#### Router Organization
```
/v1/auth/*      - Authentication endpoints
/v1/content/*   - Game content (dungeons, questions)
/v1/runs/*      - Game session management
/v1/profile/*   - User profile management
/v1/inventory/* - Item and equipment management
/v1/leaderboards/* - Ranking and competition
/v1/config/*    - Game configuration and flags
```

#### Health & Monitoring
- ✅ Basic health checks (`/healthz`)
- ✅ Detailed health with database status
- ✅ Metrics endpoint for Prometheus
- ✅ Configuration validation

### 5. Testing Infrastructure ✅

#### Comprehensive Test Suite
- ✅ **Schema Tests**: Pydantic model validation
- ✅ **Repository Tests**: Database operation testing
- ✅ **API Tests**: Endpoint structure validation
- ✅ **Security Tests**: XSS, SQL injection, input validation
- ✅ **Performance Tests**: Response times, memory usage
- ✅ **Integration Tests**: End-to-end user journeys

#### Test Configuration
- ✅ Pytest configuration with async support
- ✅ Mock fixtures for external services
- ✅ Database test isolation
- ✅ Coverage reporting setup

---

## 🔴 YET TO BE IMPLEMENTED

### 1. Business Logic Services ✅

#### Authentication Service ✅
```python
# IMPLEMENTED:
✅ auth_service.py: Complete orchestration layer
✅ apple_service.py: Apple Sign-In token verification  
✅ password hashing: Integrated in security.py
✅ jwt_service.py: Token generation/validation in security.py
✅ Exception handling: Comprehensive error management
✅ Dependency injection: FastAPI-compatible factories
```

#### Game Services ✅
```python
# IMPLEMENTED:
✅ run_service.py: Complete game session orchestration
✅ content_service.py: Question selection algorithms + external API
✅ anti_cheat_service.py: HMAC signature validation (in run_service)
✅ progression_service.py: XP/leveling logic (in run_service)
✅ trivia_api_client.py: External question sourcing
```

#### Content Services ✅
```python
# IMPLEMENTED:
✅ content_service.py: Complete content management
✅ question_service.py: Deterministic selection algorithms
✅ daily_challenge_service.py: Automated challenge generation
✅ difficulty_service.py: Floor-based adaptive difficulty
✅ External API integration: OpenTDB + Trivia API support
```

### 2. API Endpoint Implementations ✅

#### Authentication Endpoints (`/v1/auth/*`) ✅
- ✅ `POST /register`: User registration with email validation
- ✅ `POST /login`: Email/password authentication  
- ✅ `POST /apple`: Apple Sign-In integration
- ✅ `POST /refresh`: JWT token refresh
- ✅ `GET /me`: Current user information
- ✅ `POST /logout`: User logout

#### Game Endpoints (`/v1/runs/*`) ✅
- ✅ `POST /start`: Initialize game session with anti-cheat token
- ✅ `POST /{id}/submit`: Complete run with anti-cheat validation
- ✅ `GET /`: User's run history (paginated)
- ✅ `GET /{id}`: Specific run details
- ✅ `POST /{id}/abandon`: Abandon run in progress
- ✅ `GET /stats/me`: User game statistics

#### Content Endpoints (`/v1/content/*`) ✅
- ✅ `GET /dungeons`: Available dungeons list
- ✅ `GET /dungeons/{id}`: Specific dungeon details
- ✅ `GET /questions`: Deterministic question selection
- ✅ `GET /daily`: Current daily challenge
- ✅ `POST /refresh-questions`: Question pool refresh from external APIs

#### Profile Endpoints (`/v1/profile/*`) 🚧
- `GET /`: User profile information
- `PUT /`: Update profile (handle, avatar)
- `GET /stats`: User statistics and achievements

#### Inventory Endpoints (`/v1/inventory/*`) 🚧
- `GET /`: User's inventory and equipment
- `POST /equip`: Equip/unequip items
- `GET /items`: Available items catalog

#### Leaderboard Endpoints (`/v1/leaderboards/*`) 🚧
- `GET /`: Global leaderboards with filters
- `GET /me`: User's rank and nearby players
- `GET /daily`: Daily challenge leaderboards

### 3. Middleware Layer ✅

#### Security Middleware ✅
```python
# IMPLEMENTED:
✅ CORS middleware: Configured in main.py
✅ auth_middleware.py: JWT validation in dependencies.py
✅ Error handling: Global exception handling in routers
✅ Input validation: Comprehensive Pydantic schemas
✅ Security headers: Basic security implemented
```

#### Monitoring Middleware ✅
```python
# IMPLEMENTED:
✅ request_logging.py: Structured logging throughout
✅ Health monitoring: /healthz endpoints with database checks
✅ error_handling.py: Comprehensive error responses
✅ Metrics endpoint: /metrics placeholder ready
```

### 4. Background Services ✅

#### Celery Tasks ✅
```python
# IMPLEMENTED:
✅ daily_tasks.py: Daily challenge generation, question pool refresh
✅ leaderboard_tasks.py: Periodic leaderboard updates
✅ analytics_tasks.py: User statistics and system monitoring
✅ worker.py: Complete Celery configuration with routing
✅ Task scheduling: Beat schedule for automated tasks
```

#### Scheduled Jobs ✅
- ✅ Daily challenge rotation (automated)
- ✅ Leaderboard snapshot generation (every 15 minutes)
- ✅ Question pool refresh (on-demand + scheduled)
- ✅ Database maintenance tasks (hourly cleanup)

### 5. External Integrations ✅

#### Apple Services ✅
- ✅ Apple ID token verification (dev + production ready)
- ✅ Apple Sign-In integration framework
- Apple App Store receipt validation (future)
- Apple Push Notifications (future)

#### Trivia APIs ✅
- ✅ OpenTDB (Open Trivia Database) integration
- ✅ Trivia API support with fallback
- ✅ Multi-provider question sourcing
- ✅ Rate limiting and retry logic

#### Monitoring & Analytics ✅
- ✅ Health monitoring with database checks
- ✅ Structured logging throughout application
- ✅ Error tracking and reporting
- ✅ Prometheus metrics endpoint
- Sentry error tracking setup (placeholder ready)
- Custom analytics events (framework ready)

### 6. Security Implementations ✅

#### Authentication Security ✅
- ✅ Password strength enforcement (Pydantic validation + bcrypt)
- ✅ JWT token rotation (access + refresh tokens)
- ✅ Session management (secure token handling)
- ✅ Email validation (RFC-compliant with fallbacks)
- Account lockout mechanisms (framework ready)

#### API Security ✅
- ✅ Input sanitization (Pydantic validation + field validators)
- ✅ SQL injection prevention (SQLAlchemy parameterized queries)
- ✅ CORS protection (configurable origins)
- ✅ Authentication middleware (JWT validation)
- Request rate limiting (framework ready)

#### Anti-Cheat Systems ✅
- ✅ Run signature validation (HMAC signatures)
- ✅ Session token verification
- ✅ Time-based validation (reasonable bounds)
- ✅ Score calculation validation
- ✅ Deterministic content (prevents manipulation)
- Score anomaly detection (framework ready)

### 7. Performance Optimizations 🚧

#### Caching Strategy
- Redis session storage
- Question pool caching
- Leaderboard caching
- Content versioning cache

#### Database Optimizations
- Query optimization
- Index strategy implementation
- Connection pool tuning
- Read replica setup (future)

### 8. DevOps & Deployment ✅

#### Container Orchestration ✅
- ✅ Production Docker configuration (multi-service)
- ✅ Environment-specific configs (dev/staging/prod)
- ✅ Health check implementations (/healthz endpoints)
- ✅ Graceful shutdown handling (lifespan management)
- ✅ Docker Compose orchestration (API, DB, Redis, Worker)

#### Development Tools ✅
- ✅ Comprehensive testing suite (unit + integration)
- ✅ Code quality tools (ruff, black, mypy configured)
- ✅ Development scripts (key generation, validation)
- ✅ Hot reloading in development
- CI/CD Pipeline (ready for implementation)

#### Monitoring Setup ✅
- ✅ Application health monitoring
- ✅ Database connection monitoring  
- ✅ Structured logging with levels
- ✅ Error tracking framework
- ✅ Performance metrics endpoint
- Advanced dashboards (ready for implementation)

---

## Implementation Status

### ✅ Phase 1: Core Functionality (COMPLETE)
1. ✅ **Authentication Services** - User registration, login, JWT handling
2. ✅ **Basic Game Flow** - Start run, submit score, anti-cheat validation
3. ✅ **Content Management** - Dungeon and question serving with external APIs

### ✅ Phase 2: Enhanced Features (COMPLETE)
1. ✅ **Advanced Game Features** - Daily challenges, deterministic content
2. ✅ **Security Hardening** - Anti-cheat validation, session tokens
3. ✅ **External Integration** - Live trivia API, multi-provider support

### 🚧 Phase 3: Additional Features (OPTIONAL)
1. **Leaderboard Services** - Redis-backed real-time rankings
2. **Profile Management** - Advanced user profile features
3. **Inventory System** - Item management and equipment
4. **Advanced Analytics** - Comprehensive user analytics
5. **Scalability** - Read replicas, advanced caching

## Development Guidelines

### Code Organization
- Keep repositories focused on data access only
- Implement business logic in service layer
- Use dependency injection for all external dependencies
- Maintain clear separation between API, business, and data layers

### Testing Strategy
- Unit tests for all service functions
- Integration tests for API endpoints
- Repository tests with database fixtures
- Performance tests for critical paths

### Security Considerations
- Validate all user inputs at API boundary
- Implement proper authentication middleware
- Use parameterized queries to prevent SQL injection
- Implement proper CORS and security headers

This architecture provides a solid foundation for a scalable, secure, and maintainable trivia RPG backend while clearly identifying what needs to be implemented to achieve full functionality.
