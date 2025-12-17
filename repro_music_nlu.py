import sys
import os

# Setup paths
sys.path.append(os.path.abspath("atom"))
sys.path.append(os.path.abspath("backend"))

from atom.ai_core.modules.nlu import NLUModule

def test_nlu():
    print("Initializing NLU...")
    nlu = NLUModule()
    
    test_cases = [
        "play baby song",
        "play song",
        "play music",
        "open spotify and play baby song"
    ]
    
    for text in test_cases:
        print(f"\n--- Testing: '{text}' ---")
        try:
            plan, data = nlu.predict_action(text)
            print(f"Plan: {plan}")
            print(f"Data: {data}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    test_nlu()
