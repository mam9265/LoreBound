#!/usr/bin/env python3
"""Test script to demonstrate proper authentication usage."""

import requests
import json

def main():
    """Test the complete authentication flow and protected endpoint access."""
    
    base_url = "http://localhost:8000"
    
    print("=== TESTING COMPLETE AUTHENTICATION FLOW ===")
    
    # Step 1: Login to get tokens
    print("\n1. Logging in to get JWT tokens...")
    login_data = {
        "email": "testuser@example.com",
        "password": "SecurePassword123!"
    }
    
    login_response = requests.post(
        f"{base_url}/v1/auth/login",
        json=login_data,
        headers={"Content-Type": "application/json"}
    )
    
    if login_response.status_code != 200:
        print(f"[ERROR] Login failed: {login_response.status_code}")
        print(f"Response: {login_response.text}")
        return
    
    login_result = login_response.json()
    access_token = login_result["tokens"]["access_token"]
    
    print(f"[SUCCESS] Login successful!")
    print(f"User ID: {login_result['user']['id']}")
    print(f"Access Token (first 50 chars): {access_token[:50]}...")
    
    # Step 2: Test protected endpoint (/v1/auth/me)
    print("\n2. Testing protected endpoint with valid token...")
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    me_response = requests.get(
        f"{base_url}/v1/auth/me",
        headers=headers
    )
    
    if me_response.status_code == 200:
        user_info = me_response.json()
        print(f"[SUCCESS] Protected endpoint access successful!")
        print(f"Current user: {user_info['email']}")
        print(f"User status: {user_info['status']}")
    else:
        print(f"[ERROR] Protected endpoint failed: {me_response.status_code}")
        print(f"Response: {me_response.text}")
    
    # Step 3: Test without token (should fail)
    print("\n3. Testing protected endpoint WITHOUT token (should fail)...")
    no_auth_response = requests.get(f"{base_url}/v1/auth/me")
    
    if no_auth_response.status_code == 401:
        print(f"[SUCCESS] Correctly rejected request without token (401)")
        print(f"Error: {no_auth_response.json()}")
    else:
        print(f"[ERROR] Unexpected response: {no_auth_response.status_code}")
    
    # Step 4: Test with invalid token (should fail)
    print("\n4. Testing protected endpoint with INVALID token (should fail)...")
    invalid_headers = {
        "Authorization": "Bearer invalid_token_here",
        "Content-Type": "application/json"
    }
    
    invalid_response = requests.get(
        f"{base_url}/v1/auth/me",
        headers=invalid_headers
    )
    
    if invalid_response.status_code == 401:
        print(f"[SUCCESS] Correctly rejected invalid token (401)")
        print(f"Error: {invalid_response.json()}")
    else:
        print(f"[ERROR] Unexpected response: {invalid_response.status_code}")
    
    # Step 5: Test other protected endpoints
    print("\n5. Testing other protected endpoints...")
    
    # Test dungeons endpoint
    dungeons_response = requests.get(
        f"{base_url}/v1/content/dungeons",
        headers=headers
    )
    
    if dungeons_response.status_code == 200:
        print(f"[SUCCESS] Dungeons endpoint accessible")
    else:
        print(f"[WARNING] Dungeons endpoint: {dungeons_response.status_code}")
        print(f"Response: {dungeons_response.text}")
    
    print("\n=== AUTHENTICATION FLOW COMPLETE ===")
    print("\n[GUIDE] How to use authentication:")
    print("1. POST /v1/auth/login with email/password")
    print("2. Extract 'access_token' from response")
    print("3. Include in headers: Authorization: Bearer <token>")
    print("4. Use this header for all protected endpoints")

if __name__ == "__main__":
    main()
