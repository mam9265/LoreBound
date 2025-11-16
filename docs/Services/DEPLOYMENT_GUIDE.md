# LoreBound Backend - Deployment Guide

## 🚀 Production Deployment

This guide covers deploying the LoreBound backend to production environments.

## 📋 Prerequisites

### System Requirements
- **Docker** 20.10+ and Docker Compose 2.0+
- **PostgreSQL** 15+ database
- **Redis** 7+ for caching and sessions
- **SSL/TLS** certificates for HTTPS
- **Domain name** with DNS configuration

### Infrastructure Components
- **Application Server**: FastAPI with Uvicorn
- **Database**: PostgreSQL with connection pooling
- **Cache Layer**: Redis for sessions and caching
- **Background Jobs**: Celery with Redis broker
- **Reverse Proxy**: Nginx (recommended)
- **Monitoring**: Health checks and metrics

## 🏗️ Architecture Diagram

```mermaid
graph TB
    subgraph "Load Balancer / CDN"
        LB[Nginx / CloudFlare]
    end
    
    subgraph "Application Tier"
        API1[FastAPI Instance 1]
        API2[FastAPI Instance 2]
        API3[FastAPI Instance 3]
    end
    
    subgraph "Background Jobs"
        WORKER1[Celery Worker 1]
        WORKER2[Celery Worker 2]
        BEAT[Celery Beat Scheduler]
    end
    
    subgraph "Data Tier"
        DB[(PostgreSQL Primary)]
        DBR[(PostgreSQL Replica)]
        REDIS[(Redis Cluster)]
    end
    
    subgraph "External Services"
        TRIVIA[Trivia APIs]
        APPLE[Apple Sign-In]
        MONITORING[Monitoring/Logs]
    end
    
    LB --> API1
    LB --> API2
    LB --> API3
    
    API1 --> DB
    API2 --> DB
    API3 --> DB
    
    API1 --> REDIS
    API2 --> REDIS
    API3 --> REDIS
    
    WORKER1 --> DB
    WORKER2 --> DB
    BEAT --> REDIS
    
    WORKER1 --> REDIS
    WORKER2 --> REDIS
    
    API1 --> TRIVIA
    API2 --> APPLE
    
    API1 --> MONITORING
    API2 --> MONITORING
    API3 --> MONITORING
```

## 🔧 Environment Configuration

### Production Environment Variables

Create a production `.env` file:

```bash
# Application Environment
APP_ENV=prod
DEBUG=false
API_HOST=0.0.0.0
API_PORT=8000

# Database Configuration
DATABASE_URL=postgresql+asyncpg://username:password@db-host:5432/lorebound_prod
DB_ECHO=false

# Redis Configuration
REDIS_URL=redis://redis-host:6379/0

# JWT Configuration
JWT_ALG=RS256
JWT_PRIVATE_KEY_PATH=/app/secrets/jwt_private.pem
JWT_PUBLIC_KEY_PATH=/app/secrets/jwt_public.pem
ACCESS_TOKEN_TTL_SECONDS=900
REFRESH_TOKEN_TTL_SECONDS=1209600

# Apple Sign-In Configuration
APPLE_TEAM_ID=YOUR_TEAM_ID
APPLE_CLIENT_ID=YOUR_CLIENT_ID
APPLE_KEY_ID=YOUR_KEY_ID
APPLE_PRIVATE_KEY_PATH=/app/secrets/apple_signin_key.p8

# Security Configuration
CORS_ORIGINS=["https://yourdomain.com","https://www.yourdomain.com"]
RATE_LIMIT_PER_MINUTE=60

# Background Jobs
CELERY_BROKER_URL=redis://redis-host:6379/1
CELERY_RESULT_BACKEND=redis://redis-host:6379/2

# Monitoring
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
LOG_LEVEL=INFO

# Game Configuration
FEATURE_FLAGS_SEED=1
CONTENT_VERSION=1
DAILY_CHALLENGE_RESET_HOUR=0
```

## 🐳 Docker Production Setup

