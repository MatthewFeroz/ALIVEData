# ALIVE Data Architecture Explanation

## Overview

ALIVE Data is a web application for generating documentation from screenshots using OCR and AI. The application uses a **Convex-based architecture** with a React frontend.

## Architecture

### Frontend (React + Convex)
- **Location**: `frontend/` directory
- **Technology**: React, Vite, TailwindCSS, Convex
- **How it works**:
  - Uses Convex React hooks (`useQuery`, `useMutation`, `useAction`) for real-time data
  - OCR processing is done **client-side** using Tesseract.js (in the browser)
  - AI documentation generation is done **server-side** via Convex actions
  - File storage uses Convex Storage

### Backend (Convex Functions)
- **Location**: `frontend/convex/` directory
- **Technology**: TypeScript, Convex serverless functions
- **Functions**:
  - `sessions.ts` - Session management (create, list, get sessions)
  - `files.ts` - File upload and management (generateUploadUrl, uploadScreenshot, listScreenshots)
  - `ai.ts` - AI documentation generation (summarizeText, summarizeCommands)
  - `documentation.ts` - Documentation storage (saveDocumentation, getDocumentation)
  - `schema.ts` - Database schema definition

### Data Flow

1. **Session Creation**:
   - User clicks "New Session" → `sessions.createSession` mutation
   - Creates session record in Convex database
   - Returns sessionId for navigation

2. **Screenshot Upload**:
   - User uploads image → `files.generateUploadUrl` mutation
   - Gets Convex storage upload URL
   - Uploads file to Convex storage → receives storageId
   - Calls `files.uploadScreenshot` mutation to create screenshot record

3. **OCR Processing**:
   - User clicks "Process OCR" → **Client-side** Tesseract.js processes image
   - Extracted text displayed in UI

4. **Documentation Generation**:
   - User clicks "Generate Documentation" → `ai.summarizeText` action
   - Sends OCR text to OpenAI API
   - Returns generated markdown documentation
   - Calls `documentation.saveDocumentation` mutation to save

5. **Real-time Updates**:
   - All data queries use Convex `useQuery` hooks
   - UI automatically updates when data changes

## Cleanup Status

All unused components have been removed:
- ✅ FastAPI Backend (`app/` directory) - Removed
- ✅ Old Python GUI (`src/` directory) - Removed  
- ✅ Standalone Script (`main.py`) - Removed
- ✅ Deployment configs (`Dockerfile`, `Procfile`, `railway.json`, `render.yaml`) - Removed
- ✅ Related files (`test_setup.py`, `scripts/`, `run_backend.*`, `requirements.txt`, `tests/`) - Removed
- ✅ Unused Convex Functions (`convex/ocr.ts`, `frontend/convex/ocr.ts`) - Removed
- ✅ Unused Frontend Code (`frontend/src/services/api.js`) - Removed

## Current Stack

- **Frontend**: React + Vite + TailwindCSS
- **Backend**: Convex (serverless functions + database + storage)
- **OCR**: Tesseract.js (client-side)
- **AI**: OpenAI API (via Convex actions)
- **Deployment**: Frontend (Vercel), Backend (Convex cloud)

## Key Files

### Frontend
- `frontend/src/App.jsx` - Main app component with routing
- `frontend/src/pages/SessionsList.jsx` - List all sessions
- `frontend/src/pages/SessionDetail.jsx` - Session detail with upload/OCR/docs
- `frontend/src/components/` - Reusable components

### Convex Backend
- `frontend/convex/sessions.ts` - Session CRUD operations
- `frontend/convex/files.ts` - File upload and management
- `frontend/convex/ai.ts` - OpenAI integration for documentation
- `frontend/convex/documentation.ts` - Documentation storage
- `frontend/convex/schema.ts` - Database schema

## Environment Variables

- `VITE_CONVEX_URL` - Convex deployment URL (frontend)
- `OPENAI_API_KEY` - OpenAI API key (Convex backend)

