import os
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

try:
    import torch
    from transformers import T5ForConditionalGeneration, T5Tokenizer
    USE_ML = True
except ImportError:
    print("⚠️  ML Libraries not found. Switching to Rule-Based Fallback.")
    USE_ML = False
    from models.nlu.rule_based import RuleBasedNLU

MODEL_DIR = os.path.join("models", "nlu", "saved_model")

def load_brain():
    if USE_ML:
        try:
            tokenizer = T5Tokenizer.from_pretrained(MODEL_DIR, legacy=False)
            model = T5ForConditionalGeneration.from_pretrained(MODEL_DIR)
            return ("ML", tokenizer, model)
        except:
            print("⚠️  Model not found. Switching to Rule-Based Fallback.")
            return ("RULE", RuleBasedNLU(), None)
    else:
        return ("RULE", RuleBasedNLU(), None)

def predict(text, engine, tokenizer=None, model=None):
    if engine == "ML":
        input_ids = tokenizer(text, return_tensors="pt").input_ids
        outputs = model.generate(input_ids)
        return tokenizer.decode(outputs[0], skip_special_tokens=True)
    else:
        # Rule Based
        result = tokenizer.parse(text) # In this case 'tokenizer' is the RuleBasedNLU instance
        if result["intent"] == "UNKNOWN":
            return "I didn't understand that."
        
        entity_str = ", ".join([f"{k}={v}" for k, v in result["entities"].items()])
        return f"INTENT: {result['intent']} | ENTITIES: {entity_str}"

def main():
    brain_type, component1, component2 = load_brain()
    print(f"🧠 ATOM NLU Loaded [{brain_type} MODE]. Type a command.")
    print("-" * 50)

    while True:
        text = input("User: ")
        if text.lower() in ["exit", "quit", "q"]:
            break
        
        response = predict(text, brain_type, component1, component2)
        print(f"Atom: {response}")

if __name__ == "__main__":
    main()