### Production Docker Compose

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: lorebound_prod
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_prod_data:/var/lib/postgresql/data
      - ./backups:/backups
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER}"]
      interval: 30s
      timeout: 10s
      retries: 5
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes --maxmemory 512mb --maxmemory-policy allkeys-lru
    volumes:
      - redis_prod_data:/data
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 10s
      retries: 5
    restart: unless-stopped

  api:
    build: 
      context: .
      dockerfile: Dockerfile.prod
    environment:
      - APP_ENV=prod
      - DATABASE_URL=postgresql+asyncpg://${DB_USER}:${DB_PASSWORD}@db:5432/lorebound_prod
      - REDIS_URL=redis://redis:6379/0
      - CELERY_BROKER_URL=redis://redis:6379/1
      - CELERY_RESULT_BACKEND=redis://redis:6379/2
    volumes:
      - ./secrets:/app/secrets:ro
      - ./logs:/app/logs
    ports:
      - "8000:8000"
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/healthz"]
      interval: 30s
      timeout: 10s
      retries: 3
    restart: unless-stopped
    deploy:
      replicas: 3
      resources:
        limits:
          memory: 512M
          cpus: "0.5"

  worker:
    build: 
      context: .
      dockerfile: Dockerfile.prod
    command: celery -A app.jobs.worker worker --loglevel=info --concurrency=2
    environment:
      - APP_ENV=prod
      - DATABASE_URL=postgresql+asyncpg://${DB_USER}:${DB_PASSWORD}@db:5432/lorebound_prod
      - REDIS_URL=redis://redis:6379/0
      - CELERY_BROKER_URL=redis://redis:6379/1
      - CELERY_RESULT_BACKEND=redis://redis:6379/2
    volumes:
      - ./secrets:/app/secrets:ro
      - ./logs:/app/logs
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    restart: unless-stopped
    deploy:
      replicas: 2

  scheduler:
    build: 
      context: .
      dockerfile: Dockerfile.prod
    command: celery -A app.jobs.worker beat --loglevel=info
    environment:
      - APP_ENV=prod
      - DATABASE_URL=postgresql+asyncpg://${DB_USER}:${DB_PASSWORD}@db:5432/lorebound_prod
      - REDIS_URL=redis://redis:6379/0
      - CELERY_BROKER_URL=redis://redis:6379/1
      - CELERY_RESULT_BACKEND=redis://redis:6379/2
    volumes:
      - ./secrets:/app/secrets:ro
      - ./logs:/app/logs
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.prod.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
      - ./logs/nginx:/var/log/nginx
    depends_on:
      - api
    restart: unless-stopped

volumes:
  postgres_prod_data:
  redis_prod_data:
```

### Production Dockerfile

Create `Dockerfile.prod`:

```dockerfile
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV APP_ENV=prod

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create app user
RUN useradd --create-home --shell /bin/bash app

# Set work directory
WORKDIR /app

# Install Python dependencies
COPY pyproject.toml poetry.lock ./
RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --only=main --no-dev

# Copy application code
COPY --chown=app:app . .

# Create necessary directories
RUN mkdir -p logs secrets && \
    chown -R app:app /app

# Switch to app user
USER app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/healthz || exit 1

# Expose port
EXPOSE 8000

# Default command
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

## 🌐 Nginx Configuration

Create `nginx.prod.conf`:

```nginx
events {
    worker_connections 1024;
}

http {
    upstream lorebound_api {
        server api:8000;
    }

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=60r/m;
    limit_req_zone $binary_remote_addr zone=auth:10m rate=10r/m;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    server {
        listen 80;
        server_name yourdomain.com www.yourdomain.com;
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name yourdomain.com www.yourdomain.com;

        # SSL Configuration
        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;
        ssl_session_cache shared:SSL:1m;
        ssl_session_timeout 5m;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384;
        ssl_prefer_server_ciphers on;

        # API endpoints
        location /v1/ {
            limit_req zone=api burst=20 nodelay;
            proxy_pass http://lorebound_api;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Authentication endpoints (stricter rate limiting)
        location /v1/auth/ {
            limit_req zone=auth burst=5 nodelay;
            proxy_pass http://lorebound_api;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Health checks
        location /healthz {
            proxy_pass http://lorebound_api;
            access_log off;
        }

        # API documentation (optional in production)
        location /docs {
            auth_basic "API Documentation";
            auth_basic_user_file /etc/nginx/.htpasswd;
            proxy_pass http://lorebound_api;
        }
    }
}
```

