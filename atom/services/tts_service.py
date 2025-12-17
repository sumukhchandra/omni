import pyttsx3
import threading

class TTSService:
    def __init__(self):
        try:
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', 170)  # Speed
            self.engine.setProperty('volume', 1.0) # Volume
            
            # Select a decent voice (usually picking the second one on Windows gives a female voice)
            voices = self.engine.getProperty('voices')
            if len(voices) > 1:
                self.engine.setProperty('voice', voices[1].id)
            
            self.lock = threading.Lock()
        except KeyError:
             # Handle cases where voices might not be indexable or init fails
             pass

    def speak(self, text):
        """
        Speaks the text in a non-blocking way (if possible, but pyttsx3 runAndWait is blocking).
        To avoid freezing UI, we run in a thread.
        """
        threading.Thread(target=self._speak_thread, args=(text,)).start()

    def _speak_thread(self, text):
        with self.lock:
            try:
                # Re-initialize for thread safety if needed or just use the lock
                # Pyttsx3 event loop is tricky. Often better to have a dedicated worker.
                # For simple usage:
                self.engine.say(text)
                self.engine.runAndWait()
            except RuntimeError:
                # Engine already running
                pass

if __name__ == "__main__":
    tts = TTSService()
    tts.speak("Hello, I am Atom. How can I help you?")
