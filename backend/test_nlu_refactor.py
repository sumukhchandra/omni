import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.ai_core.modules.nlu import NLUModule

def test_nlu():
    nlu = NLUModule()
    
    test_cases = [
        ("play baby song", "PlayMusic", "play_music"),
        ("play baby song on spotify", "PlayMusic", "play_music"),
        ("message mom on instagram", "Social", "send_message"),
        ("send hello to mom", "Social", "send_message"),
        ("search funny cats on youtube", "Search", "search_video"),
        ("order pizza from swiggy", "Commerce", "order_food"),
        ("navigate to home", "Navigation", "navigate"),
        ("note buy milk", "Productivity", "take_note"),
        ("hay atom play baby", "PlayMusic", "play_music"), # User requested test
        ("open calculator", "GenericAction", "open_app") 
    ]
    
    print("--- Starting NLU Verification ---")
    passed = 0
    for cmd, expected_intent, expected_action in test_cases:
        print(f"\nTesting: '{cmd}'")
        try:
            instr, data = nlu.predict_action(cmd)
            action = data.get("action", "unknown")
            
            # Since we can't easily check Intent Class Name from outside without modifying NLU to return it,
            # We check the 'action' field in JSON which maps 1:1 to intents usually.
            
            if action == expected_action or (expected_action == "fallback" and "open_app" in instr):
                 print(f"✅ PASS. Action: {action}")
                 passed += 1
            else:
                 print(f"❌ FAIL. Expected {expected_action}, Got {action}. Data: {data}")
        except Exception as e:
            print(f"❌ ERROR: {e}")

    print(f"\n--- Result: {passed}/{len(test_cases)} Passed ---")

if __name__ == "__main__":
    test_nlu()
