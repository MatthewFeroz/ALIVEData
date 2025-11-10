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


def extract_text_from_image(image_path, region=None):
    """
    Run OCR on the image, optionally on a specific region.
    
    Args:
        image_path: Path to image file
        region: Optional dict with keys: x, y, width, height
                If provided, only OCR this region of the image
    
    Returns:
        Extracted text string
    """
    img = Image.open(image_path)
    
    # Crop to region if specified
    if region:
        x = region.get('x', 0)
        y = region.get('y', 0)
        width = region.get('width', img.width)
        height = region.get('height', img.height)
        
        # Ensure region is within image bounds
        x = max(0, min(x, img.width - 1))
        y = max(0, min(y, img.height - 1))
        width = min(width, img.width - x)
        height = min(height, img.height - y)
        
        if width > 0 and height > 0:
            img = img.crop((x, y, x + width, y + height))
    
    text = pytesseract.image_to_string(img)
    return text


def extract_text_from_region(image_path, region):
    """
    Extract text from a specific region of an image using OCR.
    
    Args:
        image_path: Path to image file
        region: Dict with keys: x, y, width, height
    
    Returns:
        Extracted text string
    """
    return extract_text_from_image(image_path, region=region)


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


def get_terminal_command_region(window_hwnd=None, window_width=None, window_height=None):
    """
    Get default terminal command region using heuristics.
    Assumes command line is typically at the bottom of the terminal.
    
    Args:
        window_hwnd: Window handle (Windows only, for getting dimensions)
        window_width: Window width (if known)
        window_height: Window height (if known)
    
    Returns:
        Region dict with keys: x, y, width, height, confidence
    """
    # Try to get window dimensions if hwnd provided
    if window_hwnd and WIN32_AVAILABLE and sys.platform == 'win32':
        try:
            left, top, right, bottom = win32gui.GetWindowRect(window_hwnd)
            window_width = right - left
            window_height = bottom - top
        except Exception:
            pass
    
    # Default heuristics: bottom 30% of terminal, full width
    if window_width and window_height:
        region_height = int(window_height * 0.3)
        region_y = window_height - region_height
        
        return {
            'x': 0,
            'y': max(0, region_y),
            'width': window_width,
            'height': region_height,
            'confidence': 0.5  # Medium confidence for heuristic-based region
        }
    
    # Return None if we can't determine dimensions
    return None


def extract_terminal_text(screenshot_path, region=None, window_hwnd=None):
    """
    Extract text from terminal window screenshot using OCR.
    Attempts to parse the last command line.
    Supports focus region OCR with fallback to full window.
    
    Args:
        screenshot_path: Path to terminal screenshot
        region: Optional dict with keys: x, y, width, height, confidence
                If provided, tries OCR on this region first
        window_hwnd: Optional window handle for heuristics
    
    Returns:
        Extracted command text (best effort)
    """
    try:
        focus_text = None
        focus_confidence = 0.0
        
        # Try focus region first if provided
        if region:
            try:
                focus_text = extract_text_from_region(screenshot_path, region)
                focus_confidence = region.get('confidence', 0.5)
                
                # Check if focus region yielded useful text
                if focus_text and focus_text.strip():
                    # Try to extract command from focus region text
                    command = _parse_command_from_text(focus_text)
                    if command:
                        return command
            except Exception:
                # If focus region OCR fails, continue to fallback
                pass
        
        # Fallback: use terminal heuristics if no region provided
        if not region and window_hwnd:
            heuristic_region = get_terminal_command_region(window_hwnd)
            if heuristic_region:
                try:
                    heuristic_text = extract_text_from_region(screenshot_path, heuristic_region)
                    if heuristic_text and heuristic_text.strip():
                        command = _parse_command_from_text(heuristic_text)
                        if command:
                            return command
                except Exception:
                    pass
        
        # Final fallback: full window OCR
        full_text = extract_text_from_image(screenshot_path)
        
        # If we have focus region text, prefer it if it's more recent/relevant
        if focus_text and focus_text.strip() and focus_confidence > 0.3:
            # Try parsing focus text first
            command = _parse_command_from_text(focus_text)
            if command:
                return command
        
        # Parse full window text
        command = _parse_command_from_text(full_text)
        if command:
            return command
        
        # Last resort: return first meaningful portion
        return full_text[:100] if full_text else ""
        
    except Exception:
        return ""


def _parse_command_from_text(text):
    """
    Parse command text from OCR output.
    Looks for command patterns like "C:\> command" or "$ command".
    
    Args:
        text: Raw OCR text
    
    Returns:
        Extracted command string, or None if not found
    """
    if not text:
        return None
    
    lines = text.split('\n')
    
    # Try to extract the last command line
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
    
    return None

