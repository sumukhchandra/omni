
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
                print(f"  -> Plan: {plan[:100]}...")
                
                # Success Logic
                if action == "play_music":
                    print("PASS")
                else:
                    print(f"FAIL (Expected play_music, Got {action})")
            else:
                print(f"FAIL (Status {response.status})")
    except Exception as e:
        print(f"ERROR: {e}")

time.sleep(5) # Wait for backend start
check_command("hay atom can you play sond", "Voice Typo + Filler")
check_command("play song", "Generic Play")
