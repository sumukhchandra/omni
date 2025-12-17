
import sys
import os

# Ensure we can import from atom/ai_core
sys.path.append(os.getcwd())

from atom.ai_core.modules.nlu import NLUModule

def test_nlu(text):
    print(f"\n--- Testing: '{text}' ---")
    try:
        nlu = NLUModule()
        
        # Test Preprocessing directly
        pre = nlu.preprocess_text(text)
        print(f"Preprocessed: '{pre}'")
        
        # Test Logic
        res = nlu.predict_action(text)
        print(f"Result: {res}")
        
    except Exception as e:
        print(f"CRASH: {e}")
        import traceback
        traceback.print_exc()

test_nlu("hay atom can you play sond")
test_nlu("play song")
