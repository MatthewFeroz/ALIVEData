# Troubleshooting Convex Network Errors

## Common Issues and Fixes

### Issue 1: "Missing VITE_CONVEX_URL"

**Error:** `Missing VITE_CONVEX_URL environment variable`

**Fix:**
1. Check if `.env.local` exists in `frontend/` folder
2. If not, create it:
   ```bash
   cd frontend
   echo VITE_CONVEX_URL=https://content-oriole-437.convex.cloud > .env.local
   ```
3. Restart the dev server (`npm run dev`)

### Issue 2: "Network Error" when creating session

**Possible causes:**
1. Convex functions not deployed
2. Wrong import path
3. Convex URL incorrect
4. Browser CORS issues

**Fix:**
1. **Deploy Convex functions:**
   ```bash
   cd frontend
   npx convex dev --once
   ```

2. **Check browser console (F12)** for specific error

3. **Verify Convex URL:**
   - Check `.env.local` has correct URL
   - Should be: `https://content-oriole-437.convex.cloud`

4. **Check Convex dashboard:**
   - Go to https://dashboard.convex.dev
   - Verify functions are deployed
   - Check logs for errors

### Issue 3: Import path errors

**Error:** `Cannot find module '../../convex/_generated/api'`

**Fix:**
- Import path should be: `import { api } from '../convex/_generated/api'`
- (From `frontend/src/pages/` to `frontend/convex/_generated/`)

### Issue 4: Convex functions not found

**Error:** `api.sessions.createSession is not a function`

**Fix:**
1. Make sure functions are in `frontend/convex/sessions.ts`
2. Run `npx convex dev --once` to regenerate types
3. Restart dev server

## Debugging Steps

1. **Open browser console (F12)**
   - Look for specific error messages
   - Check Network tab for failed requests

2. **Check Convex logs:**
   ```bash
   cd frontend
   npx convex logs
   ```

3. **Verify environment:**
   ```bash
   cd frontend
   echo %VITE_CONVEX_URL%  # Windows
   # or
   echo $VITE_CONVEX_URL  # macOS/Linux
   ```

4. **Test Convex connection:**
   - Open browser console
   - Type: `window.location` to verify you're on the right page
   - Check Network tab for Convex requests

## Quick Fix Checklist

- [ ] `.env.local` exists in `frontend/` folder
- [ ] `VITE_CONVEX_URL` is set correctly
- [ ] Convex functions deployed (`npx convex dev --once`)
- [ ] Dev server restarted after env changes
- [ ] Browser console checked for specific errors
- [ ] Convex dashboard shows functions deployed

## Still Not Working?

1. **Clear browser cache** and hard refresh (Ctrl+Shift+R)
2. **Restart dev server** completely
3. **Check Convex dashboard** for deployment status
4. **Verify Convex URL** matches dashboard

