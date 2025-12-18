import sys
print(f"Python: {sys.executable}")
try:
    import pyautogui
    print("PyAutoGUI: OK")
except ImportError as e:
    print(f"PyAutoGUI: MISSING ({e})")

try:
    import PIL
    from PIL import ImageGrab
    print("Pillow: OK")
except ImportError as e:
    print(f"Pillow: MISSING ({e})")

try:
    import pytesseract
    print("Pytesseract: OK")
except ImportError as e:
    print(f"Pytesseract: MISSING ({e})")
