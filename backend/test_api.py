"""
API Test Script - Test all endpoints
Run the API server first with: python api.py
Then run this script in another terminal
"""

import requests
import json
import time

BASE_URL = "http://localhost:5000"

def print_response(title, response):
    """Pretty print API response."""
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")
    print(f"Status Code: {response.status_code}")
    try:
        print(f"Response:\n{json.dumps(response.json(), indent=2)}")
    except:
        print(f"Response: {response.text}")


def test_root():
    """Test root endpoint."""
    response = requests.get(f"{BASE_URL}/")
    print_response("Test 1: Root Endpoint", response)
    return response.status_code == 200


def test_api_info():
    """Test API info endpoint."""
    response = requests.get(f"{BASE_URL}/api")
    print_response("Test 2: API Info", response)
    return response.status_code == 200


def test_health():
    """Test health check."""
    response = requests.get(f"{BASE_URL}/api/health")
    print_response("Test 3: Health Check", response)
    return response.status_code == 200


def test_create_request():
    """Test creating a service request."""
    data = {
        "user_id": "TEST_USER_001",
        "issue_type": "flat_tire",
        "emergency_keywords": [],
        "description": "Flat tire on highway",
        "user_location": {"lat": 21.1458, "lon": 79.0882}
    }
    
    response = requests.post(f"{BASE_URL}/api/request", json=data)
    print_response("Test 4: Create Request", response)
    
    if response.status_code == 201:
        return response.json().get('request_id')
    return None


def test_get_request(request_id):
    """Test getting request details."""
    if not request_id:
        print("\n⚠️  Skipping Test 5: No request_id available")
        return False
    
    response = requests.get(f"{BASE_URL}/api/request/{request_id}")
    print_response("Test 5: Get Request Details", response)
    return response.status_code == 200


def test_update_location(request_id):
    """Test updating request location."""
    if not request_id:
        print("\n⚠️  Skipping Test 6: No request_id available")
        return False
    
    data = {"lat": 21.1460, "lon": 79.0885}
    response = requests.post(f"{BASE_URL}/api/request/{request_id}/location", json=data)
    print_response("Test 6: Update Location", response)
    return response.status_code == 200


def test_mechanics():
    """Test listing mechanics."""
    response = requests.get(f"{BASE_URL}/api/mechanics")
    print_response("Test 7: List Mechanics", response)
    return response.status_code == 200


def test_service_centers():
    """Test listing service centers."""
    response = requests.get(f"{BASE_URL}/api/service-centers")
    print_response("Test 8: List Service Centers", response)
    return response.status_code == 200


def test_cancel_request(request_id):
    """Test canceling a request."""
    if not request_id:
        print("\n⚠️  Skipping Test 9: No request_id available")
        return False
    
    response = requests.patch(f"{BASE_URL}/api/request/{request_id}/cancel")
    print_response("Test 9: Cancel Request", response)
    return response.status_code == 200


def test_invalid_endpoint():
    """Test invalid endpoint error handling."""
    response = requests.get(f"{BASE_URL}/api/invalid")
    print_response("Test 10: Invalid Endpoint (Should Return 404)", response)
    return response.status_code == 404


def main():
    """Run all API tests."""
    print("="*60)
    print("API Integration Tests")
    print("="*60)
    print(f"Testing API at: {BASE_URL}")
    print("Make sure the API server is running!")
    print("="*60)
    
    # Check if server is running
    try:
        requests.get(f"{BASE_URL}/api/health", timeout=2)
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to API server!")
        print("Please start the server first with:")
        print("  E:/new/backend/venv/Scripts/python.exe api.py")
        return
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return
    
    print("\n✓ Server is running!\n")
    time.sleep(0.5)
    
    # Run tests
    tests_passed = 0
    tests_failed = 0
    
    # Basic tests
    if test_root(): tests_passed += 1
    else: tests_failed += 1
    
    if test_api_info(): tests_passed += 1
    else: tests_failed += 1
    
    if test_health(): tests_passed += 1
    else: tests_failed += 1
    
    # Create request and get ID
    request_id = test_create_request()
    if request_id: tests_passed += 1
    else: tests_failed += 1
    
    # Tests that need request_id
    if test_get_request(request_id): tests_passed += 1
    else: tests_failed += 1
    
    if test_update_location(request_id): tests_passed += 1
    else: tests_failed += 1
    
    # Other tests
    if test_mechanics(): tests_passed += 1
    else: tests_failed += 1
    
    if test_service_centers(): tests_passed += 1
    else: tests_failed += 1
    
    if test_cancel_request(request_id): tests_passed += 1
    else: tests_failed += 1
    
    if test_invalid_endpoint(): tests_passed += 1
    else: tests_failed += 1
    
    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    print(f"✓ Passed: {tests_passed}")
    print(f"✗ Failed: {tests_failed}")
    print(f"Total: {tests_passed + tests_failed}")
    
    if tests_failed == 0:
        print("\n🎉 All tests passed!")
    else:
        print(f"\n⚠️  {tests_failed} test(s) failed")
    
    print("="*60)


if __name__ == "__main__":
    main()
