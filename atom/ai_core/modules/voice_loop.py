try:
    import sounddevice as sd
    import numpy as np
except ImportError:
    sd = None
    np = None

import wave
import os
import time

class VoiceLoop:
    def __init__(self, samplerate=16000, channels=1):
        self.samplerate = samplerate
        self.channels = channels
        self.mock = (sd is None) or (np is None)
        if self.mock:
             print("WARNING: 'sounddevice' or 'numpy' missing. Voice recording will be mocked.")

    def record_audio(self, duration=5, filename="temp_audio.wav"):
        """
        Records audio for a fixed duration.
        """
        if self.mock:
            print(f"[MOCK] Recording for {duration} seconds... (Simulated)")
            time.sleep(duration)
            # Create a dummy file if it plays nice with other modules
            with open(filename, "w") as f:
                f.write("mock audio data")
            return filename

        print(f"Recording for {duration} seconds...")
        recording = sd.rec(int(duration * self.samplerate), 
                           samplerate=self.samplerate, 
                           channels=self.channels,
                           dtype='float32')
        sd.wait()  # Wait until recording is finished
        
        # Save as WAV
        # Convert to 16-bit PCM for compatibility
        data = (recording * 32767).astype(np.int16)
        
        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(2) # 2 bytes = 16 bit
            wf.setframerate(self.samplerate)
            wf.writeframes(data.tobytes())
            
        print("Recording complete.")
        return filename

if __name__ == "__main__":
    vl = VoiceLoop()
    vl.record_audio(duration=3, filename="test_rec.wav")
