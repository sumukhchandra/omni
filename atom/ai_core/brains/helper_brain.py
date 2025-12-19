import pyautogui
import pytesseract
import cv2
import numpy as np
import os
from PIL import Image

# Ensure Tesseract path if needed (User's system specific, but usually in PATH or needs config)
# If tesseract is not in path, we might need to search for it, but for MVP we assume PATH or simple setup.
# On Windows, commonly: C:\Program Files\Tesseract-OCR\tesseract.exe
# We will try to auto-detect or default.

class HelperBrain:
    def __init__(self):
        print("[Helper Brain] Initializing Vision...")
        self.setup_tesseract()

    def setup_tesseract(self):
        # MVP: hardcode common path or assume PATH.
        # Check common paths
        common_paths = [
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
             os.path.expanduser("~") + r"\AppData\Local\Tesseract-OCR\tesseract.exe"
        ]
        
        found = False
        for p in common_paths:
            if os.path.exists(p):
                pytesseract.pytesseract.tesseract_cmd = p
                print(f"[Helper Brain] Tesseract found at {p}")
                found = True
                break
        
        if not found:
             # Retain default, might be in PATH
             print("[Helper Brain] Tesseract not found in common paths. Assuming PATH.")

    def see(self):
        """
        Captures screen and performs OCR.
        Returns: 
            dict: {
                "text": "full text string", 
                "data": pandas dataframe or dict with word coordinates
            }
        """
        print("[Helper Brain] Capturing screen...")
        try:
            screenshot = pyautogui.screenshot()
            # Convert to OpenCV format
            img = np.array(screenshot)
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)  
            
            # Simple Text Extraction
            text = pytesseract.image_to_string(img)
            
            # Detailed Data (for checking coordinates)
            data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
            
            print(f"[Helper Brain] Analysis complete. Found {len(text)} chars.")
            return {"text": text, "data": data, "image_size": screenshot.size}
        except Exception as e:
            print(f"[Helper Brain] BLINDNESS ERROR: {e}")
            return {"text": "", "data": {}, "error": str(e)}

    def find_text_on_screen(self, target_text, screen_data=None):
        """
        Locates center coordinates of a specific word/phrase.
        Returns: (x, y) or None
        """
        if not screen_data:
            result = self.see()
            screen_data = result["data"]
            
        target_lower = target_text.lower()
        n_boxes = len(screen_data['text'])
        
        for i in range(n_boxes):
            word = screen_data['text'][i].lower().strip()
            # Partial match checks
            # 1. Exact contains (to handle "Siddu." punctuation)
            # 2. Or if word is part of target (less likely useful)
            if word and (target_lower in word or word in target_lower):
                 # Filter trivial matches (e.g. "a" in "apple" is bad, but "search" in "search..." is good)
                 # Length heuristic:
                 if len(word) < 2 and len(target_lower) > 2: continue

                 (x, y, w, h) = (screen_data['left'][i], screen_data['top'][i], screen_data['width'][i], screen_data['height'][i])
                 center_x = x + w // 2
                 center_y = y + h // 2
                 print(f"[Helper Brain] Found '{target_text}' (match: '{word}') at ({center_x}, {center_y})")
                 return (center_x, center_y)
        
        print(f"[Helper Brain] '{target_text}' not visible.")
        return None

    def find_all_text_on_screen(self, target_text, screen_data=None):
        """
        Locates ALL occurrences of a specific word/phrase.
        Returns: List of (x, y) tuples
        """
        if not screen_data:
            result = self.see()
            screen_data = result["data"]
            
        target_lower = target_text.lower()
        n_boxes = len(screen_data['text'])
        matches = []
        
        for i in range(n_boxes):
            word = screen_data['text'][i].lower().strip()
            if word and (target_lower in word or word in target_lower):
                 if len(word) < 2 and len(target_lower) > 2: continue
                 (x, y, w, h) = (screen_data['left'][i], screen_data['top'][i], screen_data['width'][i], screen_data['height'][i])
                 center_x = x + w // 2
                 center_y = y + h // 2
                 matches.append((center_x, center_y))
        
        print(f"[Helper Brain] Found {len(matches)} matches for '{target_text}'")
        return matches
