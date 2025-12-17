import sys
import importlib
import platform


GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"

def check_import(module_name, display_name=None):
    if not display_name:
        display_name = module_name
    
    print(f"Checking {display_name}...", end=" ")
    try:
        importlib.import_module(module_name)
        print(f"{GREEN}OK{RESET}")
        return True
    except ImportError as e:
        print(f"{RED}MISSING ({e}){RESET}")
        return False

def main():
    print(f"🩺 ATOM AI Doctor (Python {sys.version.split()[0]})")
    print("-" * 40)
    
    all_good = True
    
    # Core
    all_good &= check_import("PyQt5", "UI Framework (PyQt5)")
    
    # Audio
    all_good &= check_import("speech_recognition", "Ears (SpeechRecognition)")
    all_good &= check_import("pyaudio", "Microphone Driver (PyAudio)")
    all_good &= check_import("pyttsx3", "Voice (TTS)")
    

    # Brain (Optional)
    print("Checking Brain Core (PyTorch)...", end=" ")
    try:
        importlib.import_module("torch")
        print(f"{GREEN}OK{RESET}")
    except ImportError:
        print(f"{YELLOW}WARNING (Using Rule-Based Brain){RESET}")
        # do not set all_good = False for this
    
    # ...
    
    print("-" * 40)
    if all_good:
        print(f"{GREEN}✅ System is HEALTHY. You can run 'run_atom.bat' now.{RESET}")
    else:
        print(f"{RED}❌ System issues detected. Please wait for installation to finish.{RESET}")

if __name__ == "__main__":
    main()
