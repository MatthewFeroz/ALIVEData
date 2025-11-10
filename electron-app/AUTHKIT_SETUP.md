# WorkOS AuthKit Setup Guide

## ✅ AuthKit Integration Complete

WorkOS AuthKit has been integrated into the Electron app using the React SDK. This provides a hosted authentication flow that's easier to use than the User Management API.

## What Changed

- **Migrated from User Management API to AuthKit**
- **Using `@workos-inc/authkit-react` SDK**
- **Hosted authentication flow** (no need to configure connections/providers manually)
- **Simplified authentication** - AuthKit handles the OAuth flow automatically

## Initial Setup

### 1. Install Dependencies

The AuthKit React SDK is already installed:
```bash
npm install @workos-inc/authkit-react
```

### 2. Configure WorkOS Dashboard

1. **Activate AuthKit** in your WorkOS Dashboard
   - Go to the Overview section
   - Click "Set up AuthKit" and follow the instructions

2. **Get API Keys**
   - Navigate to API Keys section in WorkOS dashboard
   - Copy your API Key and Client ID

3. **Configure Redirect URI**
   - In WorkOS Dashboard → Redirects section
   - Add redirect URI: `http://localhost:5173/callback`
   - For production, add your production callback URL

4. **Configure Login Endpoint** (Optional but recommended)
   - In WorkOS Dashboard → Redirects section
   - Set login endpoint: `http://localhost:5173/login`
   - This handles cases where users bookmark the login page

5. **Configure CORS** (Required for Electron)
   - In WorkOS Dashboard → Settings → Authentication → Configure CORS
   - Add your development URL: `http://localhost:5173`
   - Add your production URL when deploying

### 3. Environment Variables

Create or update your `.env` file in the `electron-app` directory:

```env
# WorkOS Configuration (Required)
WORKOS_CLIENT_ID=client_your_client_id_here

# Note: WORKOS_API_KEY is not needed for client-only AuthKit integration
# The API key is only needed for server-side operations

# Convex Configuration (Optional)
CONVEX_URL=https://your-deployment.convex.cloud
CONVEX_DEPLOYMENT_KEY=your_convex_deployment_key

# OpenAI Configuration (Optional)
OPENAI_API_KEY=your_openai_api_key
```

**Important:** The `WORKOS_CLIENT_ID` will be exposed to the renderer process via Vite's environment variable system. This is safe for AuthKit's client-only integration.

## How It Works

### Architecture

1. **AuthKitProvider** (`src/renderer/main.tsx`)
   - Wraps the entire app
   - Handles session management and token refresh
   - Uses `devMode={true}` for Electron (stores refresh token in localStorage)

2. **useAuth Hook** (`src/renderer/components/Auth.tsx`)
   - Provides `user`, `isLoading`, `signIn`, `signOut`
   - Automatically handles authentication state

3. **Callback Handler** (`src/renderer/components/Callback.tsx`)
   - Handles the redirect from WorkOS after authentication
   - AuthKitProvider automatically processes the callback

### Authentication Flow

1. User clicks "Sign in with WorkOS"
2. `signIn()` is called, which redirects to WorkOS hosted login page
3. User authenticates (email/password, magic link, or SSO)
4. WorkOS redirects back to `/callback` with authorization code
5. AuthKitProvider exchanges the code for tokens automatically
6. User is authenticated and can access the app

## Usage

### In Components

```typescript
import { useAuth } from '@workos-inc/authkit-react';

function MyComponent() {
  const { user, isLoading, signIn, signOut } = useAuth();

  if (isLoading) {
    return <div>Loading...</div>;
  }

  if (!user) {
    return <button onClick={signIn}>Sign In</button>;
  }

  return (
    <div>
      <p>Welcome, {user.email}!</p>
      <button onClick={signOut}>Sign Out</button>
    </div>
  );
}
```

### Accessing User Data

The `user` object from `useAuth()` contains:
- `id`: User ID
- `email`: User email
- `firstName`: First name (optional)
- `lastName`: Last name (optional)

### Getting Access Token

```typescript
import { useAuth } from '@workos-inc/authkit-react';

function MyComponent() {
  const { getAccessToken } = useAuth();

  const handleApiCall = async () => {
    const token = await getAccessToken();
    // Use token for API calls
  };
}
```

## Differences from User Management API

### What's Different

- ✅ **No connection/provider configuration needed** - AuthKit handles this
- ✅ **Hosted login page** - WorkOS provides the UI
- ✅ **Automatic token refresh** - AuthKitProvider handles this
- ✅ **Simpler code** - Less boilerplate

### What Stayed the Same

- User authentication flow
- Session management (now handled by AuthKit)
- SSO support (via `signIn({ organizationId })`)

## Troubleshooting

### "Client ID not found" Error

- Make sure `WORKOS_CLIENT_ID` is set in your `.env` file
- Restart the dev server after adding environment variables

### Callback Not Working

- Verify redirect URI in WorkOS dashboard matches `http://localhost:5173/callback`
- Check that CORS is configured in WorkOS dashboard
- Ensure AuthKit is activated in your WorkOS project

### Authentication Window Doesn't Open

- Check browser console for errors
- Verify `WORKOS_CLIENT_ID` is correctly set
- Make sure AuthKit is activated in WorkOS dashboard

### Tokens Not Persisting

- AuthKit uses localStorage in `devMode` (which is enabled for Electron)
- Check browser DevTools → Application → Local Storage
- Verify no errors in console

## Migration Notes

The old User Management API code has been replaced with AuthKit. If you need to access the old implementation, check git history. The main changes:

- Removed `src/main/auth/workosAuth.js` usage (still exists but not used)
- Updated `src/renderer/components/Auth.tsx` to use `useAuth` hook
- Updated `src/renderer/App.tsx` to use AuthKit authentication
- Added `src/renderer/components/Callback.tsx` for callback handling

## Next Steps

1. Test the authentication flow: `npm run dev`
2. Configure your WorkOS connections/providers in the dashboard
3. Set up production redirect URIs
4. Configure logout redirect in WorkOS dashboard

