# API Quick Reference - Sprint Features

Quick reference for all API endpoints needed for Dungeon Runs, Leaderboard, and Character Customization features.

---

## 🎮 Dungeon Runs API

### Start Run
```http
POST /v1/runs/start
Authorization: Bearer {token}
Content-Type: application/json

Request Body:
{
  "dungeon_id": "uuid",
  "floor": 1,
  "client_metadata": {
    "device": "iOS",
    "version": "1.0.0"
  }
}

Response (201):
{
  "id": "uuid",
  "user_id": "uuid",
  "dungeon_id": "uuid",
  "floor": 1,
  "status": "in_progress",
  "session_token": "encrypted_token",
  "total_score": null,
  "started_at": "2025-10-26T12:00:00Z",
  "completed_at": null
}
```

**Status:** ✅ EXISTS

---

### Submit Run
```http
POST /v1/runs/{run_id}/submit
Authorization: Bearer {token}
Content-Type: application/json

Request Body:
{
  "turn_data": [
    {
      "i": 0,
      "qid": "question_uuid",
      "a": 2,
      "c": true,
      "t": 1820,
      "ts": 1699999990000,
      "h": "hmac_signature"
    }
  ],
  "scores": [
    {
      "points": 100,
      "answer_time": 1.82,
      "is_correct": true,
      "streak_bonus": 10,
      "time_bonus": 5
    }
  ],
  "client_signature": "aggregate_signature"
}

Response (200):
{
  "id": "uuid",
  "user_id": "uuid",
  "dungeon_id": "uuid",
  "floor": 3,
  "status": "completed",
  "session_token": "token",
  "total_score": 1850,
  "started_at": "2025-10-26T12:00:00Z",
  "completed_at": "2025-10-26T12:15:30Z"
}
```

**Status:** ✅ EXISTS

---

### Get User Runs (History)
```http
GET /v1/runs?limit=20&offset=0
Authorization: Bearer {token}

Response (200):
[
  {
    "id": "uuid",
    "user_id": "uuid",
    "dungeon_id": "uuid",
    "floor": 3,
    "status": "completed",
    "total_score": 1850,
    "started_at": "2025-10-26T12:00:00Z",
    "completed_at": "2025-10-26T12:15:30Z"
  }
]
```

**Status:** ✅ EXISTS

---

### Get Specific Run
```http
GET /v1/runs/{run_id}
Authorization: Bearer {token}

Response (200):
{
  "id": "uuid",
  "user_id": "uuid",
  "dungeon_id": "uuid",
  "floor": 3,
  "status": "completed",
  "session_token": "token",
  "total_score": 1850,
  "started_at": "2025-10-26T12:00:00Z",
  "completed_at": "2025-10-26T12:15:30Z"
}
```

**Status:** ✅ EXISTS

---

### Abandon Run
```http
POST /v1/runs/{run_id}/abandon
Authorization: Bearer {token}

Response (200):
{
  "id": "uuid",
  "status": "abandoned",
  "started_at": "2025-10-26T12:00:00Z",
  "completed_at": "2025-10-26T12:05:00Z"
}
```

**Status:** ✅ EXISTS

---

### Get User Stats
```http
GET /v1/runs/stats/me
Authorization: Bearer {token}

Response (200):
{
  "total_runs": 25,
  "total_score": 42500,
  "average_score": 1700.0,
  "best_score": 2350,
  "total_correct": 485,
  "total_questions": 600,
  "accuracy_percentage": 80.83
}
```

**Status:** ✅ EXISTS

---

## 🏆 Leaderboard API