## 🔐 Security Setup

### 1. Generate Production Secrets

```bash
# Generate JWT keys
openssl genrsa -out secrets/jwt_private.pem 2048
openssl rsa -in secrets/jwt_private.pem -pubout -out secrets/jwt_public.pem

# Set proper permissions
chmod 600 secrets/jwt_private.pem
chmod 644 secrets/jwt_public.pem
```

### 2. SSL Certificate Setup

```bash
# Using Let's Encrypt (recommended)
certbot certonly --webroot -w /var/www/html -d yourdomain.com -d www.yourdomain.com

# Copy certificates
cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem ssl/cert.pem
cp /etc/letsencrypt/live/yourdomain.com/privkey.pem ssl/key.pem
```

### 3. Database Security

```sql
-- Create production database user
CREATE USER lorebound_prod WITH PASSWORD 'strong_random_password';
CREATE DATABASE lorebound_prod OWNER lorebound_prod;

-- Grant necessary permissions
GRANT CONNECT ON DATABASE lorebound_prod TO lorebound_prod;
GRANT USAGE ON SCHEMA public TO lorebound_prod;
GRANT CREATE ON SCHEMA public TO lorebound_prod;
```

## 📊 Database Setup

### 1. Initial Migration

```bash
# Run database migrations
docker-compose -f docker-compose.prod.yml run --rm api alembic upgrade head

# Verify migration
docker-compose -f docker-compose.prod.yml run --rm api python -c "
from app.repositories.base import test_database_connection
import asyncio
print('Database connected:', asyncio.run(test_database_connection()))
"
```

### 2. Database Backup Strategy

```bash
# Create backup script
cat > scripts/backup_db.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/backups"
DB_NAME="lorebound_prod"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Create backup
docker-compose exec db pg_dump -U lorebound_prod -d $DB_NAME | gzip > "$BACKUP_DIR/backup_$TIMESTAMP.sql.gz"

# Keep only last 7 days of backups
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +7 -delete

echo "Backup completed: backup_$TIMESTAMP.sql.gz"
EOF

chmod +x scripts/backup_db.sh

# Setup daily backup cron
echo "0 2 * * * /path/to/project/scripts/backup_db.sh" | crontab -
```

## 🚀 Deployment Process

### 1. Pre-deployment Checklist

```bash
# Verify environment configuration
python scripts/validate_config.py

# Run tests
python -m pytest tests/

# Check Docker build
docker build -f Dockerfile.prod -t lorebound-backend:latest .

# Validate JWT keys
ls -la secrets/jwt_*.pem

# Test database connection
python -c "
import asyncio
from app.repositories.base import test_database_connection
print('DB Test:', asyncio.run(test_database_connection()))
"
```

### 2. Initial Deployment

```bash
# Deploy infrastructure
docker-compose -f docker-compose.prod.yml up -d db redis

# Wait for services to be ready
docker-compose -f docker-compose.prod.yml run --rm api python scripts/wait_for_services.py

# Run database migrations
docker-compose -f docker-compose.prod.yml run --rm api alembic upgrade head

# Start application services
docker-compose -f docker-compose.prod.yml up -d api worker scheduler nginx

# Verify deployment
curl -f https://yourdomain.com/healthz
```

### 3. Zero-Downtime Updates

```bash
# Build new image
docker build -f Dockerfile.prod -t lorebound-backend:v1.1.0 .

# Update docker-compose.prod.yml with new image tag
sed -i 's/lorebound-backend:latest/lorebound-backend:v1.1.0/' docker-compose.prod.yml

# Rolling update
docker-compose -f docker-compose.prod.yml up -d --no-deps api worker

# Verify update
curl -f https://yourdomain.com/healthz
```

## 📈 Monitoring Setup

### 1. Application Monitoring

```python
# Add to app/main.py
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

if settings.sentry_dsn:
    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        integrations=[FastApiIntegration()],
        traces_sample_rate=0.1,
        environment=settings.app_env
    )
```

### 2. Health Check Monitoring

