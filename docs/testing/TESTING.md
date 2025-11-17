# Testing Guide for ALIVE Data Web Application

## Quick Start Testing

### Step 1: Install Dependencies

**Backend:**
```bash
# Create virtual environment (if not already done)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install Python packages
pip install -r requirements.txt
```

**Frontend:**
```bash
cd frontend
npm install
cd ..
```

### Step 2: Configure Environment

Create a `.env` file in the root directory:

```bash
# Copy example file
# Windows:
copy .env.example .env
# macOS/Linux:
cp .env.example .env
```

Edit `.env` and add your OpenAI API key:
```
OPENAI_API_KEY=sk-your-actual-api-key-here
```

### Step 3: Start Backend Server

**Option A: Using Python directly**
```bash
# Make sure virtual environment is activated
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Option B: Using the script**
```bash
# Windows:
run_backend.bat

# macOS/Linux:
chmod +x run_backend.sh
./run_backend.sh
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**Verify backend is running:**
- Open browser: http://localhost:8000
- Should see: `{"message":"ALIVE Data API","version":"1.0.0","docs":"/docs"}`
- API Docs: http://localhost:8000/docs (Interactive Swagger UI)

### Step 4: Start Frontend (New Terminal)

**Option A: Using npm directly**
```bash
cd frontend
npm run dev
```

**Option B: Using the script**
```bash
# Windows:
run_frontend.bat

# macOS/Linux:
chmod +x run_frontend.sh
./run_frontend.sh
```

You should see:
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:3000/
  ➜  Network: use --host to expose
```

**Verify frontend is running:**
- Open browser: http://localhost:3000
- Should see the ALIVE Data interface

## Testing Workflow

### Test 1: Create a Session

1. Open http://localhost:3000
2. Click "+ New Session" button
3. Should redirect to session detail page
4. Session ID should appear in the URL

**Expected Result:** New session created, redirected to session page

### Test 2: Upload a Screenshot

1. On the session detail page, go to "Upload Screenshot" tab
2. Drag and drop an image file OR click to select
3. Supported formats: PNG, JPG, JPEG, GIF, BMP

**Expected Result:** 
- File uploads successfully
- Success message appears
- Screenshot appears in "Screenshots" tab

### Test 3: Process OCR

1. Go to "Screenshots" tab
2. Click "Process OCR" button on any screenshot
3. Wait for processing to complete

**Expected Result:**
- OCR processing completes
- Automatically switches to "OCR Text" tab
- Extracted text appears in textarea

### Test 4: Generate Documentation

1. Ensure OCR text is in the "OCR Text" tab
2. Optionally edit the text
3. Click "Generate Documentation" button
4. Wait for AI processing (may take 10-30 seconds)

**Expected Result:**
- Documentation generation completes
- Automatically switches to "Documentation" tab
- Formatted markdown documentation appears

### Test 5: View Session List

1. Click "Sessions" in navigation
2. Should see list of all sessions

**Expected Result:** All created sessions appear in a grid

## API Testing (Using Swagger UI)

1. Open http://localhost:8000/docs
2. Try these endpoints:

**Create Session:**
- POST `/api/sessions`
- Click "Try it out"
- Click "Execute"
- Copy the `session_id` from response

**Upload Screenshot:**
- POST `/api/sessions/{session_id}/screenshots`
- Click "Try it out"
- Enter session_id
- Click "Choose File" and select an image
- Click "Execute"

**Process OCR:**
- POST `/api/sessions/{session_id}/ocr`
- Click "Try it out"
- Enter session_id
- Request body:
  ```json
  {
    "screenshot_id": "your_screenshot_filename.png"
  }
  ```
- Click "Execute"

**Generate Documentation:**
- POST `/api/sessions/{session_id}/generate`
- Click "Try it out"
- Enter session_id
- Request body:
  ```json
  {
    "ocr_text": "Some text extracted from screenshot"
  }
  ```
- Click "Execute"

## Troubleshooting

### Backend Issues

**Port 8000 already in use:**
```bash
# Change port
python -m uvicorn app.main:app --reload --port 8001
```

**Module not found errors:**
```bash
# Make sure you're in the project root directory
# Verify app/ directory exists
ls app/  # or dir app\ on Windows
```

**Tesseract OCR not found:**
- Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki
- macOS: `brew install tesseract`
- Linux: `sudo apt-get install tesseract-ocr`
- Or set path in `.env`: `TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe`

**OpenAI API errors:**
- Verify API key in `.env` file
- Check API key format: should start with `sk-`
- Ensure account has credits

### Frontend Issues

**Port 3000 already in use:**
- Vite will automatically try the next available port
- Check terminal output for actual port

**npm install fails:**
```bash
# Clear cache and retry
npm cache clean --force
rm -rf node_modules package-lock.json  # or del on Windows
npm install
```

**CORS errors:**
- Verify backend is running on port 8000
- Check browser console for specific error
- Ensure `CORS_ORIGINS` in `app/core/config.py` includes frontend URL

**API connection errors:**
- Verify backend is running
- Check `frontend/src/services/api.js` - API_BASE_URL should be `http://localhost:8000/api`
- Check browser Network tab for failed requests

### Common Issues

**Screenshots not displaying:**
- Check browser console for 404 errors
- Verify screenshot files exist in `docs/sessions/{session_id}/screenshots/`
- Check backend logs for file serving errors

**OCR returns empty text:**
- Verify Tesseract is installed correctly
- Test Tesseract manually: `tesseract --version`
- Try with a clear, high-contrast image

**Documentation generation fails:**
- Check OpenAI API key is valid
- Verify API key has sufficient credits
- Check backend logs for detailed error messages

## Manual Testing Checklist

- [ ] Backend starts without errors
- [ ] Frontend starts without errors
- [ ] Can access http://localhost:3000
- [ ] Can access http://localhost:8000/docs
- [ ] Can create a new session
- [ ] Can upload a screenshot
- [ ] Can view uploaded screenshots
- [ ] Can process OCR on screenshot
- [ ] OCR extracts text correctly
- [ ] Can generate documentation
- [ ] Documentation appears formatted correctly
- [ ] Can view session list
- [ ] Can navigate between pages
- [ ] Error messages display properly

## Performance Testing

**Upload Speed:**
- Test with various image sizes (small, medium, large)
- Monitor upload progress indicator

**OCR Processing:**
- Test with different image types (screenshots, photos, scanned documents)
- Note processing time

**AI Generation:**
- Test with short and long OCR text
- Monitor generation time (typically 10-30 seconds)

## Browser Compatibility

Test in:
- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)

## Next Steps

After successful testing:
1. Review generated documentation quality
2. Test with real-world screenshots
3. Verify file organization in `docs/sessions/`
4. Check API documentation at `/docs` endpoint

