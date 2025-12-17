
import urllib.request
import json
import time

BASE_URL = "http://localhost:5000/api/chat"

def send_command(text):
    print(f"Sending: '{text}'")
    try:
        req = urllib.request.Request(BASE_URL, method="POST")
        req.add_header('Content-Type', 'application/json')
        data = json.dumps({"message": text}).encode('utf-8')
        with urllib.request.urlopen(req, data=data) as response:
            if response.status == 200:
                print("Status: Success (200)")
                print(f"Response: {response.read().decode('utf-8')}")
            else:
                print(f"Status: Failed ({response.status})")
    except Exception as e:
        print(f"Error: {e}")

# Test 1: Simple Speech
send_command("Say I am testing my voice capabilities.")

# Test 2: Async Check (Speak + Action)
# Note: NLU splits "then", so we send a composite command
# "Say Starting System Check then check battery"
time.sleep(2)
send_command("Say Starting System Check then check battery")
