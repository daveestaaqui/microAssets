from PIL import Image
import pytesseract
import os

def check(path):
    if os.path.exists(path):
        img = Image.open(path)
        # Convert to grayscale for better OCR
        text = pytesseract.image_to_string(img.convert('L'))
        print(f"File: {path}")
        print(f"Detected Text: {text.strip()}")
        print("-" * 20)

if __name__ == "__main__":
    check("_landing_page/unified-logo.png")
    check("_landing_page/omnisuite-logo.png")
