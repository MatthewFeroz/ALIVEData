# Quick Start Guide - Testing Your ALIVE Data Web App

## Step-by-Step Testing Instructions

### 1. Run Setup Test (Optional but Recommended)

```bash
python test_setup.py
```

This will check:
- Python version
- Project structure
- Installed dependencies
- Environment configuration
- Tesseract OCR availability

### 2. Install Missing Dependencies

If the test shows missing packages, install them:

```bash
pip install -r requirements.txt
```

For frontend dependencies:
```bash
cd frontend
npm install
cd ..
```

### 3. Configure Environment

Create a `.env` file in the root directory:

**Windows:**
```cmd
copy .env.example .env
```

**macOS/Linux:**
```bash
cp .env.example .env
```

Then edit `.env` and add your OpenAI API key:
```
OPENAI_API_KEY=sk-your-actual-api-key-here
```

### 4. Start the Backend Server

**Option A: Using the batch script (Windows)**
```cmd
run_backend.bat
```

**Option B: Using Python directly**
```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Expected output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**Verify it's working:**
- Open browser: http://localhost:8000
- Should see: `{"message":"ALIVE Data API","version":"1.0.0","docs":"/docs"}`
- API Docs: http://localhost:8000/docs

### 5. Start the Frontend (New Terminal/Command Prompt)

**Option A: Using the batch script (Windows)**
```cmd
run_frontend.bat
```

**Option B: Using npm directly**
```bash
cd frontend
npm run dev
```

**Expected output:**
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:3000/
```

**Verify it's working:**
- Open browser: http://localhost:3000
- Should see the ALIVE Data interface with navigation

### 6. Test the Application

#### Test 1: Create a Session
1. Click **"+ New Session"** button
2. Should redirect to session detail page
3. Session ID appears in URL

#### Test 2: Upload a Screenshot
1. On session page, go to **"Upload Screenshot"** tab
2. Drag & drop an image OR click to select
3. Supported: PNG, JPG, JPEG, GIF, BMP
4. Should see upload progress and success

#### Test 3: View Screenshots
1. Click **"Screenshots"** tab
2. Should see uploaded image(s) in a grid

#### Test 4: Process OCR
1. In Screenshots tab, click **"Process OCR"** on any image
2. Wait for processing (may take a few seconds)
3. Should automatically switch to **"OCR Text"** tab
4. Extracted text should appear

#### Test 5: Generate Documentation
1. In **"OCR Text"** tab, review/edit the text
2. Click **"Generate Documentation"** button
3. Wait for AI processing (10-30 seconds)
4. Should automatically switch to **"Documentation"** tab
5. Formatted markdown documentation appears

#### Test 6: View Session List
1. Click **"Sessions"** in navigation
2. Should see all created sessions in a grid

### 7. Test API Directly (Optional)

Open http://localhost:8000/docs in your browser:

1. **Create Session:**
   - Expand `POST /api/sessions`
   - Click "Try it out"
   - Click "Execute"
   - Copy the `session_id` from response

2. **Upload Screenshot:**
   - Expand `POST /api/sessions/{session_id}/screenshots`
   - Enter session_id
   - Click "Choose File" and select an image
   - Click "Execute"

3. **Process OCR:**
   - Expand `POST /api/sessions/{session_id}/ocr`
   - Enter session_id and screenshot filename
   - Click "Execute"

4. **Generate Documentation:**
   - Expand `POST /api/sessions/{session_id}/generate`
   - Enter session_id and OCR text
   - Click "Execute"

## Troubleshooting

### Backend won't start
- **Port 8000 in use:** Change port: `--port 8001`
- **Module not found:** Run `pip install -r requirements.txt`
- **Import errors:** Make sure you're in the project root directory

### Frontend won't start
- **Port 3000 in use:** Vite will auto-use next available port
- **npm errors:** Run `npm install` in frontend directory
- **Module errors:** Delete `node_modules` and `package-lock.json`, then `npm install`

### Screenshots not uploading
- Check browser console (F12) for errors
- Verify backend is running
- Check file size (max 10MB)
- Verify file format is supported

### OCR not working
- Verify Tesseract is installed: `tesseract --version`
- Check backend logs for errors
- Try with a clear, high-contrast image

### Documentation generation fails
- Verify OpenAI API key in `.env`
- Check API key has credits
- Check backend logs for detailed errors

### CORS errors
- Verify backend is running on port 8000
- Check `app/core/config.py` CORS_ORIGINS includes `http://localhost:3000`

## What to Check

- [ ] Backend starts without errors
- [ ] Frontend starts without errors  
- [ ] Can access http://localhost:3000
- [ ] Can access http://localhost:8000/docs
- [ ] Can create a session
- [ ] Can upload a screenshot
- [ ] Can process OCR
- [ ] Can generate documentation
- [ ] Documentation looks correct
- [ ] Can navigate between pages

## Need Help?

- Check `TESTING.md` for detailed testing guide
- Check `README.md` for full documentation
- Review backend logs for error messages
- Check browser console (F12) for frontend errors

