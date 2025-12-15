import requests
import time

url = "http://localhost:5000/api/chat"
payload = {"message": 'note hello world this is shortcut'}

print(f"Sending POST to {url} with payload: {payload}")
try:
    response = requests.post(url, json=payload, timeout=30)
    print(f"Status Code: {response.status_code}")
    print("Response JSON:")
    print(response.json())
except Exception as e:
    print(f"Error: {e}")
