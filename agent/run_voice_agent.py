# run_voice_agent.py
import os
import sys
import time
import re
import traceback

# Add paths for atom (AI) and agent (Executor)
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(ROOT_DIR, 'atom'))
sys.path.append(os.path.join(ROOT_DIR, 'agent'))

try:
    from ai_core.modules.asr import ASRModule
    from ai_core.modules.tts import TTSModule
    from ai_core.modules.voice_loop import VoiceLoop
    from ai_core.pipeline import get_pipeline
    from executor.actions import execute_verbose_command
except ImportError as e:
    print(f"Error importing modules: {e}")
    sys.exit(1)

def main():
    print("Initializing Voice Agent...")
    
    # 1. Initialize Modules
    tts = TTSModule()
    tts.speak("Initializing system.")
    
    # Initialize ASR (Whisper) - this might take a moment
    asr = ASRModule(model_size="base") 
    
    voice = VoiceLoop()
    pipeline = get_pipeline()
    
    tts.speak("System ready. Say Hey Atom to start.")
    print("System Ready. Listening for 'Hey Atom'...")
    
    WAKE_WORD_REGEX = r"(hey|hay|hi|hello)\s*atom"
    
    while True:
        try:
            # --- 1. Listen for Wake Word ---
            # Record a short snippet (e.g., 3 seconds) to check for wake word
            # Optimization: In a real production system, we'd use a streaming buffer or Porcupine.
            # For this MVP, we record 3s chunks.
            print("\nListening for wake word...")
            audio_file = voice.record_audio(duration=3, filename="wake_check.wav")
            
            # Transcribe
            text = asr.transcribe(audio_file)
            print(f"Heard: {text}")
            
            # Check Wake Word
            if re.search(WAKE_WORD_REGEX, text.lower()):
                print("Wake Word Detected!")
                
                # --- 2. Wake Word Response ---
                # User Requirement: "whenever we say hay atom it should speek the user name 'hay user how can i help you'"
                # We'll use a generic "User" for now as we don't have login context in this script.
                tts.speak("Hey User, how can I help you?")
                
                # --- 3. Listen for Command ---
                print("Listening for command...")
                command_file = voice.record_audio(duration=5, filename="command_input.wav")
                command_text = asr.transcribe(command_file)
                print(f"Command Heard: {command_text}")
                
                if not command_text.strip():
                    tts.speak("I didn't hear anything.")
                    continue
                
                # --- 4. Acknowledge Command ---
                # User Requirement: "when he say hay atom do this work then the atom should day hay user i will do it"
                tts.speak("Hey User, I will do it.")
                
                # --- 5. Process & Execute ---
                # Use the existing pipeline
                success, logs, action_data, instructions_str = pipeline.processed_request(text_input=command_text)
                
                if instructions_str:
                    print(f"Plan: {instructions_str}")
                    # Execute
                    execute_verbose_command(instructions_str)
                    tts.speak("Task completed.")
                else:
                    tts.speak("I'm sorry, I couldn't understand what to do.")
            
            # Simple sleep to prevent rapid looping if no wake word found
            # (though recording itself blocks for 3s, so minimal sleep needed)
            # time.sleep(0.5) 
            
        except KeyboardInterrupt:
            print("\nStopping Voice Agent.")
            break
        except Exception as e:
            print(f"Error in Voice Loop: {e}")
            traceback.print_exc()
            tts.speak("An error occurred.")
            time.sleep(2)

if __name__ == "__main__":
    main()
