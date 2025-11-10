"""
Script to build ALIVE Data MVP as a standalone executable.
Run this script to create a distributable .exe file.
"""

import PyInstaller.__main__
import os
import sys
from pathlib import Path

def build_exe(toolbar=False):
    """Build the executable using PyInstaller.
    
    Args:
        toolbar: If True, build the floating toolbar. If False, build the full GUI.
    """
    
    # Ensure we're in the project root directory
    script_dir = Path(__file__).parent.parent  # Go up to project root
    os.chdir(script_dir)
    
    # Choose which script to build
    script_name = 'src/toolbar.py' if toolbar else 'src/gui.py'
    exe_name = 'ALIVE_Data_Toolbar' if toolbar else 'ALIVE_Data'
    
    # PyInstaller arguments
    args = [
        script_name,  # Main script
        f'--name={exe_name}',  # Name of the executable
        '--onefile',  # Create a single executable file
        '--windowed',  # No console window (GUI only)
        '--icon=NONE',  # You can add an icon file later if desired
        '--add-data=README.md;.',  # Include README
        '--hidden-import=pytesseract',
        '--hidden-import=PIL',
        '--hidden-import=mss',
        '--hidden-import=openai',
        '--hidden-import=dotenv',
        '--collect-all=pytesseract',  # Collect all pytesseract data
        '--collect-all=PIL',  # Collect all PIL data
    ]
    
    app_type = "Floating Toolbar" if toolbar else "Full GUI"
    print(f"Building {app_type} executable...")
    print("This may take a few minutes...")
    
    try:
        PyInstaller.__main__.run(args)
        print("\n✓ Build complete!")
        print(f"Executable location: {script_dir / 'dist' / f'{exe_name}.exe'}")
        print("\nNote: Users will need Tesseract OCR installed on their system.")
        print("The .exe file can be distributed, but Tesseract must be installed separately.")
    except Exception as e:
        print(f"\n✗ Build failed: {e}")
        raise


if __name__ == "__main__":
    # Check command line arguments
    toolbar_mode = '--toolbar' in sys.argv or '-t' in sys.argv
    build_exe(toolbar=toolbar_mode)

