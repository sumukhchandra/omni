import os

class ASRModule:
    def __init__(self, model_size="base", device=None):
        self.output_mock = False
        try:
            import whisper
            import torch
            if device is None:
                self.device = "cuda" if torch.cuda.is_available() else "cpu"
            else:
                self.device = device
            print(f"Loading Whisper model '{model_size}' on {self.device}...")
            self.model = whisper.load_model(model_size, device=self.device)
            print("Whisper model loaded.")
        except ImportError as e:
            print(f"WARNING: ASR dependencies missing ({e}). Using Mock Mode.")
            self.output_mock = True

    def transcribe(self, audio_path_or_array):
        if self.output_mock:
            return "This is a mock transcription because torch/whisper is missing."
        result = self.model.transcribe(audio_path_or_array)
        return result["text"].strip()

if __name__ == "__main__":
    asr = ASRModule(model_size="tiny")
    print("ASR Module initialized.")
    if asr.output_mock:
        print(asr.transcribe("dummy.wav"))
