# Setting Up Convex Auth

This guide explains how to enable authentication in your ALIVE Data application using Convex Auth.

## Overview

Convex Auth has been integrated into the application. All sessions and data are now user-specific and protected. Users must sign in to create sessions, upload files, and generate documentation.

## Step 1: Enable Convex Auth in Dashboard

1. Go to your Convex Dashboard: https://dashboard.convex.dev
2. Select your project
3. Navigate to **Settings** → **Authentication**
4. Click **Enable Authentication**

## Step 2: Configure Auth Providers

Convex Auth supports multiple authentication methods:

### Email/Password (Recommended for Start)

1. In the Authentication settings, enable **Email/Password**
2. Configure email settings (optional, for password reset emails)
3. Save changes

### OAuth Providers (Optional)

You can also enable:
- **Google** - Sign in with Google
- **GitHub** - Sign in with GitHub
- **Microsoft** - Sign in with Microsoft
- **Apple** - Sign in with Apple

For each provider:
1. Enable the provider
2. Follow the setup instructions to configure OAuth credentials
3. Add the required environment variables if needed

## Step 3: Update Auth Component (If Needed)

The Auth component (`frontend/src/components/Auth.jsx`) currently has a placeholder. Once Convex Auth is configured:

1. Check Convex documentation for the exact auth methods
2. Update the `handleSubmit` function in `Auth.jsx` to use the correct Convex Auth API
3. The component structure is ready - you just need to wire up the actual auth calls

Example (check Convex docs for exact API):
```javascript
import { useSignIn, useSignUp } from 'convex/react'

const signIn = useSignIn()
const signUp = useSignUp()

// Then in handleSubmit:
if (isSignUp) {
  await signUp({ email, password })
} else {
  await signIn({ email, password })
}
```

## Step 4: Test Authentication

1. Start your frontend: `npm run dev` (in the `frontend` directory)
2. Navigate to your app
3. You should see the authentication screen
4. Click "Sign up" to create a new account
5. After signing up, you'll be automatically signed in

## How It Works

### User Identity

- Each user gets a unique `tokenIdentifier` from Convex Auth
- This identifier is stored in the `userId` field of all sessions
- Users can only see and modify their own sessions

### Protected Functions

All Convex functions now check authentication:
- `sessions.createSession` - Requires auth, associates session with user
- `sessions.listSessions` - Returns only user's sessions
- `sessions.getSession` - Verifies user owns the session
- `files.uploadScreenshot` - Requires auth, verifies session ownership
- `documentation.generateDocumentation` - Requires auth, verifies session ownership

### Frontend Protection

- Routes are protected with `ProtectedRoute` component
- Unauthenticated users see the `Auth` component
- Sign out button appears in the navigation when authenticated

## Migration from No Auth

If you had existing sessions before enabling auth:
- Old sessions without `userId` will not be visible to authenticated users
- You may need to migrate existing data or start fresh
- New sessions will automatically include the `userId` field

## Troubleshooting

### "Not authenticated" errors

- Make sure Convex Auth is enabled in the dashboard
- Check that you're signed in (check the navigation bar)
- Try signing out and signing back in

### Can't see sessions

- Verify you're signed in with the correct account
- Check that sessions were created after enabling auth
- Old sessions (created before auth) won't be visible

### Auth UI not showing

- Check that `ConvexAuthProvider` is wrapping your app in `main.jsx`
- Verify Convex Auth is enabled in the dashboard
- Check browser console for errors

## Next Steps

### Adding WorkOS (Enterprise Features)

When you need enterprise features like SSO:
1. Install: `npm install @convex-dev/workos`
2. Configure WorkOS in Convex dashboard
3. Your existing code will work - no changes needed!

### Customizing Auth UI

Edit `frontend/src/components/Auth.jsx` to customize:
- Styling
- Additional fields
- OAuth provider buttons
- Password requirements

## Security Notes

- Passwords are handled securely by Convex
- User identity tokens are managed automatically
- Session ownership is verified on every operation
- Never expose `tokenIdentifier` in client-side code unnecessarily

