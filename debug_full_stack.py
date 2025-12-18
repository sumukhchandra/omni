import requests
import json
import time

def test_backend_response():
    url = "http://localhost:5000/api/chat"
    headers = {"Content-Type": "application/json"}
    
    # Test 1: Simple Command
    payload = {"message": "open new tab"}
    print(f"Sending: {payload}")
    try:
        response = requests.post(url, json=payload, headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_backend_response()
