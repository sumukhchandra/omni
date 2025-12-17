import sys
import os
import threading

# Ensure project root is in path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(ROOT_DIR, 'atom'))
sys.path.append(os.path.join(ROOT_DIR, 'agent'))

# --- Import Services ---
try:
    from ai_core.pipeline import get_pipeline
except ImportError:
    print("⚠️  Warning: AI Pipeline not found.")
    get_pipeline = None

try:
    from executor.actions import execute_verbose_command
except ImportError:
    print("⚠️  Agent Executor not found.")
    execute_verbose_command = None

try:
    from services.audio_service import AudioService
except ImportError:
    print("⚠️  Audio Service not found.")
    AudioService = None

try:
    from services.tts_service import TTSService
except ImportError:
    print("⚠️  TTS Service not found.")
    TTSService = None

try:
    from services.wake_word import WakeWordService
except ImportError:
    print("⚠️  Wake Word Service not found.")
    WakeWordService = None

from ui.desktop.floating_icon import start_ui

# --- Initialize Brain & Body ---
pipeline = get_pipeline() if get_pipeline else None
audio_service = AudioService() if AudioService else None
tts_service = TTSService() if TTSService else None
wake_word_service = WakeWordService() if WakeWordService else None
    
# --- Core Logic ---
def process_text_command(text):
    if not pipeline:
        return "I am lobotomized (Pipeline Missing) 😵"
    
    # 1. Understand & Plan (Atom)
    # pipeline returns: success, logs, action_data, strict_instruction_string
    success, logs, action_data, instructions_str = pipeline.processed_request(text_input=text)
    
    if not instructions_str:
        response = "I couldn't understand what to do."
        if tts_service: tts_service.speak(response)
        return response
    
    # 2. Act (Agent)
    if execute_verbose_command:
        # execute_verbose_command returns a list of logs
        exec_logs = execute_verbose_command(instructions_str)
        action_response = f"Done: {instructions_str}"
    else:
        action_response = "Agent Executor missing, cannot act."
    
    # 3. Respond
    if tts_service:
        tts_service.speak("Task completed.")
        
    return action_response

def handle_voice_trigger(ui_callback_update_status, ui_callback_add_user_msg, ui_callback_add_atom_msg):
    """
    Runs listening in a separate thread to not freeze UI.
    """
    if not audio_service:
        ui_callback_add_atom_msg("Audio service unavailable.")
        return

    def listen_job():
        ui_callback_update_status(True) # Set listening icon
        try:
            text, error = audio_service.listen_and_recognize()
            if text:
                ui_callback_add_user_msg(text)
                response = process_text_command(text)
                ui_callback_add_atom_msg(response)
            else:
                if error:
                    # ui_callback_add_atom_msg(f"👂 {error}")
                    pass
        except Exception as e:
            print(f"Voice Error: {e}")
        finally:
            ui_callback_update_status(False) # Reset icon

    thread = threading.Thread(target=listen_job)
    thread.start()

# --- Entry Point ---
if __name__ == "__main__":
    print("🧠 Starting ATOM AI (Python 3.10)...")

    # Define the callback wrapper for the UI to trigger voice listening
    def on_mic_click(gui_ref):
        handle_voice_trigger(
            gui_ref.set_listening,
            lambda text: gui_ref.add_message("You", text),
            lambda text: gui_ref.add_message("Atom", text)
        )

    # Launch the UI
    # Pass the wake service so the UI can connect the signal bridge
    start_ui(
        on_submit_callback=process_text_command, 
        on_mic_callback=on_mic_click,
        wake_service=wake_word_service
    )
