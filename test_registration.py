import requests
import json

url = "http://127.0.0.1:8000/register"
data = {
    "name": "Test User",
    "username": "testuser123",
    "email": "testuser123@example.com",
    "password": "testpassword123"
}

try:
    response = requests.post(url, json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"Error: {e}")
