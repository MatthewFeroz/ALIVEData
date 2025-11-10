const { WorkOS } = require('@workos-inc/node');
const path = require('path');

// electron-store v11+ uses ES modules, so we need to use dynamic import or require default
let Store;
try {
  // Try CommonJS require first
  Store = require('electron-store');
  // If it's an ES module, it might export default
  if (Store.default) {
    Store = Store.default;
  }
} catch (e) {
  // Fallback: use dynamic import (but this is async, so we'll handle it differently)
  console.error('Failed to load electron-store:', e);
}

// Load environment variables BEFORE initializing WorkOS
// This ensures .env file is loaded from electron-app directory
require('dotenv').config({ path: path.join(__dirname, '../../../.env') });

// Initialize WorkOS client
const workos = new WorkOS(process.env.WORKOS_API_KEY);

// Initialize secure store for tokens
const store = new Store({
  name: 'auth',
  encryptionKey: 'alive-data-auth-key', // In production, use a more secure key
});

class WorkOSAuth {
  constructor() {
    this.clientId = process.env.WORKOS_CLIENT_ID;
    this.redirectUri = process.env.WORKOS_REDIRECT_URI || 'http://localhost:5173/auth/callback';
    this.connectionId = process.env.WORKOS_CONNECTION_ID || null;
    this.provider = process.env.WORKOS_PROVIDER || null;
  }

  /**
   * Get authorization URL for OAuth flow
   * Requires either connectionId, organizationId, or provider
   */
  getAuthorizationUrl(state = null, options = {}) {
    const authParams = {
      clientId: this.clientId,
      redirectUri: this.redirectUri,
      state: state || this.generateState(),
    };

    // Add connectionId, organizationId, or provider (required by WorkOS)
    if (options.connectionId || this.connectionId) {
      authParams.connectionId = options.connectionId || this.connectionId;
    } else if (options.organizationId) {
      authParams.organizationId = options.organizationId;
    } else if (options.provider || this.provider) {
      authParams.provider = options.provider || this.provider;
    } else {
      // If none provided, throw a helpful error
      throw new Error(
        'WorkOS requires either a connectionId, organizationId, or provider. ' +
        'Please set WORKOS_CONNECTION_ID or WORKOS_PROVIDER in your .env file, ' +
        'or use SSO with an organizationId.'
      );
    }

    return workos.userManagement.getAuthorizationUrl(authParams);
  }

  /**
   * Exchange authorization code for access token
   */
  async exchangeCodeForToken(code) {
    try {
      const { user, accessToken, refreshToken } = await workos.userManagement.authenticateWithCode({
        clientId: this.clientId,
        code,
      });

      // Store tokens securely
      this.saveAuthState({
        user: {
          id: user.id,
          email: user.email,
          firstName: user.firstName,
          lastName: user.lastName,
        },
        accessToken,
        refreshToken,
      });

      return {
        user: {
          id: user.id,
          email: user.email,
          firstName: user.firstName,
          lastName: user.lastName,
        },
        accessToken,
      };
    } catch (error) {
      console.error('Failed to exchange code for token:', error);
      throw error;
    }
  }

  /**
   * Get current user from stored auth state
   */
  getCurrentUser() {
    const authState = store.get('authState');
    return authState ? authState.user : null;
  }

  /**
   * Get access token from stored auth state
   */
  getAccessToken() {
    const authState = store.get('authState');
    return authState ? authState.accessToken : null;
  }

  /**
   * Check if user is authenticated
   */
  isAuthenticated() {
    const authState = store.get('authState');
    return !!(authState && authState.user && authState.accessToken);
  }

  /**
   * Refresh access token using refresh token
   */
  async refreshAccessToken() {
    const authState = store.get('authState');
    if (!authState || !authState.refreshToken) {
      throw new Error('No refresh token available');
    }

    try {
      // Note: WorkOS Node SDK doesn't have a direct refresh method
      // You may need to implement this using the WorkOS API directly
      // For now, we'll return the existing token
      // In production, implement proper token refresh logic
      return authState.accessToken;
    } catch (error) {
      console.error('Failed to refresh token:', error);
      throw error;
    }
  }

  /**
   * Logout user and clear stored auth state
   */
  logout() {
    store.delete('authState');
  }

  /**
   * Save auth state to secure store
   */
  saveAuthState(authState) {
    store.set('authState', authState);
  }

  /**
   * Generate random state for OAuth flow
   */
  generateState() {
    return Math.random().toString(36).substring(2, 15) + 
           Math.random().toString(36).substring(2, 15);
  }

  /**
   * Get SSO authorization URL for an organization
   */
  getSSOAuthorizationUrl(organizationId, state = null) {
    return workos.userManagement.getAuthorizationUrl({
      clientId: this.clientId,
      redirectUri: this.redirectUri,
      organizationId,
      state: state || this.generateState(),
    });
  }
}

module.exports = new WorkOSAuth();

