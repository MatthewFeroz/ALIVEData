// WorkOS authentication service
// Uses IPC to communicate with main process where WorkOS SDK runs

export interface AuthUser {
  id: string;
  email: string;
  firstName?: string;
  lastName?: string;
}

class AuthService {
  private user: AuthUser | null = null;
  private accessToken: string | null = null;
  private authListeners: Array<(user: AuthUser | null) => void> = [];

  constructor() {
    // Load stored auth state from main process
    this.loadAuthState();
    
    // Listen for auth success events from main process
    if (window.electronAPI?.onWorkOSAuthSuccess) {
      window.electronAPI.onWorkOSAuthSuccess((authResult: { user: AuthUser; accessToken: string }) => {
        this.user = authResult.user;
        this.accessToken = authResult.accessToken;
        this.notifyListeners(this.user);
      });
    }
    
    // Listen for auth errors
    if (window.electronAPI?.onWorkOSAuthError) {
      window.electronAPI.onWorkOSAuthError((error: string) => {
        console.error('WorkOS auth error:', error);
        this.user = null;
        this.accessToken = null;
        this.notifyListeners(null);
      });
    }
  }

  private async loadAuthState() {
    try {
      if (window.electronAPI?.workosIsAuthenticated && await window.electronAPI.workosIsAuthenticated()) {
        this.user = await window.electronAPI.workosGetUser();
        this.accessToken = await window.electronAPI.workosGetAccessToken();
      }
    } catch (error) {
      console.error('Failed to load auth state:', error);
      this.user = null;
      this.accessToken = null;
    }
  }

  /**
   * Start WorkOS OAuth flow
   * Opens a browser window for authentication
   */
  async login(): Promise<AuthUser> {
    try {
      if (!window.electronAPI?.workosStartAuth) {
        throw new Error('WorkOS authentication not available');
      }
      
      await window.electronAPI.workosStartAuth();
      
      // Wait for auth success event (handled in constructor)
      // Return a promise that resolves when auth completes
      return new Promise((resolve, reject) => {
        const successHandler = (authResult: { user: AuthUser; accessToken: string }) => {
          this.user = authResult.user;
          this.accessToken = authResult.accessToken;
          this.removeAuthListeners();
          resolve(authResult.user);
        };
        
        const errorHandler = (error: string) => {
          this.removeAuthListeners();
          reject(new Error(error));
        };
        
        if (window.electronAPI?.onWorkOSAuthSuccess) {
          window.electronAPI.onWorkOSAuthSuccess(successHandler);
        }
        
        if (window.electronAPI?.onWorkOSAuthError) {
          window.electronAPI.onWorkOSAuthError(errorHandler);
        }
      });
    } catch (error: any) {
      console.error('Login failed:', error);
      throw error;
    }
  }

  /**
   * Start WorkOS SSO flow for an organization
   */
  async loginWithSSO(organizationId: string): Promise<void> {
    try {
      if (!window.electronAPI?.workosStartSSO) {
        throw new Error('WorkOS SSO not available');
      }
      
      await window.electronAPI.workosStartSSO(organizationId);
      
      // Wait for auth success event
      return new Promise((resolve, reject) => {
        const successHandler = (authResult: { user: AuthUser; accessToken: string }) => {
          this.user = authResult.user;
          this.accessToken = authResult.accessToken;
          this.removeAuthListeners();
          resolve();
        };
        
        const errorHandler = (error: string) => {
          this.removeAuthListeners();
          reject(new Error(error));
        };
        
        if (window.electronAPI?.onWorkOSAuthSuccess) {
          window.electronAPI.onWorkOSAuthSuccess(successHandler);
        }
        
        if (window.electronAPI?.onWorkOSAuthError) {
          window.electronAPI.onWorkOSAuthError(errorHandler);
        }
      });
    } catch (error: any) {
      console.error('SSO login failed:', error);
      throw error;
    }
  }

  /**
   * Logout user
   */
  async logout(): Promise<void> {
    try {
      if (window.electronAPI?.workosLogout) {
        await window.electronAPI.workosLogout();
      }
      this.user = null;
      this.accessToken = null;
      this.notifyListeners(null);
    } catch (error) {
      console.error('Logout failed:', error);
      throw error;
    }
  }

  /**
   * Check if user is authenticated
   */
  async isAuthenticated(): Promise<boolean> {
    try {
      if (window.electronAPI?.workosIsAuthenticated) {
        const authenticated = await window.electronAPI.workosIsAuthenticated();
        if (authenticated && !this.user) {
          // Reload auth state if authenticated but not loaded
          await this.loadAuthState();
        }
        return authenticated;
      }
      return false;
    } catch (error) {
      console.error('Failed to check authentication:', error);
      return false;
    }
  }

  /**
   * Get current user
   */
  getUser(): AuthUser | null {
    return this.user;
  }

  /**
   * Get access token
   */
  async getAccessToken(): Promise<string | null> {
    if (!this.accessToken && window.electronAPI?.workosGetAccessToken) {
      this.accessToken = await window.electronAPI.workosGetAccessToken();
    }
    return this.accessToken;
  }

  /**
   * Subscribe to auth state changes
   */
  onAuthStateChange(callback: (user: AuthUser | null) => void) {
    this.authListeners.push(callback);
    return () => {
      this.authListeners = this.authListeners.filter(cb => cb !== callback);
    };
  }

  private notifyListeners(user: AuthUser | null) {
    this.authListeners.forEach(callback => callback(user));
  }

  private removeAuthListeners() {
    // Note: In a real implementation, you'd want to properly remove IPC listeners
    // For now, this is a placeholder
  }
}

export const authService = new AuthService();

