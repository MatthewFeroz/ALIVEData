const express = require('express');
const cookieParser = require('cookie-parser');
const { WorkOS } = require('@workos-inc/node');
const dotenv = require('dotenv');
const path = require('path');

// Load environment variables
dotenv.config({ path: path.join(__dirname, '.env') });

const app = express();

// Initialize WorkOS
const workos = new WorkOS(process.env.WORKOS_API_KEY, {
  clientId: process.env.WORKOS_CLIENT_ID,
});

// Middleware
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(cookieParser());

// Login endpoint - redirects to WorkOS AuthKit
app.get('/login', async (req, res) => {
  try {
    const authParams = {
      clientId: process.env.WORKOS_CLIENT_ID,
      redirectUri: process.env.WORKOS_REDIRECT_URI || 'http://localhost:3000/callback',
    };

    // Add connectionId, organizationId, or provider if configured
    if (process.env.WORKOS_CONNECTION_ID) {
      authParams.connectionId = process.env.WORKOS_CONNECTION_ID;
    } else if (process.env.WORKOS_PROVIDER) {
      authParams.provider = process.env.WORKOS_PROVIDER;
    } else if (req.query.organizationId) {
      authParams.organizationId = req.query.organizationId;
    }

    const url = workos.userManagement.getAuthorizationUrl(authParams);

    return res.redirect(url);
  } catch (error) {
    console.error('Login error:', error);
    return res.status(500).send('Failed to generate login URL: ' + error.message);
  }
});

// Callback endpoint - handles AuthKit redirect
app.get('/callback', async (req, res) => {
  // The authorization code returned by AuthKit
  const code = req.query.code;

  if (!code) {
    return res.status(400).send('No code provided');
  }

  try {
    const authenticateResponse = await workos.userManagement.authenticateWithCode({
      clientId: process.env.WORKOS_CLIENT_ID,
      code,
      session: {
        sealSession: true,
        cookiePassword: process.env.WORKOS_COOKIE_PASSWORD,
      },
    });

    const { user, sealedSession } = authenticateResponse;

    // Store the session in a cookie
    res.cookie('wos-session', sealedSession, {
      path: '/',
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production', // Only secure in production
      sameSite: 'lax',
    });

    // Use the information in `user` for further business logic.
    console.log(`User ${user.email} authenticated successfully`);

    // Redirect the user to the homepage
    return res.redirect('/');
  } catch (error) {
    console.error('Callback error:', error);
    return res.redirect('/login');
  }
});

// Auth middleware function
async function withAuth(req, res, next) {
  try {
    const session = workos.userManagement.loadSealedSession({
      sessionData: req.cookies['wos-session'],
      cookiePassword: process.env.WORKOS_COOKIE_PASSWORD,
    });

    const { authenticated, reason } = await session.authenticate();

    if (authenticated) {
      return next();
    }

    // If the cookie is missing, redirect to login
    if (!authenticated && reason === 'no_session_cookie_provided') {
      return res.redirect('/login');
    }

    // If the session is invalid, attempt to refresh
    try {
      const { authenticated, sealedSession } = await session.refresh();

      if (!authenticated) {
        return res.redirect('/login');
      }

      // Update the cookie
      res.cookie('wos-session', sealedSession, {
        path: '/',
        httpOnly: true,
        secure: process.env.NODE_ENV === 'production',
        sameSite: 'lax',
      });

      // Redirect to the same route to ensure the updated cookie is used
      return res.redirect(req.originalUrl);
    } catch (e) {
      // Failed to refresh access token, redirect user to login page
      // after deleting the cookie
      res.clearCookie('wos-session');
      res.redirect('/login');
    }
  } catch (error) {
    console.error('Auth middleware error:', error);
    res.clearCookie('wos-session');
    return res.redirect('/login');
  }
}

// Protected route example
app.get('/dashboard', withAuth, async (req, res) => {
  try {
    const session = workos.userManagement.loadSealedSession({
      sessionData: req.cookies['wos-session'],
      cookiePassword: process.env.WORKOS_COOKIE_PASSWORD,
    });

    const { user } = await session.authenticate();

    console.log(`User ${user.firstName || user.email} is logged in`);

    // Render dashboard page or return user data
    res.json({
      user: {
        id: user.id,
        email: user.email,
        firstName: user.firstName,
        lastName: user.lastName,
      },
    });
  } catch (error) {
    console.error('Dashboard error:', error);
    return res.redirect('/login');
  }
});

// Logout endpoint
app.get('/logout', async (req, res) => {
  try {
    const session = workos.userManagement.loadSealedSession({
      sessionData: req.cookies['wos-session'],
      cookiePassword: process.env.WORKOS_COOKIE_PASSWORD,
    });

    const url = await session.getLogoutUrl();

    res.clearCookie('wos-session');
    res.redirect(url);
  } catch (error) {
    console.error('Logout error:', error);
    // Even if there's an error, clear the cookie and redirect
    res.clearCookie('wos-session');
    res.redirect('/login');
  }
});

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ status: 'ok' });
});

// Start server
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
  console.log(`Make sure WORKOS_API_KEY, WORKOS_CLIENT_ID, and WORKOS_COOKIE_PASSWORD are set in .env`);
});

