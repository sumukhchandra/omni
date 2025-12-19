import requests
import time
import json

BASE_URL = "http://localhost:5000"

def test_endpoint(method, endpoint, data=None):
    url = f"{BASE_URL}{endpoint}"
    print(f"\n--- Testing {method} {endpoint} ---")
    try:
        if method == "GET":
            response = requests.get(url)
        else:
            response = requests.post(url, json=data)
        
        print(f"Status Code: {response.status_code}")
        try:
            print(f"Response: {json.dumps(response.json(), indent=2)}")
        except:
            print(f"Response (Text): {response.text}")
        return response
    except Exception as e:
        print(f"❌ Request Failed: {e}")
        return None

def main():
    print("🏥 STARTING FULL SYSTEM HEALTH CHECK (BRAIN & BODY) 🏥")
    
    # 1. Check Body Status
    print("\n[BODY CHECK] Initial Status...")
    test_endpoint("GET", "/api/agent/status")
    
    # 2. Stop Agent (Reset)
    print("\n[BODY CHECK] Stopping Agent...")
    test_endpoint("POST", "/api/agent/stop")
    
    # 3. Start Agent (Test Launch)
    print("\n[BODY CHECK] Starting Agent...")
    test_endpoint("POST", "/api/agent/start")
    time.sleep(2) # Give it time to spawn
    
    # 4. Verify Running
    print("\n[BODY CHECK] Verifying Running State...")
    test_endpoint("GET", "/api/agent/status")
    
    # 5. Check Brain (Chat)
    print("\n[BRAIN CHECK] Testing AI Response (Hello)...")
    test_endpoint("POST", "/api/chat", {"message": "Hello atom"})
    
    # 6. Check Brain (Action Intent)
    print("\n[BRAIN CHECK] Testing Action Intent (Click on Siddu)...")
    # This simulates a command that requires the Finalizer to plan and potential execution
    test_endpoint("POST", "/api/chat", {"message": "click on Siddu"})

    print("\n[FINAL] Health Check Complete.")

if __name__ == "__main__":
    main()
