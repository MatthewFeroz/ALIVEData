import time
import pytesseract
from PIL import Image
import mss
from datetime import datetime
import os

# Configure Tesseract path for Windows if not in PATH
if os.name == 'nt':  # Windows
    tesseract_paths = [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    ]
    for path in tesseract_paths:
        if os.path.exists(path):
            pytesseract.pytesseract.tesseract_cmd = path
            break


def capture_screen(screenshot_path="screenshot.png"):
    """Take a screenshot and save it."""
    with mss.mss() as sct:
        monitor = sct.monitors[1]
        sct_img = sct.grab(monitor)
        img = Image.frombytes("RGB", sct_img.size, sct_img.rgb)
        img.save(screenshot_path)
    return screenshot_path


def extract_text_from_image(image_path):
    """Run OCR on the image."""
    img = Image.open(image_path)
    text = pytesseract.image_to_string(img)
    return text


def capture_and_ocr():
    """Capture a screenshot and return extracted text."""
    path = f"docs/screen_{datetime.now().strftime('%H%M%S')}.png"
    capture_screen(path)
    text = extract_text_from_image(path)
    return text

