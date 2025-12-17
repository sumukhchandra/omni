
import sys
import os
sys.path.append(os.path.abspath("atom"))
from ai_core.modules.nlu import NLUModule

nlu = NLUModule()

tests = [
    "turn volume up",
    "mute my system",
    "what is the time",
    "play next song",
    "open notepad",
    "hello atom"
]

print("--- NLU Verification of 'Perfect' Rules ---")
for text in tests:
    try:
        instr, data = nlu.predict_action(text)
        print(f"\nInput: '{text}'")
        print(f"Instruction: {instr}")
        print(f"Action Data: {data}")
    except Exception as e:
        print(f"Failed '{text}': {e}")
