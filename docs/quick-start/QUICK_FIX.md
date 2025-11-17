# Quick Fix for Network Errors

## The Problem

Your console shows errors trying to connect to `:8000/api/sessions/...` - this is the old FastAPI backend that isn't running.

## The Solution

I've updated `SessionDetail.jsx` to use Convex instead of the old API. Now you need to:

### 1. Restart Frontend Dev Server

**IMPORTANT:** Restart your frontend dev server so it picks up the changes:

1. Stop the current server (Ctrl+C in the terminal running `npm run dev`)
2. Start it again:
   ```bash
   cd frontend
   npm run dev
   ```

### 2. Verify .env.local File

The `.env.local` file should be in `frontend/.env.local`:

```
frontend/
├── .env.local          ← Should be here
├── package.json
└── src/
```

**Contents should be:**
```
VITE_CONVEX_URL=https://content-oriole-437.convex.cloud
```

### 3. Deploy Convex Functions

Run this to deploy the new functions:

```bash
cd frontend
npx convex dev --once
```

### 4. Set OpenAI API Key in Convex

```bash
cd frontend
npx convex env set OPENAI_API_KEY sk-your-actual-key-here
```

## After Restarting

1. **Hard refresh browser** (Ctrl+Shift+R)
2. **Check console** - should see Convex URL logged
3. **Try creating a session** - should work without network errors
4. **Check Network tab** - should see requests to `convex.cloud`, not `localhost:8000`

## What Changed

- ✅ `SessionDetail` now uses Convex hooks instead of FastAPI
- ✅ File uploads use Convex storage
- ✅ All API calls go to Convex, not FastAPI backend

## If Still Getting Errors

1. Check browser console for specific error
2. Verify `.env.local` exists and has correct URL
3. Make sure Convex functions are deployed (`npx convex dev --once`)
4. Check Convex dashboard for function errors

