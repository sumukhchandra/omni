
import sys
import os
sys.path.append(os.path.abspath("atom"))
from ai_core.modules.nlu import NLUModule

print("--- FINAL 5-TASK VERIFICATION ---")
nlu = NLUModule()

definitions = {
    1: "Hello Atom",
    2: "What is the time?",
    3: "Turn volume up",
    4: "Open Notepad",
    5: "Play Blinding Lights on YouTube"
}

for i in range(1, 6):
    cmd = definitions[i]
    print(f"\nTask {i}: '{cmd}'")
    try:
        instr, data = nlu.predict_action(cmd.lower())
        print(f"  -> Instruction: {instr}")
        print(f"  -> Action Type: {data.get('action')}")
        if data.get('action') == "unknown":
            print("  -> RESULT: FAIL")
        else:
            print("  -> RESULT: SUCCESS")
    except Exception as e:
        print(f"  -> ERROR: {e}")
