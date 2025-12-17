import pyttsx3
# import sounddevice as sd
# import numpy as np

def test_tts():
    print("Testing TTS...")
    try:
        engine = pyttsx3.init()
        engine.say("Testing Text to Speech system.")
        engine.runAndWait()
        print("TTS Test Passed.")
    except Exception as e:
        print(f"TTS Test Failed: {e}")

def test_mic():
    print("Testing Microphone (Recording 3s)...")
    try:
        import sounddevice as sd
        import numpy as np
        fs = 16000
        seconds = 3
        # Record
        myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=1)
        sd.wait()
        print("Recording Complete. Playing back...")
        sd.play(myrecording, fs)
        sd.wait()
        print("Mic Test Passed (if you heard your voice).")
    except Exception as e:
        print(f"Mic Test Failed: {e}")

if __name__ == "__main__":
    test_tts()
    # test_mic()
