#!/usr/bin/env python3
"""
Everything-In-Screen: cross-platform automation server.
Now strictly controlled by Verbose AI Instructions.
"""
import os, sys, time, json, traceback, subprocess, platform
from pathlib import Path
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
# from PIL import Image, ImageDraw, ImageFont # Lazy import now
# import numpy as np # Lazy import now
try:
    import cv2
    import pytesseract
except ImportError:
    cv2 = None
    pytesseract = None

# Optional automation libs
try:
    import pyautogui
except Exception:
    pyautogui = None

ROOT = Path(__file__).resolve().parent
SS = ROOT / "screenshots"
ANN = SS / "annotated"
SS.mkdir(exist_ok=True)
ANN.mkdir(exist_ok=True)

# Config
EXECUTE = True # Force execution for this MVP stage as requested
DRY_RUN = False
TESSERACT_CMD = os.environ.get("TESSERACT_CMD", "tesseract")
if pytesseract:
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD

def capture():
    try:
        from PIL import Image
        import mss
        with mss.mss() as s:
            m = s.monitors[1]
            g = s.grab(m)
            return Image.frombytes("RGB", g.size, g.rgb)
    except Exception:
        if pyautogui:
            from PIL import Image
            import numpy as np
            return Image.fromarray(np.array(pyautogui.screenshot()))
        raise

def save(img, name: str):
    from PIL import Image
    p = SS / name
    img.save(str(p))

def ocr(img):
    from PIL import Image
    return pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)

# --- OPTIMIZATION HELPERS ---
def run_speak(text):
    try:
        import pyttsx3
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()
    except:
        pass

def smart_wait_for_app(app_name_fragment, timeout=10):
    """
    Waits for a process matching the name to appear.
    If found early, returns immediately (Fast).
    If not, waits until timeout.
    """
    try:
        import psutil
        start_time = time.time()
        print(f"[SMART WAIT] Looking for process: {app_name_fragment}")
        
        while (time.time() - start_time) < timeout:
            for proc in psutil.process_iter(['name']):
                try:
                    if app_name_fragment.lower() in proc.info['name'].lower():
                        print(f"[SMART WAIT] Found {proc.info['name']}! Ready in {time.time() - start_time:.2f}s")
                        return True
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
            time.sleep(0.5) # Poll frequency
        return False
    except ImportError:
         time.sleep(3.0) # Fallback if psutil fails
         return False

def platform_open_app(app_name: str):
    plat = platform.system().lower()
    try:
        if plat == "darwin":
            subprocess.run(["open", "-a", app_name], check=False)
        elif plat == "windows":
            subprocess.run(["cmd", "/c", "start", "", app_name], shell=False)
        else:
            subprocess.run(["/usr/bin/xdg-open", app_name], check=False)
        
        # SMART WAIT LOGIC
        if "notepad" in app_name.lower(): smart_wait_for_app("notepad")
        elif "spotify" in app_name.lower(): 
             smart_wait_for_app("spotify")
             time.sleep(2.0) # Extra wait for UI load
        elif "chrome" in app_name.lower(): smart_wait_for_app("chrome")
        elif "calculator" in app_name.lower(): smart_wait_for_app("calc")
        else:
             time.sleep(2.0) # Default for unknown apps
             
        return True
    except Exception:
        return False