### Get Leaderboard
```http
GET /v1/leaderboards?scope=alltime&limit=100&offset=0
Authorization: Bearer {token}

Query Parameters:
- scope: "today" | "weekly" | "alltime" (default: "alltime")
- limit: 1-100 (default: 100)
- offset: 0+ (default: 0)

Response (200):
{
  "scope": "alltime",
  "period_key": "2025",
  "total_participants": 1247,
  "entries": [
    {
      "rank": 1,
      "user_id": "uuid",
      "handle": "Astra",
      "score": 9876,
      "total_runs": 142,
      "avatar_layers": {...}
    },
    {
      "rank": 2,
      "user_id": "uuid",
      "handle": "Kane",
      "score": 9530,
      "total_runs": 120,
      "avatar_layers": {...}
    }
  ],
  "last_updated": "2025-10-26T12:00:00Z"
}
```

**Status:** 🔨 NEEDS IMPLEMENTATION

**File to create:** `lorebound-backend/app/api/v1/routers/leaderboards.py`

---

### Get User Rank
```http
GET /v1/leaderboards/me?scope=alltime
Authorization: Bearer {token}

Query Parameters:
- scope: "today" | "weekly" | "alltime" (default: "alltime")

Response (200):
{
  "user_id": "uuid",
  "handle": "YourName",
  "rank": 42,
  "score": 2340,
  "total_runs": 15,
  "scope": "alltime",
  "period_key": "2025",
  "neighbors": [
    {
      "rank": 40,
      "handle": "Player40",
      "score": 2398
    },
    {
      "rank": 41,
      "handle": "Player41",
      "score": 2361
    },
    {
      "rank": 43,
      "handle": "Player43",
      "score": 2325
    }
  ]
}
```

**Status:** 🔨 NEEDS IMPLEMENTATION

---

### Get Leaderboard Stats
```http
GET /v1/leaderboards/stats?scope=alltime
Authorization: Bearer {token}

Query Parameters:
- scope: "today" | "weekly" | "alltime" (default: "alltime")

Response (200):
{
  "scope": "alltime",
  "period_key": "2025",
  "participants": 1247,
  "total_scores": 3542,
  "average_score": 1683.4,
  "highest_score": 9876,
  "lowest_score": 120,
  "last_updated": "2025-10-26T12:00:00Z"
}
```

**Status:** 🔨 NEEDS IMPLEMENTATION

---

## 🎨 Character Customization API

### Get User Profile
```http
GET /v1/profile
Authorization: Bearer {token}

Response (200):
{
  "user_id": "uuid",
  "handle": "YourName",
  "level": 12,
  "xp": 3450,
  "avatar_layers": {
    "helmet": "iron_helm",
    "armor": "chainmail",
    "weapon": "battle_axe",
    "shield": "iron_shield"
  },
  "equipped_items": [
    {
      "id": "uuid",
      "slug": "iron_helm",
      "name": "Iron Helm",
      "slot": "helmet",
      "rarity": "common",
      "stats": {
        "defense": 5,
        "weight": 2
      }
    }
  ]
}
```

**Status:** 🔨 NEEDS IMPLEMENTATION

**File to create:** `lorebound-backend/app/api/v1/routers/profile.py`

---

### Update Avatar Customization
```http
PUT /v1/profile/avatar
Authorization: Bearer {token}
Content-Type: application/json

Request Body:
{
  "avatar_layers": {
    "helmet": "iron_helm",
    "armor": "chainmail",
    "weapon": "battle_axe",
    "shield": "iron_shield",
    "colors": {
      "primary": "#FF5733",
      "secondary": "#3357FF"
    }
  }
}

Response (200):
{
  "user_id": "uuid",
  "avatar_layers": {...},
  "updated_at": "2025-10-26T12:00:00Z"
}
```

**Status:** 🔨 NEEDS IMPLEMENTATION

---

