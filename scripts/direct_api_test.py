#!/usr/bin/env python3
"""Direct API test to see detailed error responses."""

import httpx
import json
import asyncio

async def test_registration_directly():
    """Test registration directly and get detailed error responses."""
    
    registration_data = {
        "email": "direct_test@example.com",
        "password": "SecurePassword123!",
        "handle": "DirectTest"
    }
    
    print("=== DIRECT API TEST ===")
    
    # First test health endpoint
    try:
        async with httpx.AsyncClient() as client:
            print("Testing health endpoint...")
            health_response = await client.get("http://localhost:8000/healthz")
            print(f"Health status: {health_response.status_code}")
            if health_response.status_code == 200:
                print(f"Health response: {health_response.json()}")
            else:
                print(f"Health error: {health_response.text}")
    except Exception as e:
        print(f"Health endpoint failed: {e}")
        return
    
    # Test registration
    try:
        async with httpx.AsyncClient() as client:
            print("\nTesting registration endpoint...")
            response = await client.post(
                "http://localhost:8000/v1/auth/register",
                json=registration_data,
                headers={"Content-Type": "application/json"}
            )
            
            print(f"Registration status: {response.status_code}")
            
            if response.status_code == 201:
                print("SUCCESS: Registration worked!")
                result = response.json()
                print(f"User ID: {result.get('user', {}).get('id')}")
                print(f"Access token length: {len(result.get('tokens', {}).get('access_token', ''))}")
            else:
                print(f"ERROR: Registration failed")
                try:
                    error_details = response.json()
                    print(f"Error details: {json.dumps(error_details, indent=2)}")
                except:
                    print(f"Response text: {response.text}")
                
    except Exception as e:
        print(f"Registration request failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_registration_directly())
