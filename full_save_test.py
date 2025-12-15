import sys
import os
import time

# Setup paths
sys.path.append(os.path.join(os.getcwd(), 'backend', 'ai_core'))
sys.path.append(os.path.join(os.getcwd(), 'backend', 'executor'))

try:
    from modules.nlu import NLUModule
    from actions import execute_verbose_command
except ImportError as e:
    print(f"Import failed: {e}")
    sys.exit(1)

def test_flow():
    print("--- Starting End-to-End Save Test ---")
    
    # 1. Initialize NLU
    print("1. Initializing NLU...")
    nlu = NLUModule() # Will likely use Mock mode which is fine/preferred for now
    
    # 2. Get Plan
    user_input = "note hello world"
    print(f"2. Processing User Input: '{user_input}'")
    instruction, data = nlu.predict_action(user_input)
    print(f"   Generated Instruction: {instruction}")
    
    # 3. Execute
    print("3. Executing Plan...")
    logs = execute_verbose_command(instruction)
    
    print("\n--- Execution Logs ---")
    for log in logs:
        print(log)
        
    print("\n--- Test Finished ---")

if __name__ == "__main__":
    test_flow()
