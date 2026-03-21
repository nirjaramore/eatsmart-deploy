"""
Test the search endpoint
"""
import requests
import json

# Test search endpoint
url = "http://localhost:3000/search"
data = {
    "query": "amul",
    "user_id": "test_user",
    "limit": 5
}

try:
    response = requests.post(url, json=data, timeout=10)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print("Search Results:")
        print(json.dumps(result, indent=2))
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Connection error: {e}")
    print("Make sure the backend server is running on http://localhost:3000")