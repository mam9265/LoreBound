#!/usr/bin/env python3
"""Test script for content management endpoints."""

import requests
import json
import random
import string

def generate_random_user():
    """Generate random user data for testing."""
    random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    return {
        "email": f"content_test_{random_suffix}@example.com",
        "password": "SecurePassword123!",
        "handle": f"ContentTester{random_suffix}"
    }

def get_auth_token(base_url):
    """Register a user and get authentication token."""
    user_data = generate_random_user()
    
    print(f"Registering test user: {user_data['email']}")
    
    register_response = requests.post(
        f"{base_url}/v1/auth/register",
        json=user_data,
        headers={"Content-Type": "application/json"}
    )
    
    if register_response.status_code == 201:
        result = register_response.json()
        token = result["tokens"]["access_token"]
        print(f"[SUCCESS] Authentication token obtained")
        return token
    else:
        print(f"[ERROR] Registration failed: {register_response.status_code}")
        print(f"Response: {register_response.text}")
        return None

def test_endpoint(base_url, endpoint, headers, description):
    """Test a single endpoint and return the result."""
    print(f"\n--- Testing: {description} ---")
    print(f"Endpoint: {endpoint}")
    
    try:
        response = requests.get(f"{base_url}{endpoint}", headers=headers)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"[SUCCESS] Response received")
                
                # Show some sample data structure
                if isinstance(data, list):
                    print(f"Response type: List with {len(data)} items")
                    if len(data) > 0:
                        print(f"First item keys: {list(data[0].keys()) if isinstance(data[0], dict) else 'Not a dict'}")
                elif isinstance(data, dict):
                    print(f"Response type: Dict with keys: {list(data.keys())}")
                
                return data
            except json.JSONDecodeError:
                print(f"[WARNING] Response is not JSON: {response.text[:200]}")
                return None
        elif response.status_code == 401:
            print(f"[ERROR] Authentication failed - check token")
        elif response.status_code == 404:
            print(f"[INFO] Endpoint not found (may not be implemented)")
        elif response.status_code == 500:
            print(f"[ERROR] Server error")
            try:
                error_data = response.json()
                print(f"Error detail: {error_data.get('detail', 'No detail provided')}")
            except:
                print(f"Raw error: {response.text[:200]}")
        else:
            print(f"[WARNING] Unexpected status code")
            print(f"Response: {response.text[:200]}")
        
        return None
        
    except requests.exceptions.ConnectionError:
        print(f"[ERROR] Cannot connect to server at {base_url}")
        return None
    except Exception as e:
        print(f"[ERROR] Request failed: {e}")
        return None

def main():
    """Test all content management endpoints."""
    
    base_url = "http://localhost:8000"
    
    print("=== CONTENT ENDPOINTS TESTING ===")
    
    # First check if server is running
    try:
        health_response = requests.get(f"{base_url}/healthz")
        if health_response.status_code == 200:
            print(f"[SUCCESS] API server is running")
        else:
            print(f"[ERROR] API server health check failed")
            return
    except requests.exceptions.ConnectionError:
        print(f"[ERROR] Cannot connect to API server at {base_url}")
        print("Make sure the server is running with: docker-compose up -d")
        return
    
    # Get authentication token
    token = get_auth_token(base_url)
    if not token:
        print("[ERROR] Could not obtain authentication token")
        return
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Test content endpoints
    content_endpoints = [
        {
            "endpoint": "/v1/content/dungeons",
            "description": "Get all available dungeons"
        },
        {
            "endpoint": "/v1/content/daily",
            "description": "Get current daily challenge"
        }
    ]
    
    results = {}
    
    for endpoint_info in content_endpoints:
        endpoint = endpoint_info["endpoint"]
        description = endpoint_info["description"]
        
        result = test_endpoint(base_url, endpoint, headers, description)
        results[endpoint] = result
    
    # Test dungeons with specific ID (if we got dungeons)
    if results.get("/v1/content/dungeons"):
        dungeons = results["/v1/content/dungeons"]
        if isinstance(dungeons, list) and len(dungeons) > 0:
            # Try to get first dungeon details
            first_dungeon = dungeons[0]
            if isinstance(first_dungeon, dict) and 'id' in first_dungeon:
                dungeon_id = first_dungeon['id']
                test_endpoint(
                    base_url, 
                    f"/v1/content/dungeons/{dungeon_id}",
                    headers,
                    f"Get specific dungeon details (ID: {dungeon_id})"
                )
    
    # Test questions endpoint (requires parameters)
    print(f"\n--- Testing: Get questions for dungeon ---")
    print("Endpoint: /v1/content/questions")
    print("Note: This endpoint requires dungeon_id, floor, and count parameters")
    
    # Try with sample parameters
    questions_url = f"{base_url}/v1/content/questions?dungeon_id=550e8400-e29b-41d4-a716-446655440000&floor=1&count=5"
    try:
        questions_response = requests.get(questions_url, headers=headers)
        print(f"Status Code: {questions_response.status_code}")
        
        if questions_response.status_code == 200:
            questions_data = questions_response.json()
            print(f"[SUCCESS] Questions retrieved")
            if 'questions' in questions_data:
                print(f"Number of questions: {len(questions_data['questions'])}")
        elif questions_response.status_code == 404:
            print(f"[INFO] Sample dungeon ID not found (expected)")
        else:
            print(f"Response: {questions_response.text[:200]}")
    except Exception as e:
        print(f"[ERROR] Questions request failed: {e}")
    
    # Test admin endpoint (refresh questions)
    print(f"\n--- Testing: Refresh question pool (Admin) ---")
    print("Endpoint: /v1/content/refresh-questions")
    
    refresh_response = requests.post(
        f"{base_url}/v1/content/refresh-questions",
        headers=headers,
        params={"category": "history", "batch_size": 10}
    )
    
    print(f"Status Code: {refresh_response.status_code}")
    if refresh_response.status_code == 200:
        print(f"[SUCCESS] Question pool refresh completed")
    elif refresh_response.status_code == 403:
        print(f"[INFO] Admin endpoint - access forbidden (expected for regular user)")
    else:
        print(f"Response: {refresh_response.text[:200]}")
    
    # Summary
    print(f"\n=== CONTENT ENDPOINTS TEST SUMMARY ===")
    
    working_endpoints = []
    error_endpoints = []
    
    for endpoint, result in results.items():
        if result is not None:
            working_endpoints.append(endpoint)
        else:
            error_endpoints.append(endpoint)
    
    print(f"\n[SUCCESS] Working endpoints ({len(working_endpoints)}):")
    for endpoint in working_endpoints:
        print(f"  + {endpoint}")
    
    if error_endpoints:
        print(f"\n[ISSUES] Endpoints with issues ({len(error_endpoints)}):")
        for endpoint in error_endpoints:
            print(f"  X {endpoint}")
    
    print(f"\n[INFO] Next steps for content system:")
    print("1. Implement dungeon data seeding")
    print("2. Set up external trivia API integration")
    print("3. Create daily challenge generation logic")
    print("4. Add question pool management")
    print("5. Implement content versioning")

if __name__ == "__main__":
    main()
