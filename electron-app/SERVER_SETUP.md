# Backend Server Setup

## Overview

This server provides backend API endpoints for WorkOS AuthKit authentication with cookie-based session management.

## Installation

Dependencies are already installed:
- `express` - Web server framework
- `cookie-parser` - Cookie parsing middleware
- `@workos-inc/node` - WorkOS Node SDK (already installed)

## Environment Variables

Add these to your `.env` file in the `electron-app` directory:

```env
# WorkOS Configuration (Required)
WORKOS_API_KEY=sk_your_api_key_here
WORKOS_CLIENT_ID=client_your_client_id_here
WORKOS_REDIRECT_URI=http://localhost:3000/callback

# Cookie Password (Required - must be at least 32 characters)
# Generate with: openssl rand -base64 24
WORKOS_COOKIE_PASSWORD=your_secure_password_here_min_32_chars

# Optional: For login endpoint
WORKOS_CONNECTION_ID=conn_xxxxxxxxxxxxx
# OR
WORKOS_PROVIDER=Google

# Server Configuration
PORT=3000
NODE_ENV=development
```

## Running the Server

```bash
cd electron-app
npm run server
```

Or for development with auto-reload:
```bash
npm install -g nodemon  # if not already installed
npm run dev:server
```

## API Endpoints

### GET `/login`
Redirects to WorkOS AuthKit login page.

**Query Parameters:**
- `organizationId` (optional) - For SSO login

**Example:**
```
http://localhost:3000/login
http://localhost:3000/login?organizationId=org_xxxxx
```

### GET `/callback`
Handles the OAuth callback from WorkOS. Exchanges authorization code for user session and sets secure cookie.

**Query Parameters:**
- `code` (required) - Authorization code from WorkOS

### GET `/dashboard`
Protected route that requires authentication. Returns user information.

**Headers:**
- Cookie: `wos-session` (set automatically after login)

**Response:**
```json
{
  "user": {
    "id": "user_xxxxx",
    "email": "user@example.com",
    "firstName": "John",
    "lastName": "Doe"
  }
}
```

### GET `/logout`
Logs out the user, clears the session cookie, and redirects to WorkOS logout URL.

### GET `/health`
Health check endpoint. Returns server status.

**Response:**
```json
{
  "status": "ok"
}
```

## Middleware

### `withAuth`
Protects routes that require authentication. Automatically:
- Validates session cookie
- Refreshes expired sessions
- Redirects to `/login` if not authenticated

**Usage:**
```javascript
app.get('/protected-route', withAuth, (req, res) => {
  // This route requires authentication
  res.json({ message: 'Protected content' });
});
```

## Session Management

Sessions are stored in HTTP-only cookies named `wos-session`. The session is:
- **Sealed** (encrypted) using `WORKOS_COOKIE_PASSWORD`
- **HttpOnly** (not accessible via JavaScript)
- **Secure** (HTTPS only in production)
- **SameSite: lax** (CSRF protection)

## Integration with Electron App

This server can be used as a backend API for your Electron app:

1. **Start the server:**
   ```bash
   npm run server
   ```

2. **Update Electron app to call server endpoints:**
   - Use `fetch()` or `axios` to call server endpoints
   - Server handles authentication and session management
   - Electron app receives user data from server

3. **Example API call from Electron:**
   ```javascript
   // In your Electron renderer process
   const response = await fetch('http://localhost:3000/dashboard', {
     credentials: 'include' // Include cookies
   });
   const data = await response.json();
   ```

## Troubleshooting

### "No code provided" Error
- Make sure redirect URI in WorkOS dashboard matches `WORKOS_REDIRECT_URI`
- Check that WorkOS is redirecting correctly

### "Cookie password must be at least 32 characters"
- Generate a secure password: `openssl rand -base64 24`
- Update `WORKOS_COOKIE_PASSWORD` in `.env`

### "Failed to generate login URL"
- Check that `WORKOS_CLIENT_ID` is set correctly
- If using connection/provider, ensure `WORKOS_CONNECTION_ID` or `WORKOS_PROVIDER` is set
- Or pass `organizationId` as query parameter

### Session Not Persisting
- Check that cookies are being sent with requests (`credentials: 'include'`)
- Verify `WORKOS_COOKIE_PASSWORD` is correct
- Check browser/Electron cookie settings

## Notes

- The server runs on port 3000 by default (configurable via `PORT` env var)
- In production, set `NODE_ENV=production` for secure cookies
- The server is separate from your Electron app - you can run both simultaneously
- For Electron, you may want to use IPC to communicate between renderer and main process, then main process calls the server

