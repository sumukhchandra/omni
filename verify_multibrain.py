
import urllib.request
import json
import time

print("--- MULTI-BRAIN VERIFICATION ---")
time.sleep(2) 

tasks = {
    "system": "Turn volume up",
    "conversation": "Hello Atom",
    "web": "Play Blinding Lights",
    "app": "Open Notepad"
}

url = "http://localhost:5000/api/chat"

for category, cmd in tasks.items():
    print(f"\nTask: '{cmd}' ({category})")
    try:
        data = json.dumps({"message": cmd}).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req) as response:
            if response.status == 200:
                body = response.read().decode('utf-8')
                resp_data = json.loads(body)
                logs = resp_data.get("logs", [])
                
                decision = "Unknown"
                for log in logs:
                    if "[SELECTOR] Chosen:" in log:
                        decision = log.split("Chosen:")[1].strip()
                print(f"  -> Selector Decision: {decision}")
            else:
                print(f"  -> Error: {response.status}")
    except Exception as e:
        print(f"  -> Failed: {e}")
