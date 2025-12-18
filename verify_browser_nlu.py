import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'atom'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from atom.ai_core.modules.nlu import NLUModule

def test_browser_commands():
    nlu = NLUModule()
    
    test_cases = [
        "open new tab",
        "type hello world",
        "search for python on google",
        "select first option",
        "select 2nd option",
        "close tab",
        "navigate to search bar" # Indirectly tested via search
    ]
    
    print("--- Testing Browser NLU ---")
    for text in test_cases:
        print(f"\nInput: '{text}'")
        s, data = nlu.predict_action(text)
        print(f"Plan: {s}")
        print(f"Data: {data}")
        
    print("\n--- Verification Complete ---")

if __name__ == "__main__":
    test_browser_commands()
