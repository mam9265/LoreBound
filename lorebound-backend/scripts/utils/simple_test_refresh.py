#!/usr/bin/env python3
"""Simple test to verify the refresh endpoint works with fixed code."""

import requests

def test_simple_refresh():
    """Test the refresh endpoint with a simple call."""
    
    base_url = "http://localhost:8000"
    
    # Login as admin
    admin_data = {"email": "admin@lorebound.com", "password": "AdminPass123!"}
    
    login_response = requests.post(
        f"{base_url}/v1/auth/login",
        json=admin_data,
        headers={"Content-Type": "application/json"}
    )
    
    if login_response.status_code != 200:
        print(f"[ERROR] Admin login failed: {login_response.status_code}")
        return
    
    token = login_response.json()["tokens"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    print("=== TESTING REFRESH ENDPOINT ===")
    
    # Test dungeons first
    dungeons_response = requests.get(f"{base_url}/v1/content/dungeons", headers=headers)
    print(f"Dungeons: {dungeons_response.status_code} - {len(dungeons_response.json()) if dungeons_response.status_code == 200 else 'Error'}")
    
    # Test questions
    if dungeons_response.status_code == 200:
        dungeons = dungeons_response.json()
        if dungeons:
            dungeon_id = dungeons[0]['id']
            questions_response = requests.get(
                f"{base_url}/v1/content/questions",
                headers=headers,
                params={"dungeon_id": dungeon_id, "floor": 1, "count": 5}
            )
            print(f"Questions: {questions_response.status_code}")
            if questions_response.status_code == 200:
                questions_data = questions_response.json()
                print(f"Questions in response: {len(questions_data.get('questions', []))}")
    
    # Test one refresh call (small batch to avoid rate limits)
    print("\nTesting single refresh call...")
    refresh_response = requests.post(
        f"{base_url}/v1/content/refresh-questions",
        headers=headers,
        params={"category": "history", "batch_size": 10}
    )
    
    print(f"Refresh status: {refresh_response.status_code}")
    if refresh_response.status_code == 200:
        result = refresh_response.json()
        print(f"[SUCCESS] Questions added: {result.get('questions_added', 0)}")
    else:
        try:
            error = refresh_response.json()
            print(f"[ERROR] {error.get('detail', 'Unknown error')}")
        except:
            print(f"[ERROR] Raw response: {refresh_response.text}")

if __name__ == "__main__":
    test_simple_refresh()
