export interface ElectronAPI {
  // Window tracking
  getWindows: () => Promise<any[]>;
  getWindowInfo: (hwnd: number) => Promise<any>;
  
  // Process monitoring
  getProcesses: () => Promise<any[]>;
  
  // Screenshot capture
  captureScreen: (options?: any) => Promise<string>;
  captureWindow: (hwnd: number) => Promise<string>;
  
  // Event tracking
  startTracking: () => Promise<void>;
  stopTracking: () => Promise<void>;
  onWindowFocusChange: (callback: (event: any, data: any) => void) => void;
  
  // OCR
  extractText: (imagePath: string, options?: any) => Promise<{ text: string; confidence: number; words: any[] }>;
  extractTextFromRegion: (imagePath: string, region: { x: number; y: number; width: number; height: number }) => Promise<{ text: string; confidence: number; words: any[] }>;
  extractTerminalCommand: (imagePath: string, region?: { x: number; y: number; width: number; height: number } | null) => Promise<{ command: string; fullText: string; confidence: number }>;
  
  // Settings
  getSettings: () => Promise<any>;
  saveSettings: (settings: any) => Promise<void>;
  
  // WorkOS Authentication
  workosStartAuth: () => Promise<{ success: boolean }>;
  workosStartSSO: (organizationId: string) => Promise<{ success: boolean }>;
  workosGetUser: () => Promise<{ id: string; email: string; firstName?: string; lastName?: string } | null>;
  workosGetAccessToken: () => Promise<string | null>;
  workosIsAuthenticated: () => Promise<boolean>;
  workosLogout: () => Promise<{ success: boolean }>;
  onWorkOSAuthSuccess: (callback: (data: { user: { id: string; email: string; firstName?: string; lastName?: string }; accessToken: string }) => void) => void;
  onWorkOSAuthError: (callback: (error: string) => void) => void;
}

declare global {
  interface Window {
    electronAPI: ElectronAPI;
  }
}

