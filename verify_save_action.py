import sys
import os
import time

# Ensure we can import actions from backend/executor
sys.path.append(os.path.join(os.getcwd(), 'backend', 'executor'))

try:
    from actions import execute_verbose_command
except ImportError:
    print("Could not import actions from backend/executor")
    sys.exit(1)

print("Starting Verification of Save Fix...")
# Verify the fix: using "save it" should now generate a timestamped file
# We simulate the verbose instruction directly to bypass NLU
instruction = "open notepad then type 'Verification Test for Save Fix' then save it"

print(f"Executing Instruction: {instruction}")
logs = execute_verbose_command(instruction)

print("\nExecution Logs:")
for log in logs:
    print(log)

print("\nVerification Complete.")
