# WorkOS Setup Guide

## ✅ Implementation Complete

WorkOS authentication has been fully integrated into the Electron app. The implementation includes:

- **OAuth Flow**: Standard WorkOS authentication via browser window
- **SSO Support**: Organization-based SSO authentication
- **Secure Token Storage**: Tokens stored using `electron-store` with encryption
- **IPC Communication**: Secure communication between renderer and main process

## Initial Setup

1. **Create WorkOS Account**
   - Go to https://workos.com
   - Sign up for an account
   - Create a new project

2. **Get API Keys**
   - Navigate to API Keys section in WorkOS dashboard
   - Copy your API Key and Client ID
   - Add to `.env` file in `electron-app/` directory:
     ```env
     WORKOS_API_KEY=sk_your_api_key_here
     WORKOS_CLIENT_ID=client_your_client_id_here
     WORKOS_REDIRECT_URI=http://localhost:5173/auth/callback
     ```

3. **Configure Connection or Provider (REQUIRED)**
   - WorkOS requires either a `connectionId`, `organizationId`, or `provider` for OAuth
   - **Option A: Use a Connection ID** (Recommended)
     - Go to Connections section in WorkOS dashboard
     - Create or select a connection (e.g., Email Magic Link, Google OAuth)
     - Copy the Connection ID (starts with `conn_`)
     - Add to `.env`:
       ```env
       WORKOS_CONNECTION_ID=conn_xxxxxxxxxxxxx
       ```
   - **Option B: Use a Provider**
     - Add a provider name directly (e.g., "Google", "GitHub", "Microsoft")
     - Add to `.env`:
       ```env
       WORKOS_PROVIDER=Google
       ```
   - **Option C: Use SSO** (for organization-based authentication)
     - Use the `loginWithSSO()` method with an organizationId instead
     - No environment variable needed for this option

4. **Configure Redirect URI**
   - In WorkOS dashboard, add redirect URI: `http://localhost:5173/auth/callback`
   - For production, add your production URL
   - Note: The redirect URI doesn't need to be a real web server - Electron will handle it

## Authentication Flow

### Standard OAuth Flow
1. User clicks "Sign in with WorkOS" button
2. Electron opens a browser window with WorkOS login page
3. User authenticates (email/password or magic link)
4. WorkOS redirects to callback URL with authorization code
5. Electron captures the code and exchanges it for tokens
6. Tokens are stored securely and user is logged in

### SSO Flow
1. User enters organization ID and clicks "Sign in with SSO"
2. Electron opens browser window with organization SSO provider
3. User authenticates with their organization's SSO
4. WorkOS redirects with authorization code
5. Electron exchanges code for tokens and logs user in

## Architecture

### Main Process (`src/main/auth/workosAuth.js`)
- Uses WorkOS Node SDK (`@workos-inc/node`)
- Handles OAuth URL generation
- Exchanges authorization codes for tokens
- Stores tokens securely using `electron-store`

### IPC Handlers (`src/main/main.js`)
- `workos-start-auth`: Initiates OAuth flow
- `workos-start-sso`: Initiates SSO flow
- `workos-get-user`: Gets current authenticated user
- `workos-get-access-token`: Gets access token
- `workos-is-authenticated`: Checks auth status
- `workos-logout`: Logs out user

### Renderer Process (`src/renderer/services/auth.ts`)
- Communicates with main process via IPC
- Manages auth state in renderer
- Provides auth state change listeners
- Handles auth success/error events

### UI Component (`src/renderer/components/Auth.tsx`)
- Provides login interface
- Supports both standard OAuth and SSO flows
- Shows loading states and error messages

## Usage

### In Your Components

```typescript
import { authService } from './services/auth';

// Check if authenticated
const isAuth = await authService.isAuthenticated();

// Get current user
const user = authService.getUser();

// Get access token
const token = await authService.getAccessToken();

// Logout
await authService.logout();

// Listen for auth state changes
authService.onAuthStateChange((user) => {
  if (user) {
    console.log('User logged in:', user);
  } else {
    console.log('User logged out');
  }
});
```

## Security Considerations

✅ **Implemented:**
- API keys stored in environment variables (never exposed to renderer)
- Tokens stored securely using `electron-store` with encryption
- IPC communication for secure main/renderer separation
- Context isolation enabled in Electron windows

⚠️ **Production Recommendations:**
- Use a more secure encryption key for `electron-store` (currently using a simple key)
- Implement token refresh logic (currently placeholder)
- Add token expiration checking
- Consider using Electron's `safeStorage` API for additional security
- Use HTTPS redirect URIs in production

## Troubleshooting

### Authentication Window Doesn't Open
- Check that `WORKOS_API_KEY` and `WORKOS_CLIENT_ID` are set in `.env`
- Verify the redirect URI matches WorkOS dashboard configuration

### Callback Not Working
- Ensure redirect URI in `.env` matches WorkOS dashboard
- Check browser console for errors in auth window
- Verify WorkOS project is properly configured

### Tokens Not Persisting
- Check that `electron-store` is working correctly
- Verify file permissions for store location
- Check main process console for errors

## Next Steps

1. **Token Refresh**: Implement automatic token refresh before expiration
2. **User Profile**: Add user profile fetching and display
3. **Session Management**: Add session timeout handling
4. **Multi-User Support**: Add support for switching between users

