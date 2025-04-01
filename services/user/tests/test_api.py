#!/usr/bin/env python3
import requests
import json
import os
import sys
import random
import string
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path

# Get the project root directory (two levels up from this script)
project_root = Path(__file__).parent.parent.parent

# Load environment variables from multiple locations
load_dotenv(project_root / '.env')  # Main .env file
load_dotenv(Path(__file__).parent / '.env.test')  # Test .env file

# Configuration with better error handling
def get_env_var(key, default=None):
    value = os.environ.get(key, default)
    if value is None:
        raise ValueError(f"Missing required environment variable: {key}")
    return value

try:
    host = get_env_var('API_HOST', 'localhost')
    port = get_env_var('PORT', '5001')
    base_url = f"http://{host}:{port}"
except ValueError as e:
    print(f"❌ Error: {e}")
    print("Please ensure all required environment variables are set in .env.test")
    sys.exit(1)

# Store the user ID for requests
test_user_id = None

def generate_random_string(length=8):
    """Generate a random string for test data"""
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def test_health_check():
    """Test the health check endpoint"""
    url = f"{base_url}/health"
    print(f"Testing health check: GET {url}")
    
    try:
        response = requests.get(url)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {e}")
        return False

def test_register_user():
    """Test user registration"""
    global test_user_id
    
    url = f"{base_url}/api/users/register"
    print(f"Testing user registration: POST {url}")
    
    # Generate random test user data
    random_suffix = generate_random_string()
    payload = {
        'username': f'testuser_{random_suffix}',
        'email': f'test_{random_suffix}@example.com',
        'password': 'TestPassword123!',
        'first_name': 'Test',
        'last_name': 'User'
    }
    
    print(f"Request Payload (sensitive data masked):")
    masked_payload = payload.copy()
    masked_payload['password'] = '*****'
    print(json.dumps(masked_payload, indent=2))
    
    try:
        response = requests.post(url, json=payload)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 201:
            result = response.json()
            test_user_id = result.get('user_id')
            
            print("✅ Success! User registered.")
            print("Username:", result.get('user', {}).get('username'))
            print("User ID:", test_user_id)
            
            return True
        else:
            print(f"❌ Error: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {e}")
        return False

def test_login_user():
    """Test user login"""
    url = f"{base_url}/api/users/login"
    print(f"Testing user login: POST {url}")
    
    # Find the username from the previous test
    if not test_user_id:
        print("❌ Cannot test login - no test user created")
        return False
    
    # Get all users to find our test user
    all_users_url = f"{base_url}/api/users/search?q=testuser"
    response = requests.get(all_users_url)
    if response.status_code != 200:
        print(f"❌ Could not retrieve users to find test user: {response.text}")
        return False
    
    users = response.json()
    if not users:
        print("❌ No test users found")
        return False
    
    # Find our test user by ID
    test_user = next((user for user in users if user.get('id') == test_user_id), None)
    if not test_user:
        print(f"❌ Could not find test user with ID {test_user_id}")
        return False
    
    payload = {
        'username': test_user.get('username'),
        'password': 'TestPassword123!'
    }
    
    print(f"Request Payload (sensitive data masked):")
    masked_payload = payload.copy()
    masked_payload['password'] = '*****'
    print(json.dumps(masked_payload, indent=2))
    
    try:
        response = requests.post(url, json=payload)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            user_id = result.get('user_id')
            
            print("✅ Success! User logged in.")
            print("Username:", result.get('user', {}).get('username'))
            print("User ID:", user_id)
            
            return True
        else:
            print(f"❌ Error: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {e}")
        return False

def test_get_profile():
    """Test getting user profile"""
    if not test_user_id:
        print("❌ Cannot test profile retrieval - no test user created")
        return False
    
    url = f"{base_url}/api/users/profile/{test_user_id}"
    print(f"Testing get profile: GET {url}")
    
    try:
        response = requests.get(url)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            user_profile = response.json()
            print("✅ Success! Retrieved user profile.")
            print("Username:", user_profile.get('username'))
            print("Email:", user_profile.get('email'))
            print("First Name:", user_profile.get('first_name'))
            print("Last Name:", user_profile.get('last_name'))
            
            return True
        else:
            print(f"❌ Error: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {e}")
        return False

def test_update_profile():
    """Test updating user profile"""
    if not test_user_id:
        print("❌ Cannot test profile update - no test user created")
        return False
    
    url = f"{base_url}/api/users/profile/{test_user_id}"
    print(f"Testing update profile: PUT {url}")
    
    payload = {
        'first_name': 'Updated',
        'last_name': 'TestUser'
    }
    
    print(f"Request Payload:")
    print(json.dumps(payload, indent=2))
    
    try:
        response = requests.put(url, json=payload)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Success! Profile updated.")
            print("New First Name:", result.get('user', {}).get('first_name'))
            print("New Last Name:", result.get('user', {}).get('last_name'))
            
            return True
        else:
            print(f"❌ Error: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {e}")
        return False

def test_search_users():
    """Test searching for users"""
    url = f"{base_url}/api/users/search?q=test"
    print(f"Testing user search: GET {url}")
    
    try:
        response = requests.get(url)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            users = response.json()
            count = len(users)
            print(f"✅ Success! Found {count} users matching 'test'.")
            if count > 0:
                print("First user found:", users[0].get('username'))
            
            return True
        else:
            print(f"❌ Error: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {e}")
        return False

def test_get_user_by_id():
    """Test getting a user by ID"""
    if not test_user_id:
        print("❌ Cannot test get user by ID - no test user created")
        return False
    
    url = f"{base_url}/api/users/{test_user_id}"
    print(f"Testing get user by ID: GET {url}")
    
    try:
        response = requests.get(url)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            user = response.json()
            print("✅ Success! Retrieved user by ID.")
            print("Username:", user.get('username'))
            print("First Name:", user.get('first_name'))
            print("Last Name:", user.get('last_name'))
            
            # Verify that sensitive information is not exposed
            if 'email' in user:
                print("⚠️ Warning: Public user data includes email!")
            if 'password_hash' in user:
                print("⚠️ Warning: Public user data includes password hash!")
            
            return True
        else:
            print(f"❌ Error: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {e}")
        return False

def run_all_tests():
    """Run all API tests"""
    print("=" * 50)
    print("🧪 TESTING USER SERVICE API")
    print("=" * 50)
    
    # Test health check
    print("\n🩺 Health Check Test")
    print("-" * 30)
    health_ok = test_health_check()
    
    if not health_ok:
        print("❌ Health check failed, aborting remaining tests")
        return
    
    # Test user registration
    print("\n📝 User Registration Test")
    print("-" * 30)
    registration_ok = test_register_user()
    
    if not registration_ok:
        print("❌ User registration failed, some tests may not work")
    
    # Test user login
    print("\n🔑 User Login Test")
    print("-" * 30)
    login_ok = test_login_user()
    
    if not login_ok:
        print("❌ User login failed, authenticated tests may not work")
    
    # Test get profile
    print("\n👤 Get User Profile Test")
    print("-" * 30)
    test_get_profile()
    
    # Test update profile
    print("\n✏️ Update User Profile Test")
    print("-" * 30)
    test_update_profile()
    
    # Test get user by ID
    print("\n🔍 Get User by ID Test")
    print("-" * 30)
    test_get_user_by_id()
    
    # Test search users
    print("\n🔎 Search Users Test")
    print("-" * 30)
    test_search_users()
    
    print("\n" + "=" * 50)
    print("🏁 All tests completed!")
    print("=" * 50)

if __name__ == "__main__":
    run_all_tests() 