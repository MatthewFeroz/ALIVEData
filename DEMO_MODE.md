# 🎭 Demo Mode - Bypass Authentication

Demo mode allows you to run the app locally without setting up WorkOS authentication. Perfect for demonstrations and quick testing!

## How to Enable Demo Mode

1. **Open `.env.local`** in the `frontend/` folder

2. **Add this line:**
   ```env
   VITE_DEMO_MODE=true
   ```

3. **Make sure you still have Convex URL:**
   ```env
   VITE_CONVEX_URL=https://your-deployment-url.convex.cloud
   ```

4. **Restart your dev server** (stop with Ctrl+C, then run `npm run dev` again)

## What Demo Mode Does

✅ **Bypasses WorkOS authentication** - No login required  
✅ **Shows a yellow banner** at the top indicating demo mode  
✅ **All features accessible** - Create sessions, upload screenshots, etc.  
✅ **Uses dummy user** - Shows as "Demo User" (demo@example.com)  

## Example `.env.local` for Demo Mode

```env
# Convex Configuration (Required)
VITE_CONVEX_URL=https://happy-animal-123.convex.cloud

# Enable Demo Mode (Bypasses WorkOS)
VITE_DEMO_MODE=true

# WorkOS not needed in demo mode!
# VITE_WORKOS_CLIENT_ID=not-needed
```

## Disabling Demo Mode

To go back to production mode with real authentication:

1. **Remove or comment out** the `VITE_DEMO_MODE` line:
   ```env
   # VITE_DEMO_MODE=true
   ```

2. **Add WorkOS Client ID:**
   ```env
   VITE_WORKOS_CLIENT_ID=client_01H123ABC456DEF
   ```

3. **Restart your dev server**

## When to Use Demo Mode

- ✅ **Local demonstrations** - Show the app without auth setup
- ✅ **Quick testing** - Test features without configuring WorkOS
- ✅ **Development** - Focus on features, not auth
- ✅ **Presentations** - No login interruptions

## When NOT to Use Demo Mode

- ❌ **Production deployments** - Always use real authentication
- ❌ **Testing auth flows** - Use production mode
- ❌ **User testing** - Use real auth to test the full experience

## Visual Indicator

When demo mode is active, you'll see a yellow banner at the top of the app:

```
🎭 DEMO MODE: Authentication is disabled. All features are accessible without login.
```

This makes it clear to anyone viewing the app that it's running in demo mode.

## Technical Details

- Demo mode uses a mock authentication provider
- All auth hooks (`useAuth`, `useConvexAuth`) return authenticated state
- Convex backend still works normally (queries, mutations)
- Backend auth checks may still apply (depending on your Convex functions)

## Troubleshooting

### "Still asking for login"
- Make sure `VITE_DEMO_MODE=true` (not `"true"` or `True`)
- Restart your dev server after changing `.env.local`
- Check browser console for errors

### "Convex connection errors"
- Demo mode still needs `VITE_CONVEX_URL` set
- Make sure `npx convex dev` is running

### "Features not working"
- Some backend functions may still check authentication
- Check Convex function code - you may need to temporarily disable auth checks there too


