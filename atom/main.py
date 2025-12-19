import sys
import os
import threading
import time

# Ensure project root is in path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(ROOT_DIR, 'atom'))
sys.path.append(os.path.join(ROOT_DIR, 'agent'))

# --- Import Services ---
try:
    from ai_core.brains.finalizer_brain import FinalizerBrain
except ImportError as e:
    print(f"⚠️  Finalizer Brain not found: {e}")
    FinalizerBrain = None

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
finalizer = FinalizerBrain() if FinalizerBrain else None
audio_service = AudioService() if AudioService else None
tts_service = TTSService() if TTSService else None
wake_word_service = WakeWordService() if WakeWordService else None
    
# --- Core Logic ---
def process_text_command(text):
    if not finalizer:
        return "I am lobotomized (Finalizer Brain Missing) 😵"
    
    # Execute via Finalizer Brain
    try:
        success, response_msg = finalizer.execute(text)
    except Exception as e:
        print(f"❌ [Main] Finalizer Crash: {e}")
        import traceback
        traceback.print_exc()
        success, response_msg = False, f"I crashed. Error: {e}"
    
    if tts_service:
        tts_service.speak(response_msg)
        
    return response_msg

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
    # --- Single Instance Lock ---
    # Try to create a mutex to ensure only one instance runs.
    # On Windows, we can use a Named Mutex via ctypes.
    import ctypes
    from ctypes import wintypes
    
    kernel32 = ctypes.windll.kernel32
    mutex_name = "Global\\AtomAgentMutex_v4"
    
    # CreateMutexW(security_attributes, initial_owner, name)
    mutex = kernel32.CreateMutexW(None, False, mutex_name)
    last_error = kernel32.GetLastError()
    
    ERROR_ALREADY_EXISTS = 183
    
    if last_error == ERROR_ALREADY_EXISTS:
        print("⚠️  Another instance of Atom is already running. Exiting.")
        time.sleep(2) # Show message briefly if running in console
        sys.exit(0)

    print("Starting ATOM AI (Python 3.10)...")

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
