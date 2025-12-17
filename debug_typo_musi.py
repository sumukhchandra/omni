
import urllib.request
import json
import time

BASE_URL = "http://localhost:5000/api/chat"

def check(text):
    print(f"TST: '{text}'")
    try:
        req = urllib.request.Request(BASE_URL, method="POST")
        req.add_header('Content-Type', 'application/json')
        data = json.dumps({"message": text}).encode('utf-8')
        
        with urllib.request.urlopen(req, data=data) as response:
            body = json.loads(response.read().decode('utf-8'))
            action = body.get('action', {}).get('action', 'unknown')
            print(f"ACT: {action}")
            if action == "play_music":
                print("PASS")
            else:
                print("FAIL")
    except Exception as e:
        print(f"ERR: {e}")

time.sleep(3)
check("musi")
