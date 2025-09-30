# LoreBound Backend - API Documentation

## 📋 Table of Contents
- [Authentication](#authentication)
- [Content Management](#content-management)
- [Game Runs](#game-runs)
- [User Management](#user-management)
- [Leaderboards](#leaderboards)
- [System Health](#system-health)
- [Error Handling](#error-handling)
- [Rate Limiting](#rate-limiting)

## 🔐 Authentication

All authenticated endpoints require a Bearer token in the Authorization header:
```
Authorization: Bearer <jwt_token>
```

### Register User
```http
POST /v1/auth/register
Content-Type: application/json

{
  "email": "player@example.com",
  "password": "SecurePassword123!",
  "handle": "AwesomePlayer"
}
```

**Response (201 Created):**
```json
{
  "tokens": {
    "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 900
  },
  "user": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "email": "player@example.com",
    "apple_sub": null,
    "status": "active",
    "created_at": "2024-01-01T00:00:00Z",
    "last_login_at": "2024-01-01T12:00:00Z"
  }
}
```

### Login User
```http
POST /v1/auth/login
Content-Type: application/json

{
  "email": "player@example.com",
  "password": "SecurePassword123!"
}
```

**Response (200 OK):**
```json
{
  "tokens": {
    "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 900
  },
  "user": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "email": "player@example.com",
    "status": "active"
  }
}
```

### Apple Sign-In
```http
POST /v1/auth/apple
Content-Type: application/json

{
  "identity_token": "eyJraWQiOiJBNklVUkwiLCJhbGciOiJSUzI1NiJ9...",
  "handle": "ApplePlayer"
}
```

### Refresh Token
```http
POST /v1/auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### Get Current User
```http
GET /v1/auth/me
Authorization: Bearer <token>
```

### Logout
```http
POST /v1/auth/logout
Authorization: Bearer <token>
```

## 🎯 Content Management

### Get Dungeons
```http
GET /v1/content/dungeons
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Ancient History Depths",
    "category": "history",
    "tier_count": 10,
    "metadata": {
      "description": "Journey through ancient civilizations",
      "difficulty": "medium",
      "estimated_duration": "15-20 minutes"
    },
    "tiers": [
      {
        "id": "660e8400-e29b-41d4-a716-446655440000",
        "floor": 1,
        "boss_metadata": {
          "name": "Guardian of Knowledge",
          "description": "Ancient keeper of historical wisdom"
        }
      }
    ]
  }
]
```

### Get Dungeon Details
```http
GET /v1/content/dungeons/{dungeon_id}
Authorization: Bearer <token>
```

### Get Questions
```http
GET /v1/content/questions?dungeon_id={uuid}&floor={int}&count={int}
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "questions": [
    {
      "id": "770e8400-e29b-41d4-a716-446655440000",
      "prompt": "Which ancient civilization built the pyramids of Giza?",
      "choices": [
        "Romans",
        "Egyptians",
        "Greeks",
        "Babylonians"
      ],
      "difficulty": "easy",
      "tags": ["history", "ancient", "egypt"],
      "metadata": {
        "source": "trivia_api",
        "verified": true
      }
    }
  ],
  "metadata": {
    "dungeon_id": "550e8400-e29b-41d4-a716-446655440000",
    "floor": 1,
    "total_questions": 10,
    "seed": 12345
  }
}
```

### Get Daily Challenge
```http
GET /v1/content/daily
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "id": "880e8400-e29b-41d4-a716-446655440000",
  "date": "2024-01-15",
  "dungeon": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Daily Knowledge Quest",
    "category": "mixed"
  },
  "modifiers": {
    "time_pressure": true,
    "bonus_xp": 1.5
  },
  "expires_at": "2024-01-16T00:00:00Z",
  "metadata": {
    "theme": "World Geography",
    "estimated_duration": "10 minutes"
  }
}
```

### Refresh Question Pool (Admin)
```http
POST /v1/content/refresh-questions?category={string}&batch_size={int}
Authorization: Bearer <admin_token>
```

## 🎮 Game Runs

### Start New Run
```http
POST /v1/runs/start
Authorization: Bearer <token>
Content-Type: application/json

{
  "dungeon_id": "550e8400-e29b-41d4-a716-446655440000",
  "is_daily_challenge": false,
  "modifiers": {
    "difficulty": "normal",
    "time_limit": 300
  }
}
```

**Response (201 Created):**
```json
{
  "id": "990e8400-e29b-41d4-a716-446655440000",
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "dungeon_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "in_progress",
  "seed": 42,
  "started_at": "2024-01-15T14:30:00Z",
  "anti_cheat_token": "abc123def456...",
  "metadata": {
    "total_floors": 10,
    "current_floor": 1,
    "time_limit": 300
  }
}
```

### Submit Run
```http
POST /v1/runs/{run_id}/submit
Authorization: Bearer <token>
Content-Type: application/json

{
  "scores": [
    {
      "floor": 1,
      "correct_answers": 8,
      "total_questions": 10,
      "time_taken_ms": 45000,
      "streak": 5,
      "points": 850
    }
  ],
  "turns": [
    {
      "question_id": "770e8400-e29b-41d4-a716-446655440000",
      "answer_index": 1,
      "time_taken_ms": 4500,
      "correct": true
    }
  ],
  "client_signature": "def789ghi012...",
  "completion_time": "2024-01-15T14:45:00Z"
}
```

**Response (200 OK):**
```json
{
  "id": "990e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "final_score": 8500,
  "total_time_ms": 900000,
  "floors_completed": 10,
  "accuracy": 0.85,
  "ranking": {
    "global_rank": 42,
    "percentile": 95.5
  },
  "rewards": {
    "xp_gained": 150,
    "items_earned": [
      {
        "id": "item123",
        "name": "Scholar's Badge",
        "rarity": "rare"
      }
    ]
  }
}
```

### Get User Runs
```http
GET /v1/runs/?limit={int}&offset={int}&status={string}
Authorization: Bearer <token>
```

### Get Run Details
```http
GET /v1/runs/{run_id}
Authorization: Bearer <token>
```

### Abandon Run
```http
POST /v1/runs/{run_id}/abandon
Authorization: Bearer <token>
```

### Get User Statistics
```http
GET /v1/runs/stats/me
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "total_runs": 25,
  "completed_runs": 23,
  "average_score": 7250,
  "best_score": 9500,
  "total_playtime_minutes": 420,
  "favorite_category": "history",
  "accuracy_rate": 0.83,
  "current_streak": 5,
  "longest_streak": 12,
  "achievements_unlocked": 8,
  "rank_progression": {
    "current_rank": "Scholar",
    "next_rank": "Expert",
    "progress": 0.65
  }
}
```

## 👤 User Management

### Get User Profile
```http
GET /v1/profile/
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "handle": "AwesomePlayer",
  "level": 15,
  "xp": 2250,
  "avatar_layers": {
    "base": "scholar",
    "accessory": "glasses",
    "background": "library"
  },
  "stats": {
    "total_runs": 25,
    "best_score": 9500,
    "favorite_category": "history"
  },
  "achievements": [
    {
      "id": "first_win",
      "name": "First Victory",
      "unlocked_at": "2024-01-10T15:30:00Z"
    }
  ]
}
```

### Update Profile
```http
PUT /v1/profile/
Authorization: Bearer <token>
Content-Type: application/json

{
  "handle": "NewAwesomePlayer",
  "avatar_layers": {
    "base": "wizard",
    "accessory": "staff",
    "background": "castle"
  }
}
```

### Get User Inventory
```http
GET /v1/inventory/
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "items": [
    {
      "id": "item123",
      "name": "Scholar's Badge",
      "slot": "accessory",
      "rarity": "rare",
      "equipped": true,
      "acquired_at": "2024-01-15T14:45:00Z",
      "stats": {
        "knowledge_boost": 10,
        "time_bonus": 5
      }
    }
  ],
  "total_items": 12,
  "equipped_items": {
    "weapon": "item456",
    "armor": "item789",
    "accessory": "item123"
  }
}
```

### Equip Item
```http
POST /v1/inventory/equip
Authorization: Bearer <token>
Content-Type: application/json

