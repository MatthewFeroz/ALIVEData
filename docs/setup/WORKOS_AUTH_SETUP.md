# Setting Up WorkOS AuthKit with Convex

This guide explains how to configure WorkOS AuthKit authentication for your ALIVE Data application.

## Prerequisites

- Convex project initialized
- WorkOS account (free tier available at https://workos.com/sign-up)

## Step 1: Install Packages

The required packages are already installed:
- `@convex-dev/auth` - Convex Auth integration
- `@convex-dev/workos` - WorkOS AuthKit provider

## Step 2: Configure WorkOS

1. **Sign up for WorkOS** (if you haven't already):
   - Go to https://workos.com/sign-up
   - Create a free account

2. **Set up AuthKit**:
   - In the WorkOS Dashboard, go to **Authentication** → **AuthKit**
   - Click **Set up AuthKit**
   - Follow the setup wizard

3. **Configure Redirect URI**:
   - **IMPORTANT**: The redirect URI must match your actual dev server port!
   - Check what port your app runs on: Look at the terminal when you run `npm run dev`
   - Add your redirect URI: `http://localhost:5000/callback` (replace 5000 with your actual port)
   - Common ports: 3000, 5000, 5173 (Vite default), 8080
   - For production, add your production URL: `https://yourdomain.com/callback`
   - **Example**: If `npm run dev` shows "Local: http://localhost:5000", use `http://localhost:5000/callback`

## Step 3: Get WorkOS Credentials

After setting up AuthKit, you'll need:
- **WORKOS_CLIENT_ID** - Found in WorkOS Dashboard → Configuration
- **WORKOS_API_KEY** - Found in WorkOS Dashboard → API Keys

## Step 4: Configure Convex Environment Variables

1. Go to your Convex Dashboard: https://dashboard.convex.dev
2. Select your project
3. Go to **Settings** → **Environment Variables**
4. Add the following variables:
   - `WORKOS_CLIENT_ID` = `your_client_id_here`
   - `WORKOS_API_KEY` = `your_api_key_here`

## Step 5: Update Convex Auth Configuration

The auth configuration file is already created at `frontend/convex/auth.ts`:

```typescript
import { convexAuth } from "@convex-dev/auth/server";
import { WorkOS } from "@convex-dev/auth/providers/WorkOS";

export const { auth, signIn, signOut, store } = convexAuth({
  providers: [WorkOS],
});
```

## Step 6: Frontend is Already Configured

The frontend has been updated to use WorkOS AuthKit:
- `main.jsx` uses `ConvexProviderWithAuthKit`
- `App.jsx` uses `useConvexAuth` hook
- `Auth.jsx` has a "Sign In with WorkOS" button
- `Layout.jsx` shows sign out button when authenticated

## Step 7: Test Authentication

1. Start your Convex dev server:
   ```bash
   cd frontend
   npx convex dev
   ```

2. Start your frontend:
   ```bash
   npm run dev
   ```

3. Navigate to your app (usually http://localhost:5173)
4. Click "Sign In with WorkOS"
5. You'll be redirected to WorkOS AuthKit sign-in page
6. After signing in, you'll be redirected back to your app

## How It Works

### Authentication Flow

1. User clicks "Sign In with WorkOS"
2. Frontend calls `signIn('workos')` from `@convex-dev/auth/react`
3. User is redirected to WorkOS AuthKit
4. User authenticates (email/password, SSO, etc.)
5. WorkOS redirects back to `/callback` with authorization code
6. Convex exchanges code for user identity
7. User is authenticated and can access protected routes

### Protected Functions

All Convex functions already check authentication:
- `sessions.createSession` - Requires auth, associates session with user
- `sessions.listSessions` - Returns only user's sessions
- `files.uploadScreenshot` - Requires auth, verifies session ownership
- `documentation.generateDocumentation` - Requires auth, verifies session ownership

### User Identity

- Each user gets a unique `tokenIdentifier` from WorkOS
- This identifier is stored in the `userId` field of all sessions
- Users can only see and modify their own sessions

## Troubleshooting

### "Sign In" button doesn't redirect

- Check that `WORKOS_CLIENT_ID` and `WORKOS_API_KEY` are set in Convex dashboard
- Verify the redirect URI matches in WorkOS Dashboard
- Check browser console for errors

### "Not authenticated" errors

- Make sure you're signed in (check navigation bar for sign out button)
- Try signing out and signing back in
- Check Convex dashboard logs for authentication errors

### Redirect URI mismatch

- Ensure redirect URI in WorkOS Dashboard matches your app URL
- For dev: `http://localhost:5173/callback` (or your port)
- For production: `https://yourdomain.com/callback`

### Can't see sessions

- Verify you're signed in with the correct account
- Check that sessions were created after enabling auth
- Old sessions (created before auth) won't be visible

## Next Steps

### Customize AuthKit

You can customize the AuthKit experience in WorkOS Dashboard:
- Branding (logo, colors)
- Email templates
- Password requirements
- SSO providers

### Add SSO Providers

In WorkOS Dashboard → Authentication → SSO:
- Add SAML providers
- Add OIDC providers
- Configure directory sync (SCIM)

### Production Deployment

1. Update redirect URI in WorkOS Dashboard to production URL
2. Ensure environment variables are set in production Convex deployment
3. Test authentication flow in production

## Security Notes

- WorkOS handles all authentication securely
- User identity tokens are managed automatically by Convex
- Session ownership is verified on every operation
- Never expose API keys in client-side code

