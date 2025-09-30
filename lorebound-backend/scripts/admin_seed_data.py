#!/usr/bin/env python3
"""Admin script to seed basic content data via database connection."""

import requests
import json

def create_admin_user_and_seed():
    """Create admin user and seed basic content."""
    
    base_url = "http://localhost:8000"
    
    print("=== ADMIN CONTENT SEEDING ===")
    
    # Create admin user
    admin_data = {
        "email": "admin@lorebound.com", 
        "password": "AdminPass123!",
        "handle": "LoreBoundAdmin"
    }
    
    print("1. Creating admin user...")
    
    # Try to register admin user
    register_response = requests.post(
        f"{base_url}/v1/auth/register",
        json=admin_data,
        headers={"Content-Type": "application/json"}
    )
    
    if register_response.status_code == 201:
        result = register_response.json()
        token = result["tokens"]["access_token"]
        print(f"[SUCCESS] Admin user created")
    elif register_response.status_code == 409:
        # User already exists, try to login
        print("[INFO] Admin user already exists, logging in...")
        login_response = requests.post(
            f"{base_url}/v1/auth/login",
            json={"email": admin_data["email"], "password": admin_data["password"]},
            headers={"Content-Type": "application/json"}
        )
        
        if login_response.status_code == 200:
            result = login_response.json()
            token = result["tokens"]["access_token"]
            print(f"[SUCCESS] Admin user logged in")
        else:
            print(f"[ERROR] Admin login failed: {login_response.status_code}")
            return
    else:
        print(f"[ERROR] Admin user creation failed: {register_response.status_code}")
        return
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Test current state
    print("\n2. Testing current content state...")
    
    dungeons_response = requests.get(f"{base_url}/v1/content/dungeons", headers=headers)
    if dungeons_response.status_code == 200:
        dungeons = dungeons_response.json()
        print(f"Current dungeons in database: {len(dungeons)}")
        
        if len(dungeons) > 0:
            print("Dungeons already exist:")
            for dungeon in dungeons:
                print(f"  - {dungeon.get('title', 'Unknown')} ({dungeon.get('category', 'Unknown')})")
        else:
            print("No dungeons found - database needs seeding")
    
    # Test available categories for refresh endpoint
    print("\n3. Testing question refresh with valid categories...")
    
    valid_categories = ['sports', 'music', 'history', 'pop_culture']
    
    for category in valid_categories:
        print(f"\nTesting category: {category}")
        
        refresh_response = requests.post(
            f"{base_url}/v1/content/refresh-questions",
            headers=headers,
            params={"category": category, "batch_size": 10}
        )
        
        print(f"Status: {refresh_response.status_code}")
        
        if refresh_response.status_code == 200:
            result = refresh_response.json()
            print(f"[SUCCESS] Questions refreshed for {category}")
            print(f"Questions added: {result.get('questions_added', 0)}")
        else:
            try:
                error = refresh_response.json()
                print(f"[ERROR] {error.get('detail', 'Unknown error')}")
            except:
                print(f"[ERROR] Raw response: {refresh_response.text[:100]}")
        
        # Don't overwhelm the API
        import time
        time.sleep(1)
    
    # Test dungeons again after potential seeding
    print("\n4. Re-testing dungeons endpoint...")
    
    dungeons_response = requests.get(f"{base_url}/v1/content/dungeons", headers=headers)
    if dungeons_response.status_code == 200:
        dungeons = dungeons_response.json()
        print(f"Dungeons now in database: {len(dungeons)}")
        
        if len(dungeons) > 0:
            # Test questions with actual dungeon ID
            first_dungeon = dungeons[0]
            dungeon_id = first_dungeon['id']
            
            print(f"\n5. Testing questions with real dungeon ID: {dungeon_id}")
            
            questions_response = requests.get(
                f"{base_url}/v1/content/questions",
                headers=headers,
                params={"dungeon_id": dungeon_id, "floor": 1, "count": 5}
            )
            
            print(f"Questions endpoint status: {questions_response.status_code}")
            
            if questions_response.status_code == 200:
                questions_data = questions_response.json()
                print(f"[SUCCESS] Questions retrieved: {len(questions_data.get('questions', []))}")
            else:
                try:
                    error = questions_response.json()
                    print(f"[ERROR] {error.get('detail', 'Unknown error')}")
                except:
                    print(f"[ERROR] Raw response: {questions_response.text[:100]}")
    
    print(f"\n=== CONTENT ENDPOINTS SUMMARY ===")
    print(f"+ Authentication: Working")
    print(f"+ Dungeons list: Working (returns {len(dungeons)} dungeons)")
    print(f"? Daily challenge: Needs dungeons in database")
    print(f"? Questions: Needs dungeons and questions in database")
    print(f"? Refresh: Depends on external API availability")

if __name__ == "__main__":
    create_admin_user_and_seed()