{
  "item_id": "item123",
  "slot": "accessory"
}
```

## 🏆 Leaderboards

### Get Global Leaderboards
```http
GET /v1/leaderboards/?scope={string}&period={string}&limit={int}&offset={int}
Authorization: Bearer <token>
```

**Query Parameters:**
- `scope`: `global`, `friends`, `guild`
- `period`: `daily`, `weekly`, `monthly`, `all_time`
- `limit`: Number of entries (default: 50, max: 100)
- `offset`: Pagination offset

**Response (200 OK):**
```json
{
  "leaderboard": [
    {
      "rank": 1,
      "user": {
        "id": "456e7890-e29b-41d4-a716-446655440000",
        "handle": "TopPlayer",
        "level": 25
      },
      "score": 15000,
      "runs_completed": 50,
      "accuracy": 0.92,
      "metadata": {
        "streak": 20,
        "favorite_category": "science"
      }
    }
  ],
  "metadata": {
    "scope": "global",
    "period": "weekly",
    "total_entries": 1500,
    "last_updated": "2024-01-15T12:00:00Z"
  }
}
```

### Get User Rank
```http
GET /v1/leaderboards/me?scope={string}&period={string}
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "current_rank": 42,
  "score": 8500,
  "percentile": 95.5,
  "neighbors": [
    {
      "rank": 40,
      "handle": "PlayerAbove2",
      "score": 8650
    },
    {
      "rank": 41,
      "handle": "PlayerAbove1",
      "score": 8575
    },
    {
      "rank": 42,
      "handle": "AwesomePlayer",
      "score": 8500,
      "is_current_user": true
    },
    {
      "rank": 43,
      "handle": "PlayerBelow1",
      "score": 8425
    },
    {
      "rank": 44,
      "handle": "PlayerBelow2",
      "score": 8350
    }
  ]
}
```

## 🏥 System Health

### Basic Health Check
```http
GET /healthz
```

**Response (200 OK):**
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "environment": "production",
  "database": "connected",
  "database_info": {
    "database": "lorebound",
    "active_connections": 5
  }
}
```

