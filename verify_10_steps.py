import requests
import time

def verify_10_tasks():
    base_url = "http://localhost:5000/api/chat"
    headers = {"Content-Type": "application/json"}
    
    tasks = [
        "open google",
        "search for python",
        "select first option",
        "open new tab",
        "type hello world",
        "close tab",
        "search for weather",
        "select second option", 
        "open new tab",
        "close tab"
    ]
    
    print("--- 10-Step browser Verification Protocol ---")
    for i, task in enumerate(tasks):
        print(f"\n[Task {i+1}] Simulating command: '{task}'")
        # In a real user test, we would wait for user input.
        # Here we simulate the backend processing to ensure it DOES NOT CRASH.
        try:
             res = requests.post(base_url, json={"message": task}, headers=headers)
             print(f"Status: {res.status_code}")
             print(f"Response: {res.json().get('reply', '')[:100]}...") # truncate
             time.sleep(2) # Pausing between steps
        except Exception as e:
             print(f"FAILED Task {i+1}: {e}")
             break

if __name__ == "__main__":
    verify_10_tasks()
