"""Test script to verify password and username length limits and error messages."""

import asyncio
import httpx
import json
from typing import Dict, Any


API_BASE_URL = "http://localhost:8000/v1"


async def test_registration(
    email: str,
    handle: str,
    password: str,
    expected_status: int,
    expected_error_contains: str = None
) -> Dict[str, Any]:
    """Test user registration with given parameters."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.post(
                f"{API_BASE_URL}/auth/register",
                json={
                    "email": email,
                    "handle": handle,
                    "password": password
                }
            )
            
            result = {
                "status_code": response.status_code,
                "response": response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text
            }
            
            if expected_status:
                assert response.status_code == expected_status, f"Expected {expected_status}, got {response.status_code}"
            
            if expected_error_contains and response.status_code != 200:
                error_detail = result["response"].get("detail", "") if isinstance(result["response"], dict) else str(result["response"])
                assert expected_error_contains.lower() in error_detail.lower(), \
                    f"Expected error to contain '{expected_error_contains}', got: {error_detail}"
            
            return result
        except Exception as e:
            return {"error": str(e)}


async def test_login(
    email: str,
    password: str,
    expected_status: int,
    expected_error_contains: str = None
) -> Dict[str, Any]:
    """Test user login with given parameters."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.post(
                f"{API_BASE_URL}/auth/login",
                json={
                    "email": email,
                    "password": password
                }
            )
            
            result = {
                "status_code": response.status_code,
                "response": response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text
            }
            
            if expected_status:
                assert response.status_code == expected_status, f"Expected {expected_status}, got {response.status_code}"
            
            if expected_error_contains and response.status_code != 200:
                error_detail = result["response"].get("detail", "") if isinstance(result["response"], dict) else str(result["response"])
                assert expected_error_contains.lower() in error_detail.lower(), \
                    f"Expected error to contain '{expected_error_contains}', got: {error_detail}"
            
            return result
        except Exception as e:
            return {"error": str(e)}