### Detailed Health Check
```http
GET /healthz/detailed
```

**Response (200 OK):**
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "environment": "production",
  "timestamp": "2024-01-15T14:30:00Z",
  "database": {
    "connected": true,
    "info": {
      "version": "PostgreSQL 15.0",
      "database": "lorebound",
      "active_connections": 5,
      "pool_size": 10
    }
  },
  "configuration": {
    "valid": true,
    "errors": [],
    "warnings": []
  },
  "jwt": {
    "algorithm": "RS256",
    "keys_loaded": true
  }
}
```

### Metrics (Prometheus)
```http
GET /metrics
```

## ⚠️ Error Handling

All API errors follow this format:

```json
{
  "detail": "Error description",
  "error_code": "SPECIFIC_ERROR_CODE",
  "timestamp": "2024-01-15T14:30:00Z",
  "path": "/v1/auth/login"
}
```

### Common HTTP Status Codes

- **200 OK**: Successful request
- **201 Created**: Resource created successfully
- **400 Bad Request**: Invalid request data
- **401 Unauthorized**: Authentication required
- **403 Forbidden**: Insufficient permissions
- **404 Not Found**: Resource not found
- **409 Conflict**: Resource conflict (e.g., email already exists)
- **422 Unprocessable Entity**: Validation errors
- **429 Too Many Requests**: Rate limit exceeded
- **500 Internal Server Error**: Server error

### Validation Errors (422)
```json
{
  "detail": [
    {
      "type": "string_too_short",
      "loc": ["body", "password"],
      "msg": "String should have at least 8 characters",
      "input": "123",
      "ctx": {"min_length": 8}
    }
  ]
}
```

## 🚦 Rate Limiting

Default rate limits (per minute):
- **Authentication endpoints**: 10 requests
- **Content endpoints**: 60 requests  
- **Game run endpoints**: 30 requests
- **Other endpoints**: 100 requests

Rate limit headers included in responses:
```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 59
X-RateLimit-Reset: 1642248000
```

## 🔐 Security Notes

1. **JWT Tokens**: Include user ID and expiration time
2. **Password Requirements**: Minimum 8 characters, maximum 128
3. **Email Validation**: RFC-compliant email format required
4. **Handle Requirements**: 3-50 characters, unique per user
5. **CORS**: Configured for allowed origins only
6. **Anti-Cheat**: Cryptographic signatures for game runs

## 📱 Client Integration Examples

### Authentication Flow
```javascript
// Register user
const registerResponse = await fetch('/v1/auth/register', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'player@example.com',
    password: 'SecurePassword123!',
    handle: 'AwesomePlayer'
  })
});

const { tokens, user } = await registerResponse.json();
localStorage.setItem('access_token', tokens.access_token);
localStorage.setItem('refresh_token', tokens.refresh_token);

// Use token for authenticated requests
const profileResponse = await fetch('/v1/profile/', {
  headers: {
    'Authorization': `Bearer ${tokens.access_token}`
  }
});
```

### Game Run Flow
```javascript
// Start game run
const startResponse = await fetch('/v1/runs/start', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${accessToken}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    dungeon_id: 'dungeon-uuid',
    is_daily_challenge: false
  })
});

const run = await startResponse.json();

// Get questions for the run
const questionsResponse = await fetch(
  `/v1/content/questions?dungeon_id=${run.dungeon_id}&floor=1&count=10`,
  {
    headers: { 'Authorization': `Bearer ${accessToken}` }
  }
);

// Submit completed run
const submitResponse = await fetch(`/v1/runs/${run.id}/submit`, {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${accessToken}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    scores: [/* score data */],
    turns: [/* turn data */],
    client_signature: run.anti_cheat_token
  })
});
```
