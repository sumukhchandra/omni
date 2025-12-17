
import urllib.request
import time
import json

BASE_URL = "http://localhost:5000/api/chat"

tasks = [
    # --- TEXT COMMANDS ---
    {"type": "Text", "input": "Open Ntepad", "desc": "Fuzzy Logic App Open"},
    {"type": "Text", "input": "What is 100 plus 55?", "desc": "Atom Math Solver"},
    {"type": "Text", "input": "Check Battery", "desc": "System Admin (Hands)"},
    {"type": "Text", "input": "Who is the Prime Minister of India?", "desc": "In-Chat Web Scraper (Eyes)"},
    {"type": "Text", "input": "Clean temp files", "desc": "System Cleanup (Hands)"},

    # --- VOICE COMMANDS (Simulated) ---
    {"type": "Voice", "input": "Say I am a robot", "desc": "Voice Output (Mouth)"},
    {"type": "Voice", "input": "How to fix wifi", "desc": "Knowledge Base"},
    {"type": "Voice", "input": "Open YouTube", "desc": "Web Fallback"},
    {"type": "Voice", "input": "Turn volume up", "desc": "System Volume Control"},
    {"type": "Voice", "input": "Search for Tesla stock", "desc": "Generic Search Intent"}
]

print(f"{'TYPE':<10} | {'DESC':<35} | {'INPUT':<35} | {'STATUS':<10}")
print("-" * 100)

for task in tasks:
    print(f"{task['type']:<10} | {task['desc']:<35} | {task['input']:<35} | ", end="", flush=True)
    try:
        req = urllib.request.Request(BASE_URL, method="POST")
        req.add_header('Content-Type', 'application/json')
        data = json.dumps({"message": task['input']}).encode('utf-8')
        
        with urllib.request.urlopen(req, data=data) as response:
            if response.status == 200:
                resp_json = json.loads(response.read().decode('utf-8'))
                # Basic validation
                action = resp_json.get('action', {}).get('action', 'unknown') if resp_json.get('action') else 'unknown'
                print(f"PASS ({action})")
            else:
                print(f"FAIL ({response.status})")
    except Exception as e:
        print(f"ERROR: {e}")
    
    time.sleep(1.0) # Small delay between tests

print("-" * 100)
print("Test Suite Completed.")
