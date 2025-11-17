"""
Service for handling screenshot capture and OCR processing.
Adapted from src/capture.py for web use.
"""

import os
import sys
from pathlib import Path
from typing import Optional
from PIL import Image
import pytesseract

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


def extract_text_from_image(image_path: str) -> str:
    """
    Run OCR on an image file.
    
    Args:
        image_path: Path to the image file
        
    Returns:
        Extracted text from the image
    """
    try:
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img)
        return text
    except Exception as e:
        raise Exception(f"Failed to extract text from image: {str(e)}")


def extract_terminal_text(screenshot_path: str) -> str:
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
    except Exception as e:
        return f"Error extracting text: {str(e)}"

