
import urllib.request
import json
import time

BASE_URL = "http://localhost:5000/api/chat"

def check_command(text, desc):
    print(f"Testing: '{text}' ({desc})")
    try:
        req = urllib.request.Request(BASE_URL, method="POST")
        req.add_header('Content-Type', 'application/json')
        data = json.dumps({"message": text}).encode('utf-8')
        
        with urllib.request.urlopen(req, data=data) as response:
            if response.status == 200:
                body = json.loads(response.read().decode('utf-8'))
                action = body.get('action', {}).get('action', 'unknown')
                plan = body.get('plan', 'no plan')
                print(f"  -> Action: {action}")
                print(f"  -> Plan: {plan[:100]}...") # Truncate for readability
                
                if action == "play_music" and "if it is windows" not in plan:
                    print("PASS")
                else:
                    print(f"FAIL (Expected play_music, Clean Plan. Got {action})")
            else:
                print(f"FAIL (Status {response.status})")
    except Exception as e:
        print(f"ERROR: {e}")

# Test 1: The Problem Case
check_command("i hope you can you play ordinary song", "Regex Fix Check")

# Test 2: Verbose Check
check_command("play baby", "Plan Cleanliness Check")
