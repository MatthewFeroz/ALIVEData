# Quick Start Guide

## Prerequisites

1. **Node.js** (v18 or higher) - [Download](https://nodejs.org/)
2. **Convex account** - Sign up at [convex.dev](https://convex.dev)
3. **OpenAI API key** - Get from [platform.openai.com](https://platform.openai.com)

## Setup Steps

### 1. Install Frontend Dependencies

```bash
cd frontend
npm install
```

### 2. Set Up Convex Backend

```bash
cd frontend/convex
npx convex dev
```

**First time setup:**
- This will prompt you to log in to Convex
- Create a new project or select existing one
- It will generate a `convex.json` file and give you a deployment URL

### 3. Configure Environment Variables

**Frontend (.env.local):**
Create `frontend/.env.local` file:
```env
VITE_CONVEX_URL=https://your-project.convex.cloud
```

**Convex Dashboard:**
1. Go to your Convex dashboard
2. Navigate to Settings → Environment Variables
3. Add: `OPENAI_API_KEY` = `sk-your-openai-api-key`

### 4. Run the Application

**Terminal 1 - Convex Backend:**
```bash
cd frontend/convex
npx convex dev
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

Or use the provided scripts:
- Windows: `run_frontend.bat`
- Mac/Linux: `./run_frontend.sh`

### 5. Open in Browser

The frontend will be available at: `http://localhost:5173`

## Quick Commands

```bash
# Install dependencies
cd frontend && npm install

# Run Convex backend (in frontend/convex/)
npx convex dev

# Run frontend (in frontend/)
npm run dev

# Build for production
cd frontend && npm run build
```

## Troubleshooting

**Missing VITE_CONVEX_URL:**
- Make sure you've run `npx convex dev` first
- Check that `.env.local` exists in `frontend/` directory
- Verify the URL matches your Convex deployment

**Convex connection errors:**
- Make sure `npx convex dev` is running
- Check that your Convex project is active
- Verify environment variables in Convex dashboard

**OpenAI errors:**
- Check that `OPENAI_API_KEY` is set in Convex dashboard
- Verify your API key is valid and has credits

