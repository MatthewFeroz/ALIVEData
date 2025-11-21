# 🚀 How to Run ALIVE Data Locally

Quick guide to run the app locally for demonstrations.

## Prerequisites

- **Node.js** (v16 or higher) - [Download](https://nodejs.org/)
- **npm** (comes with Node.js)
- **Convex account** (free) - Sign up at [convex.dev](https://convex.dev)

## Step 1: Install Dependencies

Open a terminal in the project root and run:

```bash
cd frontend
npm install
```

## Step 2: Set Up Convex Backend

### 2a. Initialize Convex (First Time Only)

```bash
cd frontend
npx convex dev
```

This will:
- Create your Convex project
- Generate a deployment URL (looks like `https://xxx.convex.cloud`)
- Start the Convex dev server

**Important:** Keep this terminal window open! Copy the deployment URL that appears.

### 2b. Set Up Environment Variables

1. Create `.env.local` file in the `frontend/` folder:
   ```bash
   cd frontend
   # On Windows PowerShell:
   New-Item .env.local
   # Or create manually in your editor
   ```

2. **Choose your mode:**

   **Option A: Demo Mode (No Authentication Required)**
   
   Add to `.env.local`:
   ```env
   VITE_CONVEX_URL=https://your-deployment-url.convex.cloud
   VITE_DEMO_MODE=true
   ```
   
   This bypasses WorkOS authentication - perfect for demos! You'll see a yellow banner indicating demo mode.

   **Option B: Production Mode (With WorkOS Auth)**
   
   Add to `.env.local`:
   ```env
   VITE_CONVEX_URL=https://your-deployment-url.convex.cloud
   VITE_WORKOS_CLIENT_ID=your_workos_client_id_here
   ```
   
   Get your WorkOS Client ID from [WorkOS Dashboard](https://dashboard.workos.com)

## Step 3: Set Up OpenAI API Key (For AI Features)

1. Go to [Convex Dashboard](https://dashboard.convex.dev)
2. Select your project
3. Go to **Settings** → **Environment Variables**
4. Add: `OPENAI_API_KEY` = `sk-your-actual-api-key`
5. Get your API key from [OpenAI Platform](https://platform.openai.com/api-keys)

**Note:** This is only needed if you want to test AI documentation generation. The app will run without it, but that feature won't work.

## Step 4: Start the Frontend

Open a **NEW** terminal window (keep Convex running in the first one):

```bash
cd frontend
npm run dev
```

You should see:
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5000/
```

## Step 5: Open in Browser

Open your browser and go to:
**http://localhost:5000**

## Quick Demo Checklist

Once running, you can demonstrate:

- ✅ **View Sessions** - See existing sessions
- ✅ **Create New Session** - Click "+ New Session"
- ✅ **Upload Screenshots** - Drag & drop images
- ✅ **View Documentation** - Browse generated docs

## Troubleshooting

### "Cannot find module" errors
```bash
cd frontend
rm -rf node_modules package-lock.json  # On Windows: rmdir /s node_modules
npm install
```

### Port 5000 already in use
Vite will automatically use the next available port. Check the terminal output for the actual port.

### Convex connection errors
- Make sure `npx convex dev` is running
- Verify `.env.local` has the correct `VITE_CONVEX_URL`
- Restart the frontend dev server after changing `.env.local`

### Blank screen / Auth errors
- Check that `VITE_WORKOS_CLIENT_ID` is set in `.env.local`
- Or temporarily disable auth to show the app (check `src/App.jsx`)

## What's Running?

You need **2 terminal windows**:

1. **Terminal 1:** `npx convex dev` (Convex backend)
2. **Terminal 2:** `npm run dev` (Frontend)

Both must stay running for the app to work!

## Quick Start Script (Windows)

You can also use the provided batch file:

```cmd
run_frontend.bat
```

But make sure Convex is running first!

## Need Help?

- Check `docs/quick-start/START_HERE.md` for detailed setup
- Check `docs/setup/ENV_FILE_SETUP.md` for environment variable help
- Check `docs/troubleshooting/` for common issues

