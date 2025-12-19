import sys
import os

# Add project root to path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__)))
sys.path.append(os.path.join(ROOT_DIR, 'atom'))
sys.path.append(os.path.join(ROOT_DIR, 'agent'))

print(f"PYTHONPATH: {sys.path}")

try:
    from atom.ai_core.brains.finalizer_brain import FinalizerBrain
except ImportError as e:
    print(f"FAILED IMPORT: {e}")
    sys.exit(1)

def test_brains():
    print("--- Testing 4-Brain Architecture ---")
    brain = FinalizerBrain()
    
    # Test 1: Simple Open
    cmd = "open calculator"
    print(f"\n[TEST] Command: '{cmd}'")
    success, response = brain.execute(cmd)
    print(f"[RESULT] Success: {success}")
    print(f"[RESULT] Response: {response}")
    
    # Test 2: Unknown
    # cmd = "do a backflip"
    # print(f"\n[TEST] Command: '{cmd}'")
    # success, response = brain.execute(cmd)
    # print(f"[RESULT] Success: {success}")
    # print(f"[RESULT] Response: {response}")

if __name__ == "__main__":
    test_brains()