### Get User Inventory
```http
GET /v1/inventory/items
Authorization: Bearer {token}

Response (200):
{
  "items": [
    {
      "id": "uuid",
      "slug": "iron_helm",
      "name": "Iron Helm",
      "slot": "helmet",
      "rarity": "common",
      "stats": {
        "defense": 5,
        "weight": 2
      },
      "equipped": true,
      "acquired_at": "2025-10-20T10:00:00Z"
    },
    {
      "id": "uuid",
      "slug": "leather_cap",
      "name": "Leather Cap",
      "slot": "helmet",
      "rarity": "common",
      "stats": {
        "defense": 2,
        "weight": 1
      },
      "equipped": false,
      "acquired_at": "2025-10-19T08:00:00Z"
    }
  ],
  "total_items": 15,
  "slots": {
    "helmet": 3,
    "armor": 4,
    "weapon": 5,
    "shield": 3
  }
}
```

**Status:** 🔨 NEEDS IMPLEMENTATION

---

### Equip Item
```http
POST /v1/inventory/equip
Authorization: Bearer {token}
Content-Type: application/json

Request Body:
{
  "item_id": "uuid",
  "slot": "helmet"
}

Response (200):
{
  "item_id": "uuid",
  "slot": "helmet",
  "equipped": true,
  "previously_equipped": {
    "item_id": "old_uuid",
    "name": "Leather Cap"
  }
}
```

**Status:** ⚠️ PARTIALLY EXISTS (needs updating)

**File:** `lorebound-backend/app/api/v1/routers/inventory.py`

---

### Unequip Item
```http
POST /v1/inventory/unequip
Authorization: Bearer {token}
Content-Type: application/json

Request Body:
{
  "slot": "helmet"
}

Response (200):
{
  "slot": "helmet",
  "equipped": false,
  "unequipped_item": {
    "item_id": "uuid",
    "name": "Iron Helm"
  }
}
```

**Status:** 🔨 NEEDS IMPLEMENTATION

---

### Get Available Items (Shop/Catalog)
```http
GET /v1/inventory/available?slot=helmet&rarity=rare
Authorization: Bearer {token}

Query Parameters:
- slot: "helmet" | "armor" | "weapon" | "shield" (optional)
- rarity: "common" | "rare" | "epic" | "legendary" (optional)

Response (200):
{
  "items": [
    {
      "id": "uuid",
      "slug": "dragon_helm",
      "name": "Dragon Helm",
      "slot": "helmet",
      "rarity": "epic",
      "stats": {
        "defense": 15,
        "weight": 5,
        "fire_resistance": 10
      },
      "unlock_requirements": {
        "level": 15,
        "achievement": "dragon_slayer"
      },
      "unlocked": false
    }
  ]
}
```

**Status:** 🔨 NEEDS IMPLEMENTATION

---

## 📦 Content API (Existing - For Reference)

### Get Dungeons
```http
GET /v1/content/dungeons
Authorization: Bearer {token}

Response (200):
[
  {
    "id": "uuid",
    "title": "Sports Dungeon",
    "category": "sports",
    "modifiers": {...},
    "content_version": 1
  }
]
```

**Status:** ✅ EXISTS

---

### Get Questions
```http
GET /v1/content/questions?dungeon_id=uuid&seed=12345&count=10
Authorization: Bearer {token}

Query Parameters:
- dungeon_id: UUID (required)
- seed: integer (optional, for deterministic questions)
- count: 1-50 (default: 10)

Response (200):
[
  {
    "id": "uuid",
    "prompt": "What year did the first Super Bowl take place?",
    "choices": ["1965", "1967", "1970", "1972"],
    "answer_index": 1,
    "difficulty": "medium",
    "tags": ["football", "history"]
  }
]
```

**Status:** ✅ EXISTS

---

### Get Daily Challenge
```http
GET /v1/content/daily
Authorization: Bearer {token}

Response (200):
{
  "id": "uuid",
  "date": "2025-10-26",
  "seed": 67890,
  "dungeon_id": "uuid",
  "dungeon": {
    "id": "uuid",
    "title": "Music Dungeon",
    "category": "music"
  },
  "modifiers": {
    "time_limit": 10,
    "bonus_multiplier": 1.5
  },
  "expires_at": "2025-10-27T00:00:00Z"
}
```

**Status:** ✅ EXISTS

---