```bash
# Create health check script
cat > scripts/health_monitor.sh << 'EOF'
#!/bin/bash
HEALTH_URL="https://yourdomain.com/healthz"
WEBHOOK_URL="your-slack-webhook-url"

if ! curl -f -s $HEALTH_URL > /dev/null; then
    curl -X POST -H 'Content-type: application/json' \
        --data '{"text":"🚨 LoreBound API health check failed!"}' \
        $WEBHOOK_URL
fi
EOF

chmod +x scripts/health_monitor.sh

# Run every 5 minutes
echo "*/5 * * * * /path/to/project/scripts/health_monitor.sh" | crontab -
```

### 3. Performance Monitoring

```bash
# Monitor API response times
docker-compose -f docker-compose.prod.yml logs -f api | grep "GET\|POST" > logs/api_access.log

# Monitor resource usage
docker stats --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}" > logs/resource_usage.log
```

## 🔧 Maintenance Tasks

### 1. Log Rotation

```bash
# Setup logrotate
cat > /etc/logrotate.d/lorebound << 'EOF'
/path/to/project/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    postrotate
        docker-compose -f /path/to/project/docker-compose.prod.yml restart api worker
    endscript
}
EOF
```

### 2. Database Maintenance

```sql
-- Weekly maintenance queries
VACUUM ANALYZE;
REINDEX DATABASE lorebound_prod;

-- Check for long-running queries
SELECT pid, now() - pg_stat_activity.query_start AS duration, query 
FROM pg_stat_activity 
WHERE (now() - pg_stat_activity.query_start) > interval '5 minutes';
```

### 3. Redis Maintenance

```bash
# Redis memory usage check
redis-cli info memory

# Clear expired keys
redis-cli --scan --pattern "session:*" | xargs redis-cli del
```

## 📋 Troubleshooting

### Common Issues

1. **Database Connection Errors**
   ```bash
   # Check database connectivity
   docker-compose -f docker-compose.prod.yml exec db pg_isready -U lorebound_prod
   
   # Check connection pool
   docker-compose -f docker-compose.prod.yml logs api | grep "pool"
   ```

2. **JWT Token Issues**
   ```bash
   # Verify JWT keys
   openssl rsa -in secrets/jwt_private.pem -check
   openssl rsa -in secrets/jwt_private.pem -pubout | diff - secrets/jwt_public.pem
   ```

3. **High Memory Usage**
   ```bash
   # Check for memory leaks
   docker stats --no-stream
   
   # Restart services if needed
   docker-compose -f docker-compose.prod.yml restart api worker
   ```

4. **Slow API Responses**
   ```bash
   # Check database query performance
   docker-compose -f docker-compose.prod.yml exec db psql -U lorebound_prod -c "
   SELECT query, mean_exec_time, calls 
   FROM pg_stat_statements 
   ORDER BY mean_exec_time DESC 
   LIMIT 10;"
   ```

### Emergency Procedures

1. **Service Restart**
   ```bash
   docker-compose -f docker-compose.prod.yml restart api worker scheduler
   ```

2. **Database Rollback**
   ```bash
   # Restore from backup
   gunzip -c /backups/backup_YYYYMMDD_HHMMSS.sql.gz | \
   docker-compose exec -T db psql -U lorebound_prod -d lorebound_prod
   ```

3. **Scale Services**
   ```bash
   # Increase API replicas
   docker-compose -f docker-compose.prod.yml up -d --scale api=5
   
   # Increase worker replicas
   docker-compose -f docker-compose.prod.yml up -d --scale worker=4
   ```

## ✅ Post-Deployment Verification

```bash
# 1. Health checks
curl -f https://yourdomain.com/healthz
curl -f https://yourdomain.com/healthz/detailed

# 2. API functionality
curl -X POST https://yourdomain.com/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"TestPass123!","handle":"TestUser"}'

# 3. Background jobs
docker-compose -f docker-compose.prod.yml logs scheduler | grep "beat"

# 4. Database connectivity
docker-compose -f docker-compose.prod.yml exec api python -c "
import asyncio
from app.repositories.base import test_database_connection
print('Database OK:', asyncio.run(test_database_connection()))
"

# 5. Redis connectivity
docker-compose -f docker-compose.prod.yml exec redis redis-cli ping
```

This deployment guide ensures a robust, secure, and scalable production environment for the LoreBound backend.
