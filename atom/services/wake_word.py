import speech_recognition as sr
import threading
import time

class WakeWordService:
    def __init__(self, wake_word="atom", on_wake=None):
        self.wake_word = wake_word.lower()
        self.on_wake = on_wake
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.running = False
        self._setup_mic()

    def _setup_mic(self):
        try:
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
        except Exception as e:
            print(f"Error setting up mic for wake word: {e}")

    def start_listening(self):
        self.running = True
        threading.Thread(target=self._listen_loop, daemon=True).start()

    def stop_listening(self):
        self.running = False

    def _listen_loop(self):
        print(f"Waiting for wake word: '{self.wake_word}'...")
        while self.running:
            try:
                with self.microphone as source:
                    # Short timeout for listening to keep loop responsive
                    audio = self.recognizer.listen(source, timeout=2, phrase_time_limit=3)
                
                try:
                    # Use offline pocketsphinx if available, else google (online)
                    # For speed, we want offline, but pocketsphinx requires install.
                    # We will try google for now (slower but works without extra dlls).
                    # OR we can just check if speech contains "atom"
                    text = self.recognizer.recognize_google(audio).lower()
                    # print(f"DEBUG: Heard '{text}'")
                    
                    if self.wake_word in text:
                        print("Wake Word Detected!")
                        if self.on_wake:
                            self.on_wake()
                            
                except sr.UnknownValueError:
                    pass
                except sr.RequestError:
                    pass
                    
            except sr.WaitTimeoutError:
                pass
            except Exception as e:
                print(f"Wake Word Error: {e}")
                time.sleep(1)

if __name__ == "__main__":
    def wake():
        print("I AM AWAKE!")
    
    service = WakeWordService(on_wake=wake)
    service.start_listening()
    
    while True:
        time.sleep(1)
