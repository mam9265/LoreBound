#!/usr/bin/env python3
"""Complete authentication demonstration script."""

import requests
import json
import random
import string

def generate_random_user():
    """Generate random user data for testing."""
    random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    return {
        "email": f"demo_user_{random_suffix}@example.com",
        "password": "SecurePassword123!",
        "handle": f"DemoUser{random_suffix}"
    }

def main():
    """Demonstrate complete authentication flow."""
    
    base_url = "http://localhost:8000"
    
    print("=== COMPLETE AUTHENTICATION DEMONSTRATION ===")
    
    # Generate random user data
    user_data = generate_random_user()
    print(f"\nGenerated test user:")
    print(f"Email: {user_data['email']}")
    print(f"Handle: {user_data['handle']}")
    
    # Step 1: Register new user
    print("\n1. REGISTERING NEW USER...")
    register_response = requests.post(
        f"{base_url}/v1/auth/register",
        json=user_data,
        headers={"Content-Type": "application/json"}
    )
    
    if register_response.status_code == 201:
        register_result = register_response.json()
        access_token = register_result["tokens"]["access_token"]
        print(f"[SUCCESS] Registration successful!")
        print(f"User ID: {register_result['user']['id']}")
        print(f"Access Token (first 50 chars): {access_token[:50]}...")
    else:
        print(f"[ERROR] Registration failed: {register_response.status_code}")
        print(f"Response: {register_response.text}")
        return
    
    # Step 2: Test protected endpoint with registration token
    print("\n2. TESTING PROTECTED ENDPOINT WITH REGISTRATION TOKEN...")
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
    
    # Step 3: Test login with same credentials
    print("\n3. TESTING LOGIN WITH SAME CREDENTIALS...")
    login_data = {
        "email": user_data["email"],
        "password": user_data["password"]
    }
    
    login_response = requests.post(
        f"{base_url}/v1/auth/login",
        json=login_data,
        headers={"Content-Type": "application/json"}
    )
    
    if login_response.status_code == 200:
        login_result = login_response.json()
        new_access_token = login_result["tokens"]["access_token"]
        print(f"[SUCCESS] Login successful!")
        print(f"New Access Token (first 50 chars): {new_access_token[:50]}...")
        
        # Update headers with new token
        headers["Authorization"] = f"Bearer {new_access_token}"
    else:
        print(f"[ERROR] Login failed: {login_response.status_code}")
        print(f"Response: {login_response.text}")
        return
    
    # Step 4: Test without authorization header
    print("\n4. TESTING WITHOUT AUTHORIZATION HEADER (should fail)...")
    no_auth_response = requests.get(f"{base_url}/v1/auth/me")
    
    if no_auth_response.status_code == 401:
        error_detail = no_auth_response.json()
        print(f"[SUCCESS] Correctly rejected request without token")
        print(f"Error: {error_detail['detail']}")
    else:
        print(f"[ERROR] Unexpected response: {no_auth_response.status_code}")
    
    # Step 5: Test with malformed token
    print("\n5. TESTING WITH INVALID TOKEN (should fail)...")
    invalid_headers = {
        "Authorization": "Bearer invalid_jwt_token_here",
        "Content-Type": "application/json"
    }
    
    invalid_response = requests.get(
        f"{base_url}/v1/auth/me",
        headers=invalid_headers
    )
    
    if invalid_response.status_code == 401:
        error_detail = invalid_response.json()
        print(f"[SUCCESS] Correctly rejected invalid token")
        print(f"Error: {error_detail['detail']}")
    else:
        print(f"[ERROR] Unexpected response: {invalid_response.status_code}")
    
    # Step 6: Test token refresh
    print("\n6. TESTING TOKEN REFRESH...")
    refresh_token = login_result["tokens"]["refresh_token"]
    refresh_data = {
        "refresh_token": refresh_token
    }
    
    refresh_response = requests.post(
        f"{base_url}/v1/auth/refresh",
        json=refresh_data,
        headers={"Content-Type": "application/json"}
    )
    
    if refresh_response.status_code == 200:
        refresh_result = refresh_response.json()
        print(f"[SUCCESS] Token refresh successful!")
        print(f"New tokens generated")
    else:
        print(f"[WARNING] Token refresh failed: {refresh_response.status_code}")
        print(f"Response: {refresh_response.text}")
    
    # Step 7: Demonstrate proper usage pattern
    print("\n7. PROPER USAGE PATTERN DEMONSTRATION...")
    
    # Test a few different endpoints with valid token
    endpoints = [
        "/v1/auth/me",
        "/v1/content/dungeons",
        "/v1/profile/"
    ]
    
    for endpoint in endpoints:
        test_response = requests.get(
            f"{base_url}{endpoint}",
            headers=headers
        )
        
        if test_response.status_code in [200, 404]:  # 404 is OK for unimplemented endpoints
            print(f"[SUCCESS] {endpoint} - Status: {test_response.status_code}")
        elif test_response.status_code == 401:
            print(f"[ERROR] {endpoint} - Authentication failed!")
        else:
            print(f"[INFO] {endpoint} - Status: {test_response.status_code}")
    
    print("\n=== AUTHENTICATION DEMONSTRATION COMPLETE ===")
    print("\n[SOLUTION] If you're getting 'Could not validate credentials':")
    print("1. Make sure you're including the Authorization header:")
    print("   Authorization: Bearer <your_jwt_token>")
    print("2. Ensure the token is valid (not expired)")
    print("3. Check that you're using the access_token, not refresh_token")
    print("4. Verify the token format is correct (should start with 'eyJ')")
    print("\n[EXAMPLE] Correct header format:")
    print(f"Authorization: Bearer {access_token[:50]}...")

if __name__ == "__main__":
    main()