async def run_tests():
    """Run all validation tests."""
    print("=" * 80)
    print("Testing Password and Username Length Limits")
    print("=" * 80)
    
    test_results = []
    
    # Test 1: Valid registration (within limits)
    print("\n1. Testing valid registration (password: 8-25 chars, username: 3-15 chars)...")
    result = await test_registration(
        email="test1@example.com",
        handle="ValidUser123",
        password="ValidPass123!",
        expected_status=201
    )
    test_results.append(("Valid registration", result["status_code"] == 201))
    print(f"   Status: {result['status_code']} {'✓' if result['status_code'] == 201 else '✗'}")
    
    # Test 2: Password too short (< 8 chars)
    print("\n2. Testing password too short (< 8 characters)...")
    result = await test_registration(
        email="test2@example.com",
        handle="TestUser",
        password="short",
        expected_status=422,
        expected_error_contains="Password must be at least 8"
    )
    test_results.append(("Password too short", result.get("status_code") == 422))
    if result.get("status_code") == 422:
        error_msg = result.get("response", {}).get("detail", "")
        print(f"   Error message: {error_msg}")
        print(f"   ✓ Error message is user-friendly (not '[object Object]')")
    
    # Test 3: Password too long (> 25 chars)
    print("\n3. Testing password too long (> 25 characters)...")
    result = await test_registration(
        email="test3@example.com",
        handle="TestUser",
        password="a" * 26,
        expected_status=422,
        expected_error_contains="Password must be no more than 25"
    )
    test_results.append(("Password too long", result.get("status_code") == 422))
    if result.get("status_code") == 422:
        error_msg = result.get("response", {}).get("detail", "")
        print(f"   Error message: {error_msg}")
        print(f"   ✓ Error message is user-friendly (not '[object Object]')")
    
    # Test 4: Password exactly 25 chars (should be valid)
    print("\n4. Testing password exactly 25 characters (should be valid)...")
    result = await test_registration(
        email="test4@example.com",
        handle="TestUser",
        password="a" * 25,
        expected_status=201
    )
    test_results.append(("Password exactly 25 chars", result.get("status_code") == 201))
    print(f"   Status: {result['status_code']} {'✓' if result['status_code'] == 201 else '✗'}")
    
    # Test 5: Username too short (< 3 chars)
    print("\n5. Testing username too short (< 3 characters)...")
    result = await test_registration(
        email="test5@example.com",
        handle="ab",
        password="ValidPass123!",
        expected_status=422,
        expected_error_contains="Username must be at least 3"
    )
    test_results.append(("Username too short", result.get("status_code") == 422))
    if result.get("status_code") == 422:
        error_msg = result.get("response", {}).get("detail", "")
        print(f"   Error message: {error_msg}")
        print(f"   ✓ Error message is user-friendly (not '[object Object]')")
    
    # Test 6: Username too long (> 15 chars)
    print("\n6. Testing username too long (> 15 characters)...")
    result = await test_registration(
        email="test6@example.com",
        handle="a" * 16,
        password="ValidPass123!",
        expected_status=422,
        expected_error_contains="Username must be no more than 15"
    )
    test_results.append(("Username too long", result.get("status_code") == 422))
    if result.get("status_code") == 422:
        error_msg = result.get("response", {}).get("detail", "")
        print(f"   Error message: {error_msg}")
        print(f"   ✓ Error message is user-friendly (not '[object Object]')")
    
    # Test 7: Username exactly 15 chars (should be valid)
    print("\n7. Testing username exactly 15 characters (should be valid)...")
    result = await test_registration(
        email="test7@example.com",
        handle="a" * 15,
        password="ValidPass123!",
        expected_status=201
    )
    test_results.append(("Username exactly 15 chars", result.get("status_code") == 201))
    print(f"   Status: {result['status_code']} {'✓' if result['status_code'] == 201 else '✗'}")
    
    # Test 8: Multiple validation errors (both password and username issues)
    print("\n8. Testing multiple validation errors...")
    result = await test_registration(
        email="test8@example.com",
        handle="ab",  # Too short
        password="short",  # Too short
        expected_status=422
    )
    test_results.append(("Multiple validation errors", result.get("status_code") == 422))
    if result.get("status_code") == 422:
        error_msg = result.get("response", {}).get("detail", "")
        print(f"   Error message: {error_msg}")
        assert "[object Object]" not in error_msg, "Error message should not be '[object Object]'"
        print(f"   ✓ Error message is user-friendly and contains multiple errors")
    
    # Test 9: Missing required fields
    print("\n9. Testing missing required fields...")
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.post(
                f"{API_BASE_URL}/auth/register",
                json={
                    "email": "test9@example.com"
                    # Missing handle and password
                }
            )
            result = {
                "status_code": response.status_code,
                "response": response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text
            }
            test_results.append(("Missing required fields", result.get("status_code") == 422))
            if result.get("status_code") == 422:
                error_msg = result.get("response", {}).get("detail", "")
                print(f"   Error message: {error_msg}")
                assert "[object Object]" not in error_msg, "Error message should not be '[object Object]'"
                print(f"   ✓ Error message is user-friendly")
        except Exception as e:
            print(f"   Error: {e}")
    
    # Test 10: Invalid email format
    print("\n10. Testing invalid email format...")
    result = await test_registration(
        email="not-an-email",
        handle="TestUser",
        password="ValidPass123!",
        expected_status=422,
        expected_error_contains="email"
    )
    test_results.append(("Invalid email", result.get("status_code") == 422))
    if result.get("status_code") == 422:
        error_msg = result.get("response", {}).get("detail", "")
        print(f"   Error message: {error_msg}")
        print(f"   ✓ Error message is user-friendly")
    
    # Summary
    print("\n" + "=" * 80)
    print("Test Summary")
    print("=" * 80)
    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)
    print(f"\nPassed: {passed}/{total}")
    for test_name, result in test_results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status}: {test_name}")
    
    if passed == total:
        print("\n🎉 All tests passed!")
        return True
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return False


if __name__ == "__main__":
    success = asyncio.run(run_tests())
    exit(0 if success else 1)

