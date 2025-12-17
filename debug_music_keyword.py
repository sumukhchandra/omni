
import sys
import os

# Ensure we can import from atom/ai_core
sys.path.append(os.getcwd())

from atom.ai_core.modules.nlu import NLUModule

def test_nlu(text):
    print(f"\n--- Testing: '{text}' ---")
    try:
        nlu = NLUModule()
        res = nlu.predict_action(text)
        print(f"Result: {res}")
        
    except Exception as e:
        print(f"CRASH: {e}")

test_nlu("music")
test_nlu("song")
