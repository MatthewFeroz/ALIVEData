# Migration Plan: Python FastAPI → TypeScript Convex

## Overview

We're migrating from:
- **Backend**: FastAPI (Python) → Convex (TypeScript)
- **Database**: File system → Convex Database
- **Storage**: Local files → Convex File Storage
- **OCR**: pytesseract (Python) → External API or Tesseract.js

## Migration Steps

### Phase 1: Set Up Convex Project
1. Initialize Convex in frontend
2. Set up schema
3. Create basic functions

### Phase 2: Migrate Session Management
1. Move session creation to Convex
2. Update frontend to use Convex hooks
3. Remove FastAPI session endpoints

### Phase 3: Migrate File Upload
1. Use Convex file storage
2. Update upload endpoints
3. Remove FastAPI file handling

### Phase 4: Migrate OCR Processing
1. Set up OCR service (external API or Tesseract.js)
2. Create Convex actions for OCR
3. Remove FastAPI OCR endpoints

### Phase 5: Migrate AI Documentation
1. Move OpenAI calls to Convex
2. Create documentation generation functions
3. Remove FastAPI AI endpoints

### Phase 6: Cleanup
1. Remove FastAPI backend
2. Remove Python dependencies
3. Update documentation

## Current Architecture

```
Frontend (React)
    ↓
FastAPI Backend (Python)
    ├── Sessions (file system)
    ├── Files (local storage)
    ├── OCR (pytesseract)
    └── AI (OpenAI)
```

## Target Architecture

```
Frontend (React + Convex)
    ↓
Convex Backend (TypeScript)
    ├── Sessions (Convex DB)
    ├── Files (Convex Storage)
    ├── OCR (External API / Tesseract.js)
    └── AI (OpenAI via Convex)
```

## Files to Create/Modify

### New Files:
- `convex/schema.ts` - Database schema
- `convex/sessions.ts` - Session management
- `convex/files.ts` - File handling
- `convex/ocr.ts` - OCR processing
- `convex/ai.ts` - AI documentation
- `convex/_generated/` - Auto-generated types

### Modify:
- `frontend/src/services/api.js` → Use Convex hooks instead
- `frontend/src/pages/*` → Use Convex queries/mutations
- `frontend/package.json` → Add Convex dependencies
- Remove: `app/` folder (FastAPI backend)
- Remove: `requirements.txt` (Python deps)

## OCR Options for TypeScript

### Option 1: Google Cloud Vision API
- Best accuracy
- Costs money (~$1.50 per 1000 images)
- Easy to integrate

### Option 2: AWS Textract
- Good for documents
- Costs money
- AWS integration needed

### Option 3: Tesseract.js
- Free, runs in Node.js
- Lower accuracy than Python version
- Good enough for screenshots

### Option 4: Keep Python OCR in Docker
- Run Python OCR in container
- Call from Convex via HTTP
- More complex but keeps accuracy

## Recommended: Tesseract.js + Google Vision API

- Use Tesseract.js for basic OCR (free)
- Fallback to Google Vision for complex images (paid)
- Best of both worlds

## Timeline Estimate

- Phase 1: 30 minutes (Convex setup)
- Phase 2: 1 hour (Sessions)
- Phase 3: 1 hour (Files)
- Phase 4: 2 hours (OCR)
- Phase 5: 1 hour (AI)
- Phase 6: 30 minutes (Cleanup)

**Total: ~6 hours**

## Let's Start!

