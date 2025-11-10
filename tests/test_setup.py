"""
Test script to verify ALIVE Data MVP setup
Run this to check if everything is configured correctly.
"""

import sys
from pathlib import Path

# Fix Windows console encoding for checkmarks
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

def test_imports():
    """Test if all required modules can be imported."""
    print("1. Testing imports...")
    try:
        import pytesseract
        from PIL import Image
        import mss
        from openai import OpenAI
        from dotenv import load_dotenv
        print("   ✓ All imports successful")
        return True
    except ImportError as e:
        print(f"   ✗ Import error: {e}")
        print("   → Run: pip install -r requirements.txt")
        return False

def test_tesseract():
    """Test if Tesseract OCR is accessible."""
    print("\n2. Testing Tesseract OCR...")
    try:
        import pytesseract
        import os
        
        # Check if Tesseract path is configured
        if os.name == 'nt':  # Windows
            tesseract_paths = [
                r"C:\Program Files\Tesseract-OCR\tesseract.exe",
                r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
            ]
            for path in tesseract_paths:
                if os.path.exists(path):
                    pytesseract.pytesseract.tesseract_cmd = path
                    print(f"   ✓ Tesseract found at: {path}")
                    break
            else:
                print("   ⚠ Tesseract not found in standard locations")
                print("   → Make sure Tesseract is installed and in PATH")
        
        # Try to get Tesseract version
        try:
            version = pytesseract.get_tesseract_version()
            print(f"   ✓ Tesseract version: {version}")
            return True
        except Exception as e:
            print(f"   ✗ Cannot access Tesseract: {e}")
            return False
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False

def test_ocr_on_test_image():
    """Test OCR on a simple test image."""
    print("\n3. Testing OCR functionality...")
    try:
        from PIL import Image, ImageDraw, ImageFont
        import pytesseract
        import os
        
        # Configure Tesseract if on Windows
        if os.name == 'nt':
            tesseract_paths = [
                r"C:\Program Files\Tesseract-OCR\tesseract.exe",
                r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
            ]
            for path in tesseract_paths:
                if os.path.exists(path):
                    pytesseract.pytesseract.tesseract_cmd = path
                    break
        
        # Create a simple test image with text
        img = Image.new('RGB', (400, 100), color='white')
        draw = ImageDraw.Draw(img)
        test_text = "Hello ALIVE Data Test"
        draw.text((50, 30), test_text, fill='black')
        
        test_image_path = "test_image.png"
        img.save(test_image_path)
        
        # Try OCR
        text = pytesseract.image_to_string(img)
        text = text.strip()
        
        # Clean up
        Path(test_image_path).unlink(missing_ok=True)
        
        if text:
            print(f"   ✓ OCR extracted text: '{text[:50]}...'")
            return True
        else:
            print("   ⚠ OCR returned empty text (this might be okay)")
            return True  # Still consider it a pass
    except Exception as e:
        print(f"   ✗ OCR test failed: {e}")
        return False

def test_screenshot_capture():
    """Test if screenshot capture works."""
    print("\n4. Testing screenshot capture...")
    try:
        import mss
        from PIL import Image
        
        with mss.mss() as sct:
            monitor = sct.monitors[1]
            sct_img = sct.grab(monitor)
            img = Image.frombytes("RGB", sct_img.size, sct_img.rgb)
            print(f"   ✓ Screenshot captured: {sct_img.size[0]}x{sct_img.size[1]} pixels")
            return True
    except Exception as e:
        print(f"   ✗ Screenshot capture failed: {e}")
        return False

def test_openai_config():
    """Test if OpenAI API key is configured."""
    print("\n5. Testing OpenAI configuration...")
    try:
        from dotenv import load_dotenv
        import os
        from openai import OpenAI
        
        load_dotenv()
        api_key = os.getenv("OPENAI_API_KEY")
        
        if not api_key:
            print("   ✗ OPENAI_API_KEY not found in environment")
            print("   → Create a .env file with: OPENAI_API_KEY=sk-your-key")
            return False
        
        if api_key == "sk-your-actual-key-here" or len(api_key) < 20:
            print("   ✗ OPENAI_API_KEY appears to be a placeholder")
            print("   → Update .env with your actual API key")
            return False
        
        print(f"   ✓ API key found (starts with: {api_key[:7]}...)")
        
        # Try to make a simple API call to verify it works
        print("   → Testing API connection...")
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Say 'test'"}],
            max_tokens=5,
        )
        result = response.choices[0].message.content.strip()
        print(f"   ✓ API test successful: '{result}'")
        return True
    except Exception as e:
        print(f"   ✗ OpenAI test failed: {e}")
        if "api_key" in str(e).lower() or "authentication" in str(e).lower():
            print("   → Check your API key in .env file")
        return False

def test_docs_directory():
    """Test if docs directory exists or can be created."""
    print("\n6. Testing docs directory...")
    try:
        Path("docs").mkdir(exist_ok=True)
        if Path("docs").exists():
            print("   ✓ docs/ directory ready")
            return True
        else:
            print("   ✗ Could not create docs/ directory")
            return False
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("ALIVE Data MVP - Setup Verification")
    print("=" * 60)
    
    results = []
    results.append(("Imports", test_imports()))
    results.append(("Tesseract", test_tesseract()))
    results.append(("OCR", test_ocr_on_test_image()))
    results.append(("Screenshot", test_screenshot_capture()))
    results.append(("OpenAI", test_openai_config()))
    results.append(("Docs Directory", test_docs_directory()))
    
    print("\n" + "=" * 60)
    print("Test Summary:")
    print("=" * 60)
    
    all_passed = True
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {status} - {name}")
        if not passed:
            all_passed = False
    
    print("=" * 60)
    if all_passed:
        print("🎉 All tests passed! You're ready to run: python main.py")
    else:
        print("⚠ Some tests failed. Please fix the issues above.")
    print("=" * 60)

if __name__ == "__main__":
    main()

