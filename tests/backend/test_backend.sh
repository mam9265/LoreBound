#!/bin/bash

# Backend Testing Script for LoreBound
# This script helps you quickly test Phase 1 & 2 endpoints

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() { echo -e "${GREEN}✓ $1${NC}"; }
print_error() { echo -e "${RED}✗ $1${NC}"; }
print_info() { echo -e "${BLUE}ℹ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠ $1${NC}"; }

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}LoreBound Backend Testing Script${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if backend is running
print_info "Checking if backend is accessible..."
if curl -s http://localhost:8000/healthz > /dev/null; then
    print_success "Backend is running on http://localhost:8000"
else
    print_error "Backend is not accessible. Please start it with: cd lorebound-backend && docker-compose up"
    exit 1
fi

echo ""
print_info "Checking service health..."

# Check health endpoint
HEALTH=$(curl -s http://localhost:8000/healthz)
if echo "$HEALTH" | grep -q "healthy"; then
    print_success "Backend health check passed"
    echo "$HEALTH" | python3 -m json.tool 2>/dev/null || echo "$HEALTH"
else
    print_error "Backend health check failed"
    echo "$HEALTH"
fi

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Authentication${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Get token (you'll need to modify this with actual credentials)
print_info "To test authenticated endpoints, you need a token."
print_info "Options:"
echo "  1. Login with existing user:"
echo "     curl -X POST http://localhost:8000/v1/auth/login -H 'Content-Type: application/json' -d '{\"email\":\"your@email.com\",\"password\":\"yourpass\"}'"
echo ""
echo "  2. Register new user:"
echo "     curl -X POST http://localhost:8000/v1/auth/register -H 'Content-Type: application/json' -d '{\"email\":\"test@example.com\",\"password\":\"Test123!\",\"handle\":\"TestPlayer\"}'"
echo ""

# Check if TOKEN environment variable is set
if [ -z "$TOKEN" ]; then
    print_warning "TOKEN environment variable not set"
    print_info "Please set your token: export TOKEN='your_access_token'"
    print_info "Skipping authenticated endpoint tests..."
    exit 0
fi

print_success "Token found in environment"

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Testing Phase 1: Dungeon Runs${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Test 1: Get Dungeons
print_info "Test 1: Getting dungeons list..."
DUNGEONS=$(curl -s -X GET "http://localhost:8000/v1/content/dungeons" \
    -H "Authorization: Bearer $TOKEN")

if echo "$DUNGEONS" | grep -q "id"; then
    print_success "Dungeons endpoint working"
    DUNGEON_COUNT=$(echo "$DUNGEONS" | python3 -c "import sys, json; print(len(json.load(sys.stdin)))" 2>/dev/null || echo "?")
    print_info "Found $DUNGEON_COUNT dungeons"
    
    # Get first dungeon ID
    DUNGEON_ID=$(echo "$DUNGEONS" | python3 -c "import sys, json; print(json.load(sys.stdin)[0]['id'])" 2>/dev/null)
    print_info "Using dungeon ID: $DUNGEON_ID"
else
    print_error "Dungeons endpoint failed"
    echo "$DUNGEONS"
    exit 1
fi

echo ""

# Test 2: Start a Run
print_info "Test 2: Starting a new run..."
START_RUN=$(curl -s -X POST "http://localhost:8000/v1/runs/start" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d "{\"dungeon_id\": \"$DUNGEON_ID\", \"floor\": 1}")

if echo "$START_RUN" | grep -q "session_token"; then
    print_success "Run started successfully"
    RUN_ID=$(echo "$START_RUN" | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])" 2>/dev/null)
    print_info "Run ID: $RUN_ID"
else
    print_error "Failed to start run"
    echo "$START_RUN"
fi

echo ""

# Test 3: Get Questions
print_info "Test 3: Getting questions for dungeon..."
QUESTIONS=$(curl -s -X GET "http://localhost:8000/v1/content/questions?dungeon_id=$DUNGEON_ID&count=10" \
    -H "Authorization: Bearer $TOKEN")

if echo "$QUESTIONS" | grep -q "prompt"; then
    print_success "Questions endpoint working"
    QUESTION_COUNT=$(echo "$QUESTIONS" | python3 -c "import sys, json; print(len(json.load(sys.stdin)))" 2>/dev/null || echo "?")
    print_info "Got $QUESTION_COUNT questions"
else
    print_error "Questions endpoint failed"
    echo "$QUESTIONS"
fi

echo ""

# Test 4: Get Run History
print_info "Test 4: Getting run history..."
HISTORY=$(curl -s -X GET "http://localhost:8000/v1/runs?limit=5" \
    -H "Authorization: Bearer $TOKEN")

if echo "$HISTORY" | grep -q "id"; then
    print_success "Run history endpoint working"
    RUN_COUNT=$(echo "$HISTORY" | python3 -c "import sys, json; print(len(json.load(sys.stdin)))" 2>/dev/null || echo "?")
    print_info "Found $RUN_COUNT recent runs"
else
    print_warning "Run history endpoint returned unexpected response"
    echo "$HISTORY"
fi

echo ""

# Test 5: Get Run Stats
print_info "Test 5: Getting user run statistics..."
STATS=$(curl -s -X GET "http://localhost:8000/v1/runs/stats/me" \
    -H "Authorization: Bearer $TOKEN")

if echo "$STATS" | grep -q "total_runs"; then
    print_success "Run stats endpoint working"
    echo "$STATS" | python3 -m json.tool 2>/dev/null || echo "$STATS"
else
    print_warning "Run stats endpoint returned unexpected response"
    echo "$STATS"
fi

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Testing Phase 2: Leaderboard${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Test 6: All-Time Leaderboard
print_info "Test 6: Getting all-time leaderboard..."
LEADERBOARD=$(curl -s -X GET "http://localhost:8000/v1/leaderboards?scope=alltime&limit=10" \
    -H "Authorization: Bearer $TOKEN")

if echo "$LEADERBOARD" | grep -q "entries"; then
    print_success "Leaderboard endpoint working"
    PARTICIPANTS=$(echo "$LEADERBOARD" | python3 -c "import sys, json; print(json.load(sys.stdin).get('total_participants', 0))" 2>/dev/null || echo "?")
    print_info "Total participants: $PARTICIPANTS"
else
    print_error "Leaderboard endpoint failed"
    echo "$LEADERBOARD"
fi

echo ""

# Test 7: Today's Leaderboard
print_info "Test 7: Getting today's leaderboard..."
TODAY=$(curl -s -X GET "http://localhost:8000/v1/leaderboards?scope=today&limit=10" \
    -H "Authorization: Bearer $TOKEN")

if echo "$TODAY" | grep -q "period_key"; then
    print_success "Today's leaderboard working"
    PERIOD=$(echo "$TODAY" | python3 -c "import sys, json; print(json.load(sys.stdin)['period_key'])" 2>/dev/null)
    print_info "Period key: $PERIOD"
else
    print_error "Today's leaderboard failed"
    echo "$TODAY"
fi

echo ""

# Test 8: User Rank
print_info "Test 8: Getting your rank..."
MY_RANK=$(curl -s -X GET "http://localhost:8000/v1/leaderboards/me?scope=alltime&neighbors=3" \
    -H "Authorization: Bearer $TOKEN")

if echo "$MY_RANK" | grep -q "rank"; then
    print_success "User rank endpoint working"
    RANK=$(echo "$MY_RANK" | python3 -c "import sys, json; r=json.load(sys.stdin)['rank']; print(r if r else 'No rank yet')" 2>/dev/null)
    print_info "Your rank: $RANK"
else
    print_error "User rank endpoint failed"
    echo "$MY_RANK"
fi

echo ""

# Test 9: Leaderboard Stats
print_info "Test 9: Getting leaderboard statistics..."
LB_STATS=$(curl -s -X GET "http://localhost:8000/v1/leaderboards/stats?scope=alltime" \
    -H "Authorization: Bearer $TOKEN")

if echo "$LB_STATS" | grep -q "participants"; then
    print_success "Leaderboard stats endpoint working"
    echo "$LB_STATS" | python3 -m json.tool 2>/dev/null || echo "$LB_STATS"
else
    print_error "Leaderboard stats endpoint failed"
    echo "$LB_STATS"
fi

echo ""

# Test 10: Redis Caching
print_info "Test 10: Testing Redis caching..."
print_info "First request (should hit database)..."
time curl -s -X GET "http://localhost:8000/v1/leaderboards?scope=alltime&limit=10" \
    -H "Authorization: Bearer $TOKEN" -o /dev/null

print_info "Second request (should hit cache - faster)..."
time curl -s -X GET "http://localhost:8000/v1/leaderboards?scope=alltime&limit=10" \
    -H "Authorization: Bearer $TOKEN" -o /dev/null

print_success "Compare the times - second should be faster"

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Redis Cache Verification${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

print_info "Checking Redis cache keys..."
if command -v docker &> /dev/null; then
    CACHE_KEYS=$(docker exec lorebound-backend-redis-1 redis-cli KEYS "leaderboard:*" 2>/dev/null || echo "")
    if [ -n "$CACHE_KEYS" ]; then
        print_success "Redis cache populated"
        echo "$CACHE_KEYS" | head -5
        KEY_COUNT=$(echo "$CACHE_KEYS" | wc -l)
        print_info "Found $KEY_COUNT cache keys"
    else
        print_warning "No cache keys found (this is OK if first run)"
    fi
else
    print_warning "Docker not found in PATH, skipping Redis check"
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Testing Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

print_success "Backend API tests completed"
print_info "Next steps:"
echo "  1. Review any failures above"
echo "  2. Test frontend (npm start && npm run android)"
echo "  3. Complete end-to-end flow testing"
echo ""
print_info "For detailed testing instructions, see: INTEGRATION_TEST_PLAN.md"