def execute_step(step_text):
    """
    Executes a single step from the verbose instruction.
    e.g. "click windows", "type baby", "search for spotify"
    """
    step = step_text.strip().lower()
    print(f"[EXECUTOR] Executing step: {step}")
    
    if pyautogui is None:
        return f"Error: PyAutoGUI not initialized. Cannot execute '{step}'"
    
    # Handle "click windows buttion" (typo included)
    if "click windows" in step:
        if pyautogui: 
            pyautogui.press('win')
            time.sleep(0.5) # Reduced from 1.0
        return "Pressed Windows key"

    if "search for" in step:
        query = step.split("search for")[1].strip()
        if pyautogui: pyautogui.write(query, interval=0.05) # Faster typing
        time.sleep(0.2)
        return f"Typed '{query}'"

    if "type" in step and "search" not in step: # avoid conflict with above if vague
        text = step.split("type")[1].strip()
        if pyautogui: pyautogui.write(text, interval=0.05) # Faster typing
        return f"Typed '{text}'"

    # --- HOTKEY SUPPORT ---
    if "press " in step:
        key_seq = step.split("press ")[1].strip()
        if pyautogui:
             # Handle combinations like "ctrl+t"
             if "+" in key_seq:
                 keys = key_seq.split("+")
                 pyautogui.hotkey(*keys)
             else:
                 # Map abstract keys to pyautogui
                 key_map = {
                     "volume_up": "volumeup",
                     "volume_down": "volumedown", 
                     "volume_mute": "volumemute",
                     "playpause": "playpause",
                     "nexttrack": "nexttrack",
                     "prevtrack": "prevtrack",
                     "windows": "win",
                     "enter": "enter",
                     "tab": "tab",
                     "space": "space",
                     "esc": "esc",
                     "backspace": "backspace"
                 }
                 p_key = key_map.get(key_seq, key_seq)
                 pyautogui.press(p_key)
             time.sleep(0.5) # Allow UI to react
        return f"Pressed '{key_seq}'"

    # --- VOICE UPGRADE (ASYNC) ---
    if "speak" in step or "say" in step:
        text = step.replace("speak", "").replace("say", "").strip()
        import threading
        t = threading.Thread(target=run_speak, args=(text,))
        t.daemon = True
        t.start()
        return f"Speaking (Async): '{text}'"

    # --- SYSTEM ADMIN UPGRADE ---
    if "check" in step:
        import psutil
        if "battery" in step:
            battery = psutil.sensors_battery()
            percent = battery.percent if battery else "Unknown"
            return f"Inform: Battery is at {percent}%"
        if "cpu" in step:
            usage = psutil.cpu_percent(interval=1)
            return f"Inform: CPU Usage is {usage}%"
        if "memory" in step or "ram" in step:
            mem = psutil.virtual_memory()
            return f"Inform: RAM Usage is {mem.percent}%"

    if "clean temp" in step:
        import shutil
        temp_dir = os.environ.get('TEMP')
        if temp_dir:
            try:
                # localized cleanup for safety, just counting files
                count = len(os.listdir(temp_dir))
                return f"Inform: Found {count} temp files. (Cleanup simulation for safety)"
            except:
                pass
        return "Cleaned Temp Files (Simulated)"

    if "inform " in step:
        info = step.split("inform ")[1].strip()
        return f"Info: {info}"

    # Handle "typr" (typo included)
    if "typr" in step:
         text = step.split("typr")[1].strip()
         if pyautogui: pyautogui.write(text, interval=0.05)
         return f"Typed '{text}'"

    if "open it" in step or "click open" in step:
        if pyautogui: pyautogui.press('enter')
        time.sleep(1.0) 
        return "Pressed Enter (Open App)"

    if "open " in step and "open it" not in step and "click open" not in step:
        app_name = step.split("open ")[1].strip()
        
        # Handle generic "open browser" -> Open Google
        if "browser" in app_name.lower():
             print(f"[EXECUTOR] Generic 'browser' requested. Opening default browser.")
             plat = platform.system().lower()
             if plat == "windows":
                 subprocess.run(["cmd", "/c", "start", "https://google.com"], shell=False)
             elif plat == "darwin":
                 subprocess.run(["open", "https://google.com"], check=False)
             else:
                 subprocess.run(["xdg-open", "https://google.com"], check=False)
             smart_wait_for_app("chrome") # wait for chrome
             return "Opened Default Browser to Google"

        print(f"[EXECUTOR] Attempting to open app: {app_name}")
        if platform_open_app(app_name):
             # smart wait is inside platform_open_app
             return f"Opened App '{app_name}' via platform command"
        else:
             return f"Failed to open '{app_name}'"

    if "navigate to search bar" in step:
        # Heuristic: Ctrl+L is standard for Browser URL and Spotify Search.
        if pyautogui: 
            pyautogui.hotkey('ctrl', 'l')
            time.sleep(1.0)
        return "Pressed Ctrl+L (Focus Search)"

    if "click on search" in step:
        # If Ctrl+K didn't work, we can try clicking top-left/center or Tab cycling
        # preventing "click on search" from doing nothing
        if pyautogui:
            pyautogui.press('tab') # Try tabbing once in case we are close
            time.sleep(0.2)
        return "Pressed Tab (Attempt Focus Search)"

    if "click on " in step:
        target = step.split("click on ")[-1].strip()
        print(f"[EXECUTOR] requested click on: {target}")
        
        # --- OVERRIDE: General 'Press Enter' for Search Results ---
        # User requested: "it is not only siddu it is for search result"
        # We assume if visual click fails, we just want to select the result.
        pass # Fallthrough to visual click first

        
        # --- NEW VISUAL CLICK LOGIC with TESSERACT ---
        best_match = None
        best_ratio = 0.0
        
        try:
            # Re-use existing ocr() function or call directly
            # ocr() function in this file returns image_to_data(output_type=DICT)
            # Need to capture screen first
            img = capture()
            ocr_res = ocr(img) # Returns dict of lists
            
            # ocr_res keys: left, top, width, height, text, conf...
            n_boxes = len(ocr_res['text'])
            
            from difflib import SequenceMatcher
            target_lower = target.lower()
            
            for i in range(n_boxes):
                text = ocr_res['text'][i].strip()
                if not text: continue
                
                # Check confidence
                try:
                    conf = int(ocr_res['conf'][i])
                except:
                    conf = 0
                if conf < 30: continue 

                text_lower = text.lower()
                ratio = SequenceMatcher(None, target_lower, text_lower).ratio()
                
                # Boost ratio if exact substring
                if target_lower in text_lower:
                    ratio += 0.3 # Boost for substring
                
                if ratio > best_ratio:
                    best_ratio = ratio
                    best_match = {
                        "text": text,
                        "rect": [ocr_res['left'][i], ocr_res['top'][i], ocr_res['width'][i], ocr_res['height'][i]]
                    }
                    
            print(f"[EXECUTOR] Best visual match for '{target}': {best_match} (Score: {best_ratio:.2f})")
            
            # Click if found
            if best_match and best_ratio > 0.6:
                rect = best_match['rect'] # [x, y, w, h]
                cx = rect[0] + rect[2] / 2
                cy = rect[1] + rect[3] / 2
                
                if pyautogui:
                    print(f"[EXECUTOR] Clicking at ({cx}, {cy})")
                    pyautogui.moveTo(cx, cy, duration=0.5)
                    pyautogui.click()
                    return f"Clicked on visual match: '{best_match['text']}'"
            else:
                 print("[EXECUTOR] No confident visual match found. Falling back to heuristic.")
                 
        except Exception as e:
            print(f"[EXECUTOR] Tesseract Visual Click Error: {e}")
            import traceback
            traceback.print_exc()

        # --- FALLBACK TO OLD LOGIC ---
        
        if "message bar" in target:
             # Heuristic for message bar: Just wait/implicit focus
             time.sleep(0.5) 
             return "Focused Message Bar (Implicitly)"
             
        if "send" in target:
            # Heuristic for send: Enter usually sends
            if pyautogui:
                pyautogui.press('enter')
                time.sleep(0.5)
            return "Clicked Send (Enter)"

        if pyautogui:
             # Just Press Enter (Simple Selection Fallback)
             print(f"[EXECUTOR] Fallback for '{target}': Pressing Enter")
             pyautogui.press('enter') 
             time.sleep(1.0)
        return f"Pressed Enter (Fallback for '{target}')"

    if "save it" in step or "save file" in step:
        filename = "unknown_file"
        if pyautogui:
            # Ensure we are focused on the doc
            pyautogui.click() 
            time.sleep(0.5)
            
            # Force "Save As" using Menu sequence (Alt -> F -> A)
            # This is more robust than Ctrl+Shift+S which can vary by app/version
            pyautogui.press('alt')
            time.sleep(0.2)
            pyautogui.press('f')
            time.sleep(0.2)
            pyautogui.press('a')
            time.sleep(4.0) 
            
            # Use timestamp to avoid overwrite confirmation dialogs
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"note_{timestamp}"
            pyautogui.write(filename, interval=0.05)
            time.sleep(1.0)
            pyautogui.press('enter') # Confirm save
            time.sleep(1.0) # Wait for save to complete
        return f"Pressed Ctrl+Shift+S -> Wait 4s -> Typed '{filename}' -> Enter"

    if "play the song" in step or "play song" in step:
        # Contextual, mostly Enter works for "play" in spotify search results
        if pyautogui: 
            pyautogui.press('enter') 
            time.sleep(1.0)
        return "Pressed Enter (Play)"

    return f"Unknown step: {step}"

