import sys
import os

# Add root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.asr import ASRModule
from modules.normalization import NormalizationModule
from modules.nlu import NLUModule
from modules.executor import ActionExecutor

class ECOPipeline:
    def __init__(self):
        print("Initializing pipeline modules...")
        self.asr = ASRModule(model_size="base")
        self.norm = NormalizationModule()
        if os.path.exists("AI/Models/nlu_t5"):
            model_path = "AI/Models/nlu_t5"
        elif os.path.exists("Models/nlu_t5"):
             model_path = "Models/nlu_t5"
        else:
             model_path = "t5-small"
        self.nlu = NLUModule(model_path=model_path)
        self.executor = ActionExecutor(safe_mode=True)
        print("Pipeline initialized.")

    def processed_request(self, text_input=None, audio_file=None, image_path=None):
        logs = []
        raw_text = ""
        
        # 1. Input
        if text_input:
            logs.append(f"[INPUT] Text: {text_input}")
            raw_text = text_input
        elif audio_file:
            logs.append(f"[INPUT] Audio: {audio_file}")
            raw_text = self.asr.transcribe(audio_file)
            logs.append(f"[ASR] Transcribed: {raw_text}")
        else:
            return False, ["No input provided."], [], []

        # 2. Normalization
        clean_text = self.norm.normalize(raw_text)
        logs.append(f"[NORM] Cleaned: {clean_text}")
        
        # 3. NLU
        instruction_text, action_data = self.nlu.predict_action(clean_text)
        
        logs.append(f"[NLU] Predicted Action Data: {action_data}")
        logs.append(f"[NLU] Generated Instruction: {instruction_text}")
        
        # 4. Return Data for Main Executor
        # We explicitly return the instruction_text so main.py can pass it to the executor
        return True, logs, action_data, instruction_text

# Global instance for Flask
pipeline_instance = None

def get_pipeline():
    global pipeline_instance
    if pipeline_instance is None:
        pipeline_instance = ECOPipeline()
    return pipeline_instance

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--text", type=str)
    args = parser.parse_args()
    
    p = get_pipeline()
    s, l, a = p.processed_request(text_input=args.text or "test")
    for log in l:
        print(log)
