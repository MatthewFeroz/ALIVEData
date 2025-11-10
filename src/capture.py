import time
import pytesseract
from PIL import Image
import mss
from datetime import datetime
import os
import sys

# Windows API imports
if sys.platform == 'win32':
    try:
        import win32gui
        import win32con
        import win32ui
        WIN32_AVAILABLE = True
    except ImportError:
        WIN32_AVAILABLE = False
else:
    WIN32_AVAILABLE = False

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


def capture_window(hwnd, screenshot_path=None):
    """
    Capture screenshot of a specific window.
    
    Args:
        hwnd: Window handle (Windows only)
        screenshot_path: Optional path to save screenshot
    
    Returns:
        Path to saved screenshot
    """
    if not WIN32_AVAILABLE or sys.platform != 'win32':
        # Fallback to full screen capture
        if screenshot_path is None:
            screenshot_path = f"docs/window_{datetime.now().strftime('%H%M%S')}.png"
        return capture_screen(screenshot_path)
    
    try:
        # Get window dimensions
        left, top, right, bottom = win32gui.GetWindowRect(hwnd)
        width = right - left
        height = bottom - top
        
        if width <= 0 or height <= 0:
            # Invalid window size, fallback to full screen
            if screenshot_path is None:
                screenshot_path = f"docs/window_{datetime.now().strftime('%H%M%S')}.png"
            return capture_screen(screenshot_path)
        
        # Create device context
        hwndDC = win32gui.GetWindowDC(hwnd)
        mfcDC = win32ui.CreateDCFromHandle(hwndDC)
        saveDC = mfcDC.CreateCompatibleDC()
        
        # Create bitmap
        saveBitMap = win32ui.CreateBitmap()
        saveBitMap.CreateCompatibleBitmap(mfcDC, width, height)
        saveDC.SelectObject(saveBitMap)
        
        # Copy window to bitmap
        saveDC.BitBlt((0, 0), (width, height), mfcDC, (0, 0), win32con.SRCCOPY)
        
        # Save to file
        if screenshot_path is None:
            screenshot_path = f"docs/window_{datetime.now().strftime('%H%M%S')}.png"
        
        # Ensure directory exists
        from pathlib import Path
        Path(screenshot_path).parent.mkdir(parents=True, exist_ok=True)
        
        saveBitMap.SaveBitmapFile(saveDC, screenshot_path)
        
        # Cleanup
        win32gui.DeleteObject(saveBitMap.GetHandle())
        saveDC.DeleteDC()
        mfcDC.DeleteDC()
        win32gui.ReleaseDC(hwnd, hwndDC)
        
        return screenshot_path
    except Exception:
        # Fallback to full screen capture on error
        if screenshot_path is None:
            screenshot_path = f"docs/window_{datetime.now().strftime('%H%M%S')}.png"
        return capture_screen(screenshot_path)


def get_window_text(hwnd):
    """
    Extract text from a window (Windows only).
    Note: This typically only gets the window title, not content.
    For terminal content, OCR is more reliable.
    
    Args:
        hwnd: Window handle
    
    Returns:
        Window text (usually just title)
    """
    if not WIN32_AVAILABLE or sys.platform != 'win32':
        return ""
    
    try:
        return win32gui.GetWindowText(hwnd)
    except Exception:
        return ""


def extract_terminal_text(screenshot_path):
    """
    Extract text from terminal window screenshot using OCR.
    Attempts to parse the last command line.
    
    Args:
        screenshot_path: Path to terminal screenshot
    
    Returns:
        Extracted command text (best effort)
    """
    try:
        # Use OCR to extract text
        text = extract_text_from_image(screenshot_path)
        
        # Try to extract the last command line
        # Look for patterns like "C:\> command" or "$ command"
        lines = text.split('\n')
        for line in reversed(lines):
            line = line.strip()
            # Look for command-like patterns
            if line and not line.startswith('Microsoft') and len(line) > 3:
                # Try to find the actual command (after prompt)
                if '>' in line:
                    parts = line.split('>', 1)
                    if len(parts) > 1:
                        command = parts[1].strip()
                        if command:
                            return command
                elif '$' in line:
                    parts = line.split('$', 1)
                    if len(parts) > 1:
                        command = parts[1].strip()
                        if command:
                            return command
                # If no prompt found, return the line if it looks like a command
                if line and not line.startswith('PS') and ' ' in line:
                    return line
        
        # Fallback: return first non-empty line
        for line in lines:
            line = line.strip()
            if line and len(line) > 3:
                return line
        
        return text[:100]  # Return first 100 chars if nothing else works
    except Exception:
        return ""

