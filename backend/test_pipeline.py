import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'ai_core'))

try:
    from pipeline import get_pipeline
    print("Initializing pipeline...")
    p = get_pipeline()
    print("Pipeline initialized.")
    print("Running request...")
    result = p.processed_request(text_input="Hello")
    print(f"Result type: {type(result)}")
    print(f"Result length: {len(result)}")
    print(result)
except Exception as e:
    import traceback
    traceback.print_exc()
