import sys
import os

# Setup path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.nlu.rule_based import RuleBasedNLU
from backend.executor import ActionExecutor

def test_atom():
    print("🧪 Testing ATOM Core Logic...")
    
    nlu = RuleBasedNLU()
    executor = ActionExecutor()
    
    test_inputs = [
        "open google",
        "play believer",
        "search for python wikipedia"
    ]
    
    for i, text in enumerate(test_inputs, 1):
        print(f"\n[{i}] Input: '{text}'")
        
        # 1. Understand
        intent = nlu.parse(text)
        print(f"   🧠 NLU: {intent}")
        
        # 2. Act (We will simulate execution to avoid spamming windows, or just run it)
        # For this test, we will actually RUN it so the user sees it work.
        print("   💪 Executing...")
        response = executor.execute(intent)
        print(f"   🗣️ Response: {response}")

if __name__ == "__main__":
    test_atom()
