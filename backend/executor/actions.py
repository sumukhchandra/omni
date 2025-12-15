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

def platform_open_app(app_name: str):
    plat = platform.system().lower()
    try:
        if plat == "darwin":
            subprocess.run(["open", "-a", app_name], check=False)
        elif plat == "windows":
            subprocess.run(["cmd", "/c", "start", "", app_name], shell=False)
        else:
            subprocess.run(["/usr/bin/xdg-open", app_name], check=False)
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
            time.sleep(1.0)
        return "Pressed Windows key"

    if "search for" in step:
        query = step.split("search for")[1].strip()
        if pyautogui: pyautogui.write(query, interval=0.1)
        time.sleep(0.5)
        return f"Typed '{query}'"

    if "type" in step and "search" not in step: # avoid conflict with above if vague
        text = step.split("type")[1].strip()
        if pyautogui: pyautogui.write(text, interval=0.1)
        return f"Typed '{text}'"

    # Handle "typr" (typo included)
    if "typr" in step:
         text = step.split("typr")[1].strip()
         if pyautogui: pyautogui.write(text, interval=0.1)
         return f"Typed '{text}' (processed typo 'typr')"

    if "open it" in step or "click open" in step:
        if pyautogui: pyautogui.press('enter')
        time.sleep(6.0) # Wait longer for app to open (Spotify is heavy)
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
             time.sleep(3.0)
             return "Opened Default Browser to Google"

        print(f"[EXECUTOR] Attempting to open app: {app_name}")
        if platform_open_app(app_name):
             time.sleep(3.0) # Wait for app execution
             return f"Opened App '{app_name}' via platform command"
        else:
             return f"Failed to open '{app_name}'"

    if "navigate to search bar" in step:
        # Heuristic: Ctrl+K is a common "Jump to Search" shortcut (Slack, Discord, Spotify, Teams)
        # Ctrl+F is Find. Ctrl+L is Browser URL.
        # We will try Ctrl+K as it's more specific to "search bar" than "find in page"
        if pyautogui: 
            pyautogui.hotkey('ctrl', 'k')
            time.sleep(1.0)
        return "Pressed Ctrl+K (Focus Search)"

    if "click on search" in step:
        # If Ctrl+K didn't work, we can try clicking top-left/center or Tab cycling
        # preventing "click on search" from doing nothing
        if pyautogui:
            pyautogui.press('tab') # Try tabbing once in case we are close
            time.sleep(0.2)
        return "Pressed Tab (Attempt Focus Search)"

    if "click on " in step:
        target = step.split("click on ")[-1].strip()
        # Heuristic: For any "click on {target}", we use a robust Search -> Select sequence.
        # This covers: "click on the song", "click on {contact}", "click on notes"
        
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

        # Default "Select Item" logic (Enter -> Wait -> Tab -> Down -> Enter)
        if pyautogui:
             pyautogui.press('enter') # 1. Submit search
             time.sleep(4.0)          # 2. Wait for results
             pyautogui.press('tab')   # 3. Focus list
             time.sleep(0.2)
             pyautogui.press('down')  # 4. Select first item (crucial for accurate selection)
             time.sleep(0.2)
             pyautogui.press('enter') # 5. Open/Select
             time.sleep(1.0)
        return f"Selected '{target}' (Enter->Wait->Tab->Down->Enter)"

    if "save it" in step or "save file" in step:
        if pyautogui:
            # Ensure we are focused on the doc
            pyautogui.click() 
            time.sleep(0.5)
            
            pyautogui.hotkey('ctrl', 's')
            time.sleep(4.0) # Increased wait for Save As dialog (was 2.0)
            
            # Use timestamp to avoid overwrite confirmation dialogs
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"note_{timestamp}"
            pyautogui.write(filename, interval=0.05)
            time.sleep(1.0)
            pyautogui.press('enter') # Confirm save
            time.sleep(1.0) # Wait for save to complete
        return f"Pressed Ctrl+S -> Wait 4s -> Typed '{filename}' -> Enter"

    if "play the song" in step or "play song" in step:
        # Contextual, mostly Enter works for "play" in spotify search results
        if pyautogui: 
            pyautogui.press('enter') 
            time.sleep(0.5)
        return "Pressed Enter (Play)"

    return f"Unknown step: {step}"

def execute_verbose_command(command_string):
    """
    Parses "do X then do Y then do Z" and executes sequentially.
    """
    if not command_string:
        return ["No steps to execute."]
    
    # Clean up the slash-separated OS variants (taking Windows by default for this user)
    # The NLU returns "if it is windows ... / if it is mac ..."
    # We assume we are on Windows based on user metadata.
    
    task_str = command_string
    if "/" in command_string:
        parts = command_string.split("/")
        # crude heuristic: first part is usually windows in our NLU templates
        task_str = parts[0]
        if "windows" in task_str.lower():
            pass # good
        elif len(parts) > 1 and "windows" in parts[1].lower():
            task_str = parts[1]
    
    # Remove preamble "if it is windows "
    if "if it is windows" in task_str.lower():
        task_str = task_str.lower().replace("if it is windows", "").strip()

    steps = task_str.split(" then ")
    logs = []
    
    for step in steps:
        if not step.strip(): continue
        result = execute_step(step)
        logs.append(result)
        time.sleep(0.5)
        
    return logs
