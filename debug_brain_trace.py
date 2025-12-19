import sys
import os
import time

# Add project root to path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__)))
sys.path.append(os.path.join(ROOT_DIR, 'atom'))
sys.path.append(os.path.join(ROOT_DIR, 'agent'))

try:
    from ai_core.brains.knowledge_brain import KnowledgeBrain
    from ai_core.brains.control_brain import ControlBrain
except ImportError as e:
    print(f"IMPORT ERROR: {e}")
    sys.exit(1)

def debug_trace(command):
    print(f"\n--- DEBUG TRACE: '{command}' ---")
    
    # 1. Test NLU
    kb = KnowledgeBrain()
    try:
        verbal, action_data = kb.think(command)
        print(f"[NLU] Verbal: {verbal}")
        print(f"[NLU] Action Data: {action_data}")
    except Exception as e:
        print(f"[NLU] ERROR: {e}")
        return

    # 2. Test Control
    cb = ControlBrain()
    print("[CONTROL] Attempting execution...")
    try:
        success, logs = cb.act([action_data])
        print(f"[CONTROL] Success: {success}")
        print("[CONTROL] Logs:")
        for l in logs:
            print(f"  - {l}")
    except Exception as e:
        print(f"[CONTROL] ERROR: {e}")

if __name__ == "__main__":
    with open("trace_log.txt", "w", encoding="utf-8") as f:
        sys.stdout = f
        debug_trace("open notepad")
        debug_trace("type hello world")
