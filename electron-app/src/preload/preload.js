const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld('electronAPI', {
  // Window tracking
  getWindows: () => ipcRenderer.invoke('get-windows'),
  getWindowInfo: (hwnd) => ipcRenderer.invoke('get-window-info', hwnd),
  
  // Process monitoring
  getProcesses: () => ipcRenderer.invoke('get-processes'),
  
  // Screenshot capture
  captureScreen: (options) => ipcRenderer.invoke('capture-screen', options),
  captureWindow: (hwnd) => ipcRenderer.invoke('capture-window', hwnd),
  
  // Event tracking
  startTracking: () => ipcRenderer.invoke('start-tracking'),
  stopTracking: () => ipcRenderer.invoke('stop-tracking'),
  onWindowFocusChange: (callback) => ipcRenderer.on('window-focus-change', callback),
  
  // OCR
  extractText: (imagePath, options) => ipcRenderer.invoke('extract-text', imagePath, options),
  extractTextFromRegion: (imagePath, region) => ipcRenderer.invoke('extract-text-region', imagePath, region),
  extractTerminalCommand: (imagePath, region) => ipcRenderer.invoke('extract-terminal-command', imagePath, region),
  
  // Settings
  getSettings: () => ipcRenderer.invoke('get-settings'),
  saveSettings: (settings) => ipcRenderer.invoke('save-settings', settings),
  
  // WorkOS Authentication
  workosStartAuth: () => ipcRenderer.invoke('workos-start-auth'),
  workosStartSSO: (organizationId) => ipcRenderer.invoke('workos-start-sso', organizationId),
  workosGetUser: () => ipcRenderer.invoke('workos-get-user'),
  workosGetAccessToken: () => ipcRenderer.invoke('workos-get-access-token'),
  workosIsAuthenticated: () => ipcRenderer.invoke('workos-is-authenticated'),
  workosLogout: () => ipcRenderer.invoke('workos-logout'),
  onWorkOSAuthSuccess: (callback) => ipcRenderer.on('workos-auth-success', (event, data) => callback(data)),
  onWorkOSAuthError: (callback) => ipcRenderer.on('workos-auth-error', (event, error) => callback(error)),
});

