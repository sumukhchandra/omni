import pyttsx3
import threading

class TTSModule:
    def __init__(self, rate=150, volume=1.0):
        self.rate = rate
        self.volume = volume
        self.engine = None
        self._init_engine()

    def _init_engine(self):
        try:
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', self.rate)
            self.engine.setProperty('volume', self.volume)
            # Try to set a good voice
            voices = self.engine.getProperty('voices')
            for voice in voices:
                if "david" in voice.name.lower(): # Prefer a male voice if available or adjust as needed
                     self.engine.setProperty('voice', voice.id)
                     break
        except Exception as e:
            print(f"Error initializing TTS Engine: {e}")
            self.engine = None

    def speak(self, text):
        if not self.engine:
            print(f"[MOCK TTS] {text}")
            return
        
        print(f"[TTS] Saying: {text}")
        try:
            # Run in a separate thread to avoid blocking if needed, 
            # but for conversation flow, blocking might be better to avoid talking over user.
            # For now, we use a simple blocking call or a quick run-and-wait approach.
            # pyttsx3 runAndWait blocking is tricky in some loops, but for this linear agent it should be fine.
            self.engine.say(text)
            self.engine.runAndWait()
        except RuntimeError:
             # If loop is already running
             pass

if __name__ == "__main__":
    tts = TTSModule()
    tts.speak("Hello, I am Atom.")
