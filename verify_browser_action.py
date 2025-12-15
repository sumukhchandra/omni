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

print("Starting Verification of Browser Automation...")
# Verify: "open the browser" -> opens google.com -> "search for antigravity" -> types it
# We simulate the instruction sequence as it might come from NLU (or slightly cleaned)
# NLU output: "Open the browser and search for antigravity"
# We'll split it or just feed a verbose chain:
instruction = "open the browser then search for antigravity"

print(f"Executing Instruction: {instruction}")
logs = execute_verbose_command(instruction)

print("\nExecution Logs:")
for log in logs:
    print(log)

print("\nVerification Complete.")
