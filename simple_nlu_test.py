import sys
import os

# Ensure we can import nlu
sys.path.append(os.getcwd())
# Ensure we can import nlu from backend
sys.path.append(os.path.join(os.getcwd(), 'backend', 'ai_core'))

try:
    from modules.nlu import NLUModule
except ImportError:
    print("Could not import NLUModule from backend/ai_core")
    sys.exit(1)

nlu = NLUModule()
print("Initialized NLU")
text = 'open the browser and search for antigravity'
print(f"Testing text: '{text}'")
instruction, data = nlu.predict_action(text)

with open("test_output.txt", "w") as f:
    f.write(f"Instruction: {instruction}\n")
    f.write(f"Data: {data}\n")
print("Written to test_output.txt")
