import requests
import socket
import time

print("=== User Service Diagnostic Tool ===")

# Check if the server is listening on port 5001
def check_port():
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex(('127.0.0.1', 5001))
        sock.close()
        return result == 0
    except:
        return False

print(f"Step 1: Checking if a server is running on port 5001... {'✅ YES' if check_port() else '❌ NO'}")

if not check_port():
    print("\nFAILURE: No server detected on port 5001!")
    print("Make sure to run 'python app.py' in a separate terminal first.")
    exit()

# Check if we can connect to the health endpoint
print("\nStep 2: Testing health endpoint...")
try:
    start = time.time()
    response = requests.get("http://localhost:5001/health", timeout=5)
    end = time.time()
    print(f"  Response time: {(end-start)*1000:.0f}ms")
    print(f"  Status code: {response.status_code}")
    if response.status_code == 200:
        print("  ✅ Health endpoint is working!")
        try:
            print(f"  Response: {response.json()}")
        except:
            print(f"  Raw response: {response.text}")
    else:
        print(f"  ❌ Health endpoint returned status code {response.status_code}")
        print(f"  Response: {response.text}")
except Exception as e:
    print(f"  ❌ Error connecting to health endpoint: {str(e)}")

# Try to register a user
print("\nStep 3: Testing user registration...")
try:
    data = {"username": "diagnosticuser", "password": "testpwd"}
    response = requests.post("http://localhost:5001/api/users/register", json=data, timeout=5)
    print(f"  Status code: {response.status_code}")
    if response.status_code == 201:
        print("  ✅ User registration successful!")
        print(f"  Response: {response.json()}")
    elif response.status_code == 400 and "already taken" in response.text:
        print("  ⚠️ User already exists (which is fine)")
        print(f"  Response: {response.json()}")
    else:
        print(f"  ❌ User registration failed with status code {response.status_code}")
        print(f"  Response: {response.text}")
except Exception as e:
    print(f"  ❌ Error with user registration: {str(e)}")

print("\n=== Diagnostic Complete ===")
print("If all tests passed, the service is working correctly.")
print("If tests failed, check the error messages above for more information.") 