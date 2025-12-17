
import urllib.request
import json
import time

BASE_URL = "http://localhost:5000/api/chat"

def check_command(text, desc, expected_action=None):
    print(f"\n--- Test: '{text}' ({desc}) ---")
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
                
                # Validation Logic
                if expected_action:
                    if action == expected_action or (expected_action == "open_app" and "open" in action):
                        print("✅ PASS")
                    else:
                         print(f"❌ FAIL (Expected {expected_action}, Got {action})")
                else:
                    print("ℹ️ INFO Only")
            else:
                print(f"❌ FAIL (Status {response.status})")
    except Exception as e:
        print(f"❌ ERROR: {e}")

# Wait for potential backend startup
time.sleep(2)

# 1. Complex Voice Query (Filler + Typo)
check_command("hay atom can you play sond", "Voice Robustness", "play_music")

# 2. Single Keyword
check_command("music", "Single Keyword", "play_music")

# 3. Explicit Browser Search
check_command("open google and search for tesla", "Explicit Web", "web")

# 4. Interaction
check_command("tell me a joke", "Interaction", "info")

# 5. Fuzzy App Launch (Typo)
check_command("calculater", "App Typo", "open_app")
