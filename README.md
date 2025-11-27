# ALIVE Data

**Automatically generate documentation from screenshots using OCR and AI.**

ALIVE Data captures screenshots, extracts text using OCR, and uses AI to transform that content into clean, structured markdown documentation.

---

## What It Does

1. **Upload Screenshots** — Drag & drop or select images from your workflow
2. **Extract Text (OCR)** — Tesseract.js extracts readable text from images
3. **Generate Documentation** — OpenAI converts extracted text into well-formatted markdown
4. **Organize by Session** — Group related screenshots into sessions for organized workflows

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                          ALIVE Data                                  │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   ┌──────────────┐    ┌──────────────┐    ┌──────────────────────┐  │
│   │   Frontend   │◄──►│    Convex    │◄──►│      OpenAI API      │  │
│   │  React/Vite  │    │   Backend    │    │  (GPT-4o-mini)       │  │
│   └──────────────┘    └──────────────┘    └──────────────────────┘  │
│         │                    │                                       │
│         │                    ▼                                       │
│         │             ┌──────────────┐                              │
│         │             │   Convex DB  │                              │
│         │             │  + Storage   │                              │
│         │             └──────────────┘                              │
│         │                                                            │
│         ▼                                                            │
│   ┌──────────────┐    ┌──────────────┐                              │
│   │ Tesseract.js │    │    WorkOS    │                              │
│   │ (OCR/Client) │    │    (Auth)    │                              │
│   └──────────────┘    └──────────────┘                              │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Frontend** | React + Vite + Tailwind | Single-page application UI |
| **Backend** | Convex (serverless) | Database, file storage, server functions |
| **OCR** | Tesseract.js | Client-side text extraction from images |
| **AI** | OpenAI GPT-4o-mini | Documentation generation |
| **Auth** | WorkOS AuthKit | User authentication |
| **Hosting** | Vercel (frontend) + Convex Cloud | Production deployment |

---

## Quick Start

### Prerequisites