## 🔐 Authentication API (Existing - For Reference)

### Register
```http
POST /v1/auth/register
Content-Type: application/json

Request Body:
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "handle": "PlayerName"
}

Response (201):
{
  "access_token": "jwt_token",
  "refresh_token": "refresh_token",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "profile": {
      "handle": "PlayerName",
      "level": 1,
      "xp": 0
    }
  }
}
```

**Status:** ✅ EXISTS

---

### Login
```http
POST /v1/auth/login
Content-Type: application/json

Request Body:
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}

Response (200):
{
  "access_token": "jwt_token",
  "refresh_token": "refresh_token",
  "token_type": "bearer",
  "user": {...}
}
```

**Status:** ✅ EXISTS

---

### Refresh Token
```http
POST /v1/auth/refresh
Content-Type: application/json

Request Body:
{
  "refresh_token": "refresh_token"
}

Response (200):
{
  "access_token": "new_jwt_token",
  "refresh_token": "new_refresh_token",
  "token_type": "bearer"
}
```

**Status:** ✅ EXISTS

---

## 📊 Implementation Priority

### Phase 1: Runs (Days 1-3)
- ✅ POST /v1/runs/start
- ✅ POST /v1/runs/{id}/submit
- ✅ GET /v1/runs
- ✅ GET /v1/runs/{id}
- ✅ POST /v1/runs/{id}/abandon
- ✅ GET /v1/runs/stats/me
- ✅ GET /v1/content/questions

### Phase 2: Leaderboard (Days 4-5)
- 🔨 GET /v1/leaderboards
- 🔨 GET /v1/leaderboards/me
- 🔨 GET /v1/leaderboards/stats

### Phase 3: Character (Days 6-8)
- 🔨 GET /v1/profile
- 🔨 PUT /v1/profile/avatar
- 🔨 GET /v1/inventory/items
- 🔨 POST /v1/inventory/equip
- 🔨 POST /v1/inventory/unequip
- 🔨 GET /v1/inventory/available

---

## 🧪 Testing Endpoints

You can test all endpoints using:

1. **Swagger UI:** http://localhost:8000/docs
2. **ReDoc:** http://localhost:8000/redoc
3. **Python Script:** `python scripts/test_api_endpoints.py`
4. **cURL Examples Below**

### cURL Examples

**Get Leaderboard (once implemented):**
```bash
curl -X GET "http://localhost:8000/v1/leaderboards?scope=alltime&limit=10" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Start Run:**
```bash
curl -X POST "http://localhost:8000/v1/runs/start" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "dungeon_id": "DUNGEON_UUID",
    "floor": 1
  }'
```

**Get User Profile (once implemented):**
```bash
curl -X GET "http://localhost:8000/v1/profile" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 📝 Error Responses

All endpoints follow this error format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

### Common HTTP Status Codes
- `200 OK` - Success
- `201 Created` - Resource created successfully
- `400 Bad Request` - Invalid request data
- `401 Unauthorized` - Missing or invalid token
- `403 Forbidden` - Valid token but insufficient permissions
- `404 Not Found` - Resource doesn't exist
- `409 Conflict` - Anti-cheat violation or duplicate action
- `500 Internal Server Error` - Server error

---

## 💡 Quick Tips

1. **Always include Authorization header** for protected endpoints
2. **Use pagination** on list endpoints (limit/offset)
3. **Cache leaderboard data** on client side (refresh every 30s)
4. **Store session_token** securely for run submissions
5. **Validate on client before submitting** to reduce errors
6. **Handle 401 errors** by refreshing token automatically

---

**Legend:**
- ✅ EXISTS - Endpoint is implemented and working
- ⚠️ PARTIALLY EXISTS - Endpoint exists but needs updates
- 🔨 NEEDS IMPLEMENTATION - Endpoint needs to be created

---

**Last Updated:** October 26, 2025
**API Version:** v1
**Backend Base URL:** http://localhost:8000 (development)

