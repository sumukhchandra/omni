import os
import subprocess
import time

def test_ocr_complete():
    # File to save temp screenshot to
    img_path = os.path.abspath("temp_ocr_screen.png")
    
    print(f"Running OCR Capture -> {img_path}...")
    cmd = ["powershell", "-ExecutionPolicy", "Bypass", "-File", "win_ocr_capture.ps1", img_path]
    
    try:
        start = time.time()
        result = subprocess.run(cmd, capture_output=True, text=True)
        duration = time.time() - start
        
        print(f"Time Taken: {duration:.2f}s")
        print("STDOUT:", result.stdout) # FULL OUTPUT
        print("STDERR:", result.stderr)
        
        if "ERROR" in result.stdout:
            print("OCR Failed")
        elif len(result.stdout) < 10:
             print("OCR Result too short (Screen empty?)")
        else:
            print("OCR Success! Found text on screen.")
            
    except Exception as e:
        print(f"Subprocess failed: {e}")

if __name__ == "__main__":
    test_ocr_complete()
