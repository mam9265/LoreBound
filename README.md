# LoreBound - Trivia RPG Game

[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![React Native](https://img.shields.io/badge/React_Native-0.81+-blue.svg)](https://reactnative.dev)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-blue.svg)](https://postgresql.org)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://docker.com)

A full-stack trivia RPG game with a React Native mobile app and FastAPI backend, featuring user authentication, content management, game runs, and leaderboards.

## 🎮 About LoreBound

LoreBound is an innovative trivia RPG that combines knowledge-based gameplay with role-playing game elements. Players progress through themed dungeons, answer trivia questions, collect items, and compete on leaderboards.

---

## ⚡ TL;DR - Quick Start for Experienced Developers

```bash
# 1. Backend (Terminal 1)
cd lorebound-backend
mkdir -p secrets
openssl genrsa -out secrets/jwt_private.pem 2048
openssl rsa -in secrets/jwt_private.pem -pubout -out secrets/jwt_public.pem
docker-compose up -d
docker-compose --profile migration run --rm migrate

# 2. Mobile App (Terminal 2)
cd lorebound
npm install
npm start

# 3. Run App (Terminal 3 - after Metro starts)
cd lorebound
npm run android  # or npm run ios (macOS only)
```

**Verify**: Backend at http://localhost:8000/docs | App launches on emulator

**Note**: Make sure Docker Desktop and Android Studio (with AVD) are running before starting.

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

## 🚀 How to Run the Entire Application

This guide will walk you through running both the **backend** (FastAPI) and the **mobile app** (React Native) for local development and testing.

### Prerequisites

Before you begin, ensure you have the following installed:

#### For Backend:
- **Docker Desktop** (includes Docker & Docker Compose) - [Download](https://www.docker.com/products/docker-desktop)
- **Python 3.11+** (optional, for local development without Docker)

#### For Mobile App:
- **Node.js 20+** - [Download](https://nodejs.org/)
- **npm** or **yarn** (comes with Node.js)
- **Android Studio** (for Android development) - [Download](https://developer.android.com/studio)
  - Make sure to install Android SDK and create an Android Virtual Device (AVD)
  - Recommended: **Pixel 9 Pro XL** emulator
- **Xcode** (for iOS development, macOS only) - [Download from App Store](https://apps.apple.com/us/app/xcode/id497799835)
- **React Native CLI** (will be installed via npx)

---

## 📦 Part 1: Running the Backend

### Step 1: Navigate to the Backend Directory

```bash
cd lorebound-backend
```

### Step 2: Generate JWT Keys

The backend requires JWT keys for authentication. Generate them with OpenSSL:

```bash
# Create secrets directory if it doesn't exist
mkdir -p secrets

# Generate RSA private key
openssl genrsa -out secrets/jwt_private.pem 2048

# Generate public key from private key
openssl rsa -in secrets/jwt_private.pem -pubout -out secrets/jwt_public.pem
```

### Step 3: Start Backend Services with Docker

Start all backend services (PostgreSQL, Redis, API server, Celery worker):

```bash
docker-compose up -d
```

This will start:
- **PostgreSQL database** on port `5433`
- **Redis** on port `6379`
- **FastAPI server** on port `8000`
- **Celery worker** for background jobs

### Step 4: Run Database Migrations

Initialize the database schema:

```bash
docker-compose --profile migration run --rm migrate
```

### Step 5: Verify Backend is Running

Open your browser and check these URLs:
- **API Documentation (Swagger)**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/healthz
- **API Base URL**: http://localhost:8000/v1

You should see the API documentation and a healthy status.

### Optional: Seed Sample Data

To populate the database with sample content:

```bash
docker-compose exec api poetry run python scripts/seed_content_data.py
```

---

## 📱 Part 2: Running the Mobile App

### Step 1: Navigate to the Mobile App Directory

Open a **new terminal window** (keep the backend running) and navigate to the mobile app:

```bash
cd lorebound
```

### Step 2: Install Dependencies

Install all required npm packages:

```bash
npm install
```

### Step 3: Configure Backend Connection

The mobile app is already configured to connect to your local backend:
- ✅ **Android emulator**: Uses `http://10.0.2.2:8000` automatically
- ✅ **iOS simulator**: Uses `http://localhost:8000` automatically

**Only edit if using a physical device**:

If testing on a real Android/iOS device, update `lorebound/src/config/config.js`:

```javascript
// Find your computer's local IP address
// Windows: ipconfig
// macOS/Linux: ifconfig

// Replace the return statement with your IP:
return 'http://192.168.x.x:8000';  // Replace with your actual IP
```

### Step 4: Start Metro Bundler

Start the React Native Metro bundler:

```bash
npm start
```

Keep this terminal running. You should see the Metro bundler running.

### Step 5: Run the App

Open **another terminal window** in the `lorebound` directory and run:

#### For Android:

**Option A: Using Android Emulator**
1. Open Android Studio
2. Start your Android Virtual Device (AVD) - Recommended: **Pixel 9 Pro XL**
3. Run the app:
   ```bash
   npm run android
   ```


```
---

## ✅ Verification

### Backend Verification

1. **Check API Health**: Visit http://localhost:8000/healthz
2. **Test Registration**:
   ```bash
   curl -X POST http://localhost:8000/v1/auth/register \
     -H "Content-Type: application/json" \
     -d '{"email":"test@example.com","password":"Test1234!","display_name":"TestUser"}'
   ```

### Mobile App Verification

1. The app should launch on your emulator/simulator
2. You should see the authentication screen
3. Try registering a new user or logging in
4. Navigate through the app menus

---

## 🛠️ Troubleshooting

### Backend Issues

**Port Already in Use**:
```bash
# Stop all containers
docker-compose down

# Check what's using the port
# Windows PowerShell:
netstat -ano | findstr :8000

# Kill the process using the port (replace PID with actual process ID)
taskkill /PID <PID> /F

# Restart
docker-compose up -d
```

**Database Connection Failed**:
```bash
# Check database is running
docker-compose ps

# View logs
docker-compose logs db

# Restart services
docker-compose restart
```

**JWT Key Issues**:
- Make sure you generated the JWT keys in `lorebound-backend/secrets/`
- Check file permissions if on macOS/Linux

### Mobile App Issues

**Metro Bundler Issues**:
```bash
# Clear cache
npm start -- --reset-cache
```

**Android Build Errors**:
```bash
# Clean build
cd android
./gradlew clean
cd ..

# Rebuild
npm run android
```

**Cannot Connect to Backend**:
- Verify backend is running at http://localhost:8000/healthz
- Check `src/config/config.js` has the correct IP address
- For Android emulator, use `10.0.2.2` instead of `localhost`
- For physical devices, use your computer's local network IP



**Node Modules Issues**:
```bash
# Remove and reinstall
rm -rf node_modules package-lock.json
npm install
```

---

## 🔧 Development Workflow

### Making Backend Changes

1. Edit files in `lorebound-backend/app/`
2. Changes are automatically reloaded (Docker volume mapping)
3. View logs: `docker-compose logs -f api`

### Making Mobile App Changes

1. Edit files in `lorebound/src/`
2. Save the file
3. Metro bundler will automatically reload
4. Shake device/emulator and select "Reload" if needed

### Stopping the Application

**Backend**:
```bash
cd lorebound-backend
docker-compose down
```

**Mobile App**:
- Press `Ctrl+C` in the Metro bundler terminal
- Close the emulator/simulator

---

## 📚 Additional Resources

- **Backend Documentation**: See `lorebound-backend/README.md`
- **API Documentation**: http://localhost:8000/docs (when running)
- **Architecture Overview**: See `docs/ARCHITECTURE_OVERVIEW.md`
- **Project Structure**: See `docs/PROJECT_STRUCTURE.md`
- **React Native Docs**: https://reactnative.dev/docs/getting-started

---

## 🎯 Quick Reference Commands

### Backend
```bash
# Start backend
cd lorebound-backend && docker-compose up -d

# View logs
docker-compose logs -f api

# Run migrations
docker-compose --profile migration run --rm migrate

# Stop backend
docker-compose down
```

### Mobile App
```bash
# Start Metro
cd lorebound && npm start

# Run Android (new terminal)
npm run android

# Run iOS (new terminal, macOS only)
npm run ios
```

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