- **Node.js** 16+ — [Download](https://nodejs.org/)
- **Convex account** (free) — [Sign up](https://convex.dev)
- **OpenAI API key** — [Get one](https://platform.openai.com/api-keys)

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Start Convex Backend

```bash
cd frontend
npx convex dev
```

This will:
- Create your Convex project (first time)
- Generate a deployment URL like `https://xxx.convex.cloud`
- Start the local development server

**Keep this terminal running.** Copy the deployment URL shown.

### 3. Configure Environment Variables

Create `frontend/.env.local`:

```env
# Required: Your Convex deployment URL
VITE_CONVEX_URL=https://your-deployment.convex.cloud

# For Demo Mode (no auth required):
VITE_DEMO_MODE=true

# OR for Production Mode (with auth):
# VITE_WORKOS_CLIENT_ID=your_workos_client_id
```

### 4. Set OpenAI API Key in Convex

1. Go to [Convex Dashboard](https://dashboard.convex.dev)
2. Select your project → **Settings** → **Environment Variables**
3. Add: `OPENAI_API_KEY` = `sk-your-api-key`

### 5. Start Frontend

Open a **new terminal**:

```bash
cd frontend
npm run dev
```

Visit **http://localhost:5000**

---

## Project Structure

```
ALIVEData/
├── frontend/
│   ├── convex/                  # Convex backend functions
│   │   ├── schema.ts            # Database schema
│   │   ├── sessions.ts          # Session management
│   │   ├── files.ts             # File upload/storage
│   │   ├── ai.ts                # OpenAI integration
│   │   ├── documentation.ts     # Documentation storage
│   │   └── auth.config.ts       # WorkOS auth config
│   │
│   ├── src/
│   │   ├── App.jsx              # Main app + routing
│   │   ├── components/          # Reusable UI components
│   │   │   ├── Auth.jsx         # Authentication UI
│   │   │   ├── FileUpload.jsx   # Drag & drop upload
│   │   │   ├── Layout.jsx       # App layout/navigation
│   │   │   └── DemoBanner.jsx   # Demo mode indicator
│   │   ├── pages/
│   │   │   ├── Landing.jsx      # Home page
│   │   │   ├── SessionsList.jsx # All sessions view
│   │   │   ├── SessionDetail.jsx# Single session view
│   │   │   └── Settings.jsx     # User settings
│   │   └── utils/
│   │       ├── authHooks.jsx    # Auth hook wrappers
│   │       └── demoAuth.jsx     # Demo mode auth
│   │
│   ├── .env.local               # Environment variables (create this)
│   └── package.json
│
└── README.md                    # This file
```

---

## Database Schema

Convex stores all data in these tables:

| Table | Purpose |
|-------|---------|
| `sessions` | Recording sessions with metadata (userId, status, timestamps) |
| `screenshots` | Uploaded images linked to sessions |
| `ocrResults` | Extracted text from screenshots |
| `documentation` | AI-generated markdown documentation |

All data is user-isolated — users can only access their own sessions.

---

## Features

### Session Management
- Create new documentation sessions
- Track session status (active, processing, completed)
- View all sessions with metadata

### Screenshot Upload
- Drag & drop or click to upload
- Supports PNG, JPG, JPEG, GIF, BMP
- Files stored in Convex file storage

### OCR Processing
- Client-side text extraction using Tesseract.js
- Processes images without server upload
- Handles terminal output, code, UI text

### AI Documentation
- Converts OCR text to structured markdown
- Creates README-style documentation
- Formats code blocks, headers, lists properly

---

## Demo Mode

Run the app without authentication setup:

```env
# In frontend/.env.local
VITE_CONVEX_URL=https://your-deployment.convex.cloud
VITE_DEMO_MODE=true
```

When active, you'll see a yellow banner: "🎭 DEMO MODE"

All features work, but without real user authentication.

---

## Production Deployment

### Deploy Convex Backend

```bash
cd frontend
npx convex deploy
```

Set environment variables in Convex Dashboard (Production):
- `OPENAI_API_KEY`

### Deploy Frontend to Vercel

**Option A: CLI**
```bash
cd frontend
npm install -g vercel
vercel login
vercel --prod
```

**Option B: GitHub Integration**
1. Push to GitHub
2. Import project at [vercel.com](https://vercel.com)
3. Set root directory to `frontend`
4. Add environment variables

### Required Environment Variables

**Convex Dashboard (Production):**
```
OPENAI_API_KEY=sk-your-key
```

**Vercel Dashboard:**
```
VITE_CONVEX_URL=https://your-project.convex.cloud
VITE_WORKOS_CLIENT_ID=your-workos-client-id
VITE_WORKOS_REDIRECT_URI=https://your-app.vercel.app/callback
```

### WorkOS Setup (Production Auth)

1. Create account at [workos.com](https://workos.com)
2. Set up AuthKit
3. Add redirect URI: `https://your-app.vercel.app/callback`
4. Copy Client ID to Vercel environment variables

---

## Troubleshooting

### "Missing VITE_CONVEX_URL"
- Create `frontend/.env.local` with your Convex URL
- Restart the dev server after changes

### Convex connection errors
- Ensure `npx convex dev` is running
- Check URL matches dashboard deployment

### OCR not working
- Check browser console for errors
- Try a clearer, higher-contrast image

### AI generation fails
- Verify `OPENAI_API_KEY` is set in Convex dashboard
- Check API key has credits available
- Check Convex logs for errors

### Auth not working (Production)
- Verify redirect URI in WorkOS matches exactly
- Check all auth environment variables are set
- Use Demo Mode for development

---

## Development

### Running Locally

You need **two terminals**:

1. **Terminal 1:** `npx convex dev` (Convex backend)
2. **Terminal 2:** `npm run dev` (Frontend)

### Convex Commands

```bash
# Start development server
npx convex dev

# Deploy to production
npx convex deploy

# View logs
npx convex logs

# Open dashboard
npx convex dashboard
```

### Making Changes

- **Frontend**: Edit files in `frontend/src/` — hot reloads automatically
- **Backend**: Edit files in `frontend/convex/` — syncs with `npx convex dev`

---

## Tech Stack

| Category | Technology |
|----------|------------|
| Framework | React 18 |
| Build Tool | Vite 5 |
| Styling | Tailwind CSS |
| Backend | Convex |
| Auth | WorkOS AuthKit |
| OCR | Tesseract.js |
| AI | OpenAI GPT-4o-mini |
| Markdown | react-markdown |
| File Upload | react-dropzone |

---

## License

[Add your license here]
