import os
import subprocess
from PIL import ImageGrab
import time

def test_ocr():
    # 1. Take Screenshot
    print("Capturing screen...")
    img = ImageGrab.grab()
    img_path = os.path.abspath("test_screen.png")
    img.save(img_path)
    
    # 2. Run PowerShell OCR
    print("Running OCR...")
    cmd = ["powershell", "-ExecutionPolicy", "Bypass", "-File", "win_ocr.ps1", img_path]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        print("STDOUT:", result.stdout[:200]) # truncated
        print("STDERR:", result.stderr)
        
        if "ERROR" in result.stdout:
            print("OCR Failed")
        else:
            print("OCR Success!")
            
    except Exception as e:
        print(f"Subprocess failed: {e}")

if __name__ == "__main__":
    test_ocr()
