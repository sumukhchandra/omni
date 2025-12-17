
import sys
import os

sys.path.append(os.getcwd())
# Suppress heavy logs
os.environ["TRANSFORMERS_VERBOSITY"] = "error"

from atom.ai_core.modules.nlu import NLUModule

def test(text):
    print(f"TST: '{text}'")
    nlu = NLUModule()
    
    clean = nlu.preprocess_text(text)
    print(f"PP: '{clean}'")
    
    for intent in nlu.router.intents:
        if intent.match(clean):
            print(f"MATCH: {intent.name}")
            res = intent.extract(clean)
            if res:
                print(f"EXTRACTED: {res[1]['action']}")
                return
            else:
                 print(f"EXTRACT FAIL: {intent.name}")

    print("Result: UNKNOWN")

test("play baby song")
