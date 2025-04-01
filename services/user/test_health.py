import requests

print("Testing User Service...")

# Test health endpoint
try:
    response = requests.get("http://127.0.0.1:5000/health")
    print(f"Health Check: {'✅ OK' if response.status_code == 200 else '❌ Failed'}")
except Exception as e:
    print(f"Health Check: ❌ Error - {e}")

# Test user registration
try:
    data = {"username": "testuser", "password": "test123"}
    response = requests.post("http://127.0.0.1:5000/api/users/register", json=data)
    if response.status_code == 201:
        print("User Registration: ✅ OK")
    elif response.status_code == 400 and "already taken" in response.text:
        print("User Registration: ⚠️ User exists (OK)")
    else:
        print(f"User Registration: ❌ Failed - {response.text}")
except Exception as e:
    print(f"User Registration: ❌ Error - {e}")

# Test user login
try:
    data = {"username": "testuser", "password": "test123"}
    response = requests.post("http://127.0.0.1:5000/api/users/login", json=data)
    print(f"User Login: {'✅ OK' if response.status_code == 200 else '❌ Failed'}")
except Exception as e:
    print(f"User Login: ❌ Error - {e}")

# Test user search
try:
    response = requests.get("http://127.0.0.1:5000/api/users/search?q=test")
    print(f"User Search: {'✅ OK' if response.status_code == 200 else '❌ Failed'}")
except Exception as e:
    print(f"User Search: ❌ Error - {e}")

print("\nMake sure to run the app with: python app.py") 