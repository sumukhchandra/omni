import subprocess
import json
import os

def test_ocr_output():
    # Capture a temp screenshot
    # Capture a temp screenshot using PIL directly
    from PIL import ImageGrab
    screenshot_path = os.path.abspath("temp_ocr_test.png")
    img = ImageGrab.grab()
    img.save(screenshot_path)
    
    ps_script = r"c:\Users\sumuk\OneDrive\Desktop\Forcys - Copy\win_ocr.ps1"
    
    cmd = ["powershell", "-ExecutionPolicy", "Bypass", "-File", ps_script, screenshot_path]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    print(f"STDOUT: {result.stdout[:200]}...") # Print first 200 chars
    with open("verify_debug_output.txt", "w") as f:
        f.write(result.stdout)
        f.write("\n--- STDERR ---\n")
        f.write(result.stderr)
    
    try:
        data = json.loads(result.stdout.strip())
        print(f"JSON Parsed Successfully. Found {len(data)} words.")
        if len(data) > 0:
            print(f"Sample: {data[0]}")
            if "rect" in data[0] and "text" in data[0]:
                 print("✅ Validation Passed: 'rect' and 'text' keys found.")
            else:
                 print("❌ Validation Failed: Missing keys.")
        else:
             print("⚠️ No text found (screen might be empty?)")
             
    except json.JSONDecodeError as e:
        print(f"❌ JSON Decode Error: {e}")
        print(f"Raw Output: {result.stdout}")

    if os.path.exists(screenshot_path):
        os.remove(screenshot_path)

if __name__ == "__main__":
    test_ocr_output()