# --- OCR HELPER (TESSERACT: NON-INTERACTIVE) ---
def get_screen_readout():
    """Captures screen via screenshot and reads text using Tesseract. Non-intrusive."""
    import subprocess
    import pyautogui
    import os
    
    # Path to Tesseract (Winget Default)
    tesseract_path = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    # Fallback if user installed elsewhere
    if not os.path.exists(tesseract_path):
        tesseract_path = r"C:\Users\sumuk\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"

    if not os.path.exists(tesseract_path):
         return "Vision Unavailable: Tesseract not found. (Please release Clipboard fallback)"

    try:
        # 1. Capture Screenshot (Background)
        screenshot_path = os.path.abspath(".gemini_vision_temp.png")
        pyautogui.screenshot(screenshot_path)
        
        # 2. Run Tesseract CLI
        # tesseract image.png stdout
        result = subprocess.run(
            [tesseract_path, screenshot_path, "stdout"], 
            capture_output=True, 
            text=True, 
            encoding='utf-8',
            creationflags=subprocess.CREATE_NO_WINDOW # Hide console window
        )
        
        if result.returncode != 0:
            return f"Vision Error: {result.stderr[:100]}"
            
        text = result.stdout.strip()
        clean_text = " ".join(text.split())[:600] # Increased limit
        
        # Cleanup
        try: os.remove(screenshot_path)
        except: pass
        
        if not clean_text: return "Screen text empty (Image clear?)"
        
        return f"Screen Readout: {clean_text}..."
        
    except Exception as e:
        return f"Vision Unavailable: {str(e)}"

def execute_verbose_command(command_string):
    """
    Parses "do X then do Y then do Z" and executes sequentially.
    """
    if not command_string:
        return ["No steps to execute."]
    
    # ... (OS handling omitted for brevity, same as before) ...
    task_str = command_string
    if "if it is windows" in task_str.lower():
        task_str = task_str.lower().replace("if it is windows", "").strip()
        if "/" in task_str: task_str = task_str.split("/")[0]

    steps = task_str.split(" then ")
    logs = []
    
    for step in steps:
        if not step.strip(): continue
        try:
            result = execute_step(step)
            logs.append(result)
        except Exception as e:
            err_msg = f"Failed step '{step}': {str(e)}"
            print(f"[EXECUTOR ERROR] {err_msg}")
            logs.append(err_msg)
            break
        time.sleep(0.5)
        
    # --- AUTO LOOK: Read screen after completion ---
    vision_log = get_screen_readout()
    logs.append(vision_log)
        
    return logs
