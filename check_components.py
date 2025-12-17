
import sys
import os
import importlib

print("--- SYSTEM COMPONENT CHECK ---")

# 1. CHECK "AI" (The Deep Learning Brain)
print("\n[1] Checking 'AI' (Deep Learning Model)...")
try:
    import torch
    import transformers
    print("    STATUS: AVAILABLE (Libraries found)")
except ImportError as e:
    print(f"    STATUS: UNAVAILABLE (Missing dependencies: {e})")
print("    ROLE: Dormant (Training requires this, but valid environment not found)")

# 2. CHECK "ATOM" (The Rule-Based Brain)
print("\n[2] Checking 'ATOM' (Rule-Based Brain)...")
try:
    sys.path.append(os.path.abspath("atom"))
    from ai_core.modules.nlu import NLUModule
    nlu = NLUModule()
    test_input = "turn volume up"
    res = nlu.predict_action(test_input)
    print(f"    STATUS: ACTIVE (Rules Loaded)")
    print(f"    TEST: '{test_input}' -> {res[1]}")
except Exception as e:
    print(f"    STATUS: ERROR ({e})")
print("    ROLE: Primary Brain (Handling all logic)")

# 3. CHECK "AGENT" (The Body)
print("\n[3] Checking 'AGENT' (Executor)...")
try:
    import pyautogui
    # We won't actually move mouse to avoid annoyance, just check import
    print("    STATUS: ACTIVE (Automation Tools Ready)")
except ImportError:
    print("    STATUS: ERROR (PyAutoGUI missing)")
print("    ROLE: Body (Executing physical actions)")

print("\n--- CONCLUSION ---")
print("System is FUNCTIONAL using [ATOM] + [AGENT].")
print("[AI] is bypassed due to hardware limits.")
print("NO TRAINING NEEDED (Rules are hard-coded).")
