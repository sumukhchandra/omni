import pytesseract
from PIL import ImageGrab
import platform

def test_tesseract():
    print("Testing Tesseract...")
    tesseract_path = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    pytesseract.pytesseract.tesseract_cmd = tesseract_path
    
    try:
        img = ImageGrab.grab()
        print("Screenshot captured.")
        
        data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
        
        n_boxes = len(data['text'])
        print(f"OCR finished. Found {n_boxes} items.")
        
        found_words = [t for t in data['text'] if t.strip()]
        print(f"First 10 words: {found_words[:10]}")
        
        if len(found_words) > 0:
            print("✅ Tesseract is working and finding text.")
        else:
            print("⚠️ Tesseract ran but found no text.")
            
    except Exception as e:
        print(f"❌ Tesseract Failed: {e}")

if __name__ == "__main__":
    test_tesseract()
