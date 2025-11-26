// Server-side authentication using Convex HTTP endpoint
// This bypasses AuthKit's client-side token exchange to avoid CORS issues

import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';

const AUTH_STORAGE_KEY = 'workos_auth';

const ServerAuthContext = createContext(null);

export function ServerAuthProvider({ children, convexUrl }) {
  const [user, setUser] = useState(null);
  const [accessToken, setAccessToken] = useState(null);
  const [refreshToken, setRefreshToken] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  // Derive the Convex HTTP URL from the Convex URL
  const convexSiteUrl = convexUrl?.replace('.convex.cloud', '.convex.site');

  // Load saved auth on mount
  useEffect(() => {
    try {
      const saved = localStorage.getItem(AUTH_STORAGE_KEY);
      if (saved) {
        const parsed = JSON.parse(saved);
        if (parsed.accessToken && parsed.user) {
          // Check if token is expired
          try {
            const tokenPayload = JSON.parse(atob(parsed.accessToken.split('.')[1]));
            const isExpired = tokenPayload.exp * 1000 < Date.now();
            
            if (!isExpired) {
              setUser(parsed.user);
              setAccessToken(parsed.accessToken);
              setRefreshToken(parsed.refreshToken);
              console.log('Restored auth session for:', parsed.user.email);
            } else {
              console.log('Saved token expired, clearing');
              localStorage.removeItem(AUTH_STORAGE_KEY);
            }
          } catch (e) {
            // Token parsing failed, clear it
            console.log('Token parsing failed, clearing');
            localStorage.removeItem(AUTH_STORAGE_KEY);
          }
        }
      }
    } catch (e) {
      console.error('Failed to restore auth:', e);
      localStorage.removeItem(AUTH_STORAGE_KEY);
    }
    setIsLoading(false);
  }, []);

  // Save auth to storage when it changes
  useEffect(() => {
    if (user && accessToken) {
      localStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify({
        user,
        accessToken,
        refreshToken,
      }));
    }
  }, [user, accessToken, refreshToken]);

  // Exchange authorization code for tokens via Convex backend
  const exchangeCodeForTokens = useCallback(async (code, redirectUri) => {
    if (!convexSiteUrl) {
      throw new Error('Convex URL not configured');
    }

    setIsLoading(true);
    setError(null);

    try {
      console.log('Exchanging code via Convex backend...', convexSiteUrl);
      const response = await fetch(`${convexSiteUrl}/auth/callback`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ code, redirectUri }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || `Token exchange failed: ${response.status}`);
      }

      console.log('Token exchange successful');

      // WorkOS returns: access_token, refresh_token, user
      if (data.access_token && data.user) {
        setAccessToken(data.access_token);
        setRefreshToken(data.refresh_token);
        setUser(data.user);
        return { success: true, user: data.user };
      } else {
        throw new Error('Invalid response from token exchange');
      }
    } catch (e) {
      console.error('Token exchange error:', e);
      setError(e.message);
      return { success: false, error: e.message };
    } finally {
      setIsLoading(false);
    }
  }, [convexSiteUrl]);

  // Sign out
  const signOut = useCallback(() => {
    setUser(null);
    setAccessToken(null);
    setRefreshToken(null);
    localStorage.removeItem(AUTH_STORAGE_KEY);
  }, []);

  // Get the current access token (for Convex auth)
  const getToken = useCallback(async () => {
    return accessToken;
  }, [accessToken]);

  // Sign in - redirect to WorkOS
  const signIn = useCallback(() => {
    const clientId = import.meta.env.VITE_WORKOS_CLIENT_ID;
    const redirectUri = import.meta.env.VITE_WORKOS_REDIRECT_URI || `${window.location.origin}/callback`;
    
    const authUrl = new URL('https://api.workos.com/user_management/authorize');
    authUrl.searchParams.set('client_id', clientId);
    authUrl.searchParams.set('redirect_uri', redirectUri);
    authUrl.searchParams.set('response_type', 'code');
    authUrl.searchParams.set('provider', 'authkit');
    
    console.log('Redirecting to WorkOS:', authUrl.toString());
    window.location.href = authUrl.toString();
  }, []);

  const value = {
    user,
    isLoading,
    isAuthenticated: !!user,
    error,
    signIn,
    signOut,
    exchangeCodeForTokens,
    getToken,
    accessToken,
  };

  return (
    <ServerAuthContext.Provider value={value}>
      {children}
    </ServerAuthContext.Provider>
  );
}

export function useServerAuth() {
  const context = useContext(ServerAuthContext);
  if (!context) {
    throw new Error('useServerAuth must be used within ServerAuthProvider');
  }
  return context;
}

// Hook that provides auth in the format Convex expects
export function useServerConvexAuth() {
  const { isLoading, isAuthenticated } = useServerAuth();
  
  return {
    isLoading,
    isAuthenticated,
  };
}
