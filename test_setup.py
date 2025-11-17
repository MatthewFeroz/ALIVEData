"""
Quick setup test script to verify ALIVE Data web app configuration.
Run this before starting the application.
"""

import sys
import os
from pathlib import Path

def test_python_version():
    """Test Python version."""
    print("[OK] Python version:", sys.version.split()[0])
    if sys.version_info < (3, 8):
        print("[FAIL] Python 3.8+ required")
        return False
    return True

def test_dependencies():
    """Test if required packages are installed."""
    required = [
        'fastapi',
        'uvicorn',
        'pydantic',
        'openai',
        'pytesseract',
        'PIL',
        'dotenv'
    ]
    missing = []
    for package in required:
        try:
            if package == 'PIL':
                __import__('PIL')
            elif package == 'dotenv':
                __import__('dotenv')
            else:
                __import__(package)
            print(f"[OK] {package} installed")
        except ImportError:
            print(f"[FAIL] {package} NOT installed")
            missing.append(package)
    
    if missing:
        print(f"\nMissing packages: {', '.join(missing)}")
        print("Run: pip install -r requirements.txt")
        return False
    return True

def test_structure():
    """Test if project structure is correct."""
    required_dirs = [
        'app',
        'app/api',
        'app/core',
        'app/models',
        'app/services',
        'frontend',
        'frontend/src'
    ]
    missing = []
    for dir_path in required_dirs:
        if not Path(dir_path).exists():
            print(f"[FAIL] Missing directory: {dir_path}")
            missing.append(dir_path)
        else:
            print(f"[OK] Directory exists: {dir_path}")
    
    if missing:
        print(f"\nMissing directories: {', '.join(missing)}")
        return False
    return True

def test_env_file():
    """Test if .env file exists."""
    env_file = Path('.env')
    if env_file.exists():
        print("[OK] .env file exists")
        # Check if API key is set (only if dotenv is installed)
        try:
            from dotenv import load_dotenv
            load_dotenv()
            api_key = os.getenv('OPENAI_API_KEY', '')
            if api_key and api_key != 'your_openai_api_key_here':
                print("[OK] OPENAI_API_KEY is configured")
                return True
            else:
                print("[WARN] OPENAI_API_KEY not configured (set it in .env)")
                return False
        except ImportError:
            print("[WARN] Cannot check API key (python-dotenv not installed)")
            return False
    else:
        print("[WARN] .env file not found (create from .env.example)")
        return False

def test_tesseract():
    """Test if Tesseract OCR is available."""
    try:
        import pytesseract
        # Try to get version
        version = pytesseract.get_tesseract_version()
        print(f"[OK] Tesseract OCR found (version {version})")
        return True
    except Exception as e:
        print(f"[WARN] Tesseract OCR not found: {e}")
        print("  Install Tesseract: https://github.com/UB-Mannheim/tesseract/wiki")
        return False

def main():
    """Run all tests."""
    print("=" * 50)
    print("ALIVE Data Web App - Setup Test")
    print("=" * 50)
    print()
    
    results = []
    
    print("1. Testing Python version...")
    results.append(test_python_version())
    print()
    
    print("2. Testing project structure...")
    results.append(test_structure())
    print()
    
    print("3. Testing Python dependencies...")
    results.append(test_dependencies())
    print()
    
    print("4. Testing environment configuration...")
    results.append(test_env_file())
    print()
    
    print("5. Testing Tesseract OCR...")
    results.append(test_tesseract())
    print()
    
    print("=" * 50)
    if all(results):
        print("[SUCCESS] All tests passed! Ready to run the application.")
        print("\nNext steps:")
        print("  1. Backend: python -m uvicorn app.main:app --reload")
        print("  2. Frontend: cd frontend && npm install && npm run dev")
    else:
        print("[WARNING] Some tests failed. Please fix the issues above.")
    print("=" * 50)

if __name__ == "__main__":
    main()

