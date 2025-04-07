#!/usr/bin/env python3
import requests
import json
import os
import sys
from datetime import datetime, timedelta
from dotenv import load_dotenv
from pathlib import Path
import pytest

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
    port = get_env_var('PORT', '5002')
    base_url = f"http://{host}:{port}"
except ValueError as e:
    print(f"❌ Error: {e}")
    print("Please ensure all required environment variables are set in .env.test")
    sys.exit(1)

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

def test_create_recommendation():
    """Test creating a recommendation through the API"""
    url = f"{base_url}/api/recommendations"
    print(f"Testing create recommendation: POST {url}")
    
    # Generate test data
    today = datetime.now().date()
    payload = {
        'trip_id': f'api-test-{datetime.now().strftime("%Y%m%d%H%M%S")}',
        'destination': 'Barcelona',
        'start_date': (today + timedelta(days=45)).isoformat(),
        'end_date': (today + timedelta(days=50)).isoformat()
    }
    
    print(f"Request Payload:")
    print(json.dumps(payload, indent=2))
    
    try:
        response = requests.post(url, json=payload)
        print(f"Status Code: {response.status_code}")
        if response.status_code in (200, 201):
            result = response.json()
            print("✅ Success! Recommendation created.")
            print("Trip ID:", result.get('trip_id'))
            print("Response contains recommendations:", 'recommendations' in result)
            return result.get('trip_id')
        else:
            print(f"❌ Error: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {e}")
        return None

def test_get_recommendation(trip_id):
    """Test retrieving a recommendation by ID"""
    if not trip_id:
        print("❌ Cannot test get recommendation - no trip_id provided")
        return False
        
    url = f"{base_url}/api/recommendations/{trip_id}"
    print(f"Testing get recommendation: GET {url}")
    
    try:
        response = requests.get(url)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print("✅ Success! Retrieved recommendation.")
            print("Trip ID:", result.get('trip_id'))
            
            # Show a sample of the recommendations
            if 'recommendations' in result and result['recommendations']:
                recommendations = result['recommendations']
                if 'attractions' in recommendations and recommendations['attractions']:
                    print("Sample attraction:", recommendations['attractions'][0]['name'])
                if 'tips' in recommendations and recommendations['tips']:
                    print("Sample tip:", recommendations['tips'][0])
            return True
        else:
            print(f"❌ Error: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {e}")
        return False

def test_get_all_recommendations():
    """Test retrieving all recommendations"""
    url = f"{base_url}/api/recommendations"
    print(f"Testing get all recommendations: GET {url}")
    
    try:
        response = requests.get(url)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            count = len(result)
            print(f"✅ Success! Retrieved {count} recommendations.")
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
    print("🧪 TESTING RECOMMENDATION SERVICE API")
    print("=" * 50)
    
    # Test health check
    print("\n🩺 Health Check Test")
    print("-" * 30)
    health_ok = test_health_check()
    
    if not health_ok:
        print("❌ Health check failed, aborting remaining tests")
        return
    
    # Test create recommendation
    print("\n🆕 Create Recommendation Test")
    print("-" * 30)
    trip_id = test_create_recommendation()
    
    # Test get recommendation
    if trip_id:
        print("\n🔍 Get Recommendation Test")
        print("-" * 30)
        test_get_recommendation(trip_id)
    
    # Test get all recommendations
    print("\n📋 Get All Recommendations Test")
    print("-" * 30)
    test_get_all_recommendations()
    
    print("\n" + "=" * 50)
    print("🏁 All tests completed!")
    print("=" * 50)

@pytest.mark.skip(reason="HTTP APIs have been removed from recommendation-management service")
def test_deprecated():
    """This test is deprecated and should be skipped"""
    pass

if __name__ == "__main__":
    run_all_tests() 