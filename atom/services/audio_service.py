import speech_recognition as sr
import threading

class AudioService:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Adjust for ambient noise once at startup (optional but good)
        # with self.microphone as source:
        #     self.recognizer.adjust_for_ambient_noise(source)

    def listen_and_recognize(self):
        """
        Listens to the microphone and returns text.
        Returns: (text, error_message)
        """
        try:
            with self.microphone as source:
                print("🎤 Listening...")
                # Short timeout to not hang forever
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
            
            print("Processing audio...")
            text = self.recognizer.recognize_google(audio)
            print(f"Recognized: {text}")
            return text, None
        
        except sr.WaitTimeoutError:
            return None, "Timeout: No speech detected."
        except sr.UnknownValueError:
            return None, "Could not understand audio."
        except sr.RequestError as e:
            return None, f"Service error: {e}"
        except Exception as e:
            return None, f"Error: {e}"

if __name__ == "__main__":
    service = AudioService()
    text, error = service.listen_and_recognize()
    if text:
        print(f"Final Text: {text}")
    else:
        print(f"Failed: {error}")
