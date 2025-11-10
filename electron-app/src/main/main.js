const { app, BrowserWindow, ipcMain, session } = require('electron');
const path = require('path');
const isDev = process.env.NODE_ENV === 'development';

// Suppress cache-related errors and Autofill protocol errors
// These must be set BEFORE app.whenReady()

// Set user data path to avoid permission issues (Windows)
if (process.platform === 'win32') {
  const userDataPath = path.join(require('os').homedir(), 'AppData', 'Roaming', 'ALIVE Data');
  app.setPath('userData', userDataPath);
  
  // Additional switches to reduce cache-related errors
  app.commandLine.appendSwitch('disable-gpu-sandbox');
  app.commandLine.appendSwitch('disable-software-rasterizer');
}

// Disable Autofill features completely to prevent DevTools protocol errors
// These flags prevent Autofill from being initialized, which stops DevTools from trying to use it
app.commandLine.appendSwitch('disable-features', 'AutofillServerCommunication,AutofillEnableAccountWalletStorage,PasswordManager,Autofill');
app.commandLine.appendSwitch('disable-background-networking');
app.commandLine.appendSwitch('disable-sync');

// CRITICAL: Suppress Chromium console logging for DevTools protocol errors
// These must be set before Electron spawns Chromium
// Note: log-level 2 suppresses warnings but keeps errors - we'll filter specific errors instead
app.commandLine.appendSwitch('log-level', '2'); // Suppress info (3) but keep errors visible for filtering
app.commandLine.appendSwitch('silent-debugger-extension-api');

// Suppress Chromium's internal error logging
if (process.platform === 'win32') {
  // On Windows, redirect Chromium logs to null
  process.env.ELECTRON_ENABLE_LOGGING = '0';
  process.env.ELECTRON_LOG_ASAR_READS = '0';
}

// Suppress console errors for cache and Autofill issues (they're harmless)
const originalConsoleError = console.error;
const originalStderrWrite = process.stderr.write.bind(process.stderr);

// Buffer for partial stderr messages (in case messages are split across chunks)
let stderrBuffer = '';

// Filter stderr output to suppress Autofill and cache errors
// This intercepts ALL stderr writes, including from child processes
process.stderr.write = function(chunk, encoding, fd) {
  if (!chunk) return true;
  
  const message = chunk.toString();
  
  // Add to buffer to handle multi-chunk messages
  stderrBuffer += message;
  
  // Check if buffer contains complete lines (has newline) or is a single line
  const hasNewline = stderrBuffer.includes('\n');
  
  if (!hasNewline && stderrBuffer.length < 500) {
    // Wait for more data if it's a partial message and buffer is small
    return true;
  }
  
  // Split by newlines to check each line
  const lines = stderrBuffer.split(/\r?\n/);
  
  // Keep the last incomplete line in buffer (if no newline at end)
  if (!message.endsWith('\n') && !message.endsWith('\r')) {
    stderrBuffer = lines.pop() || '';
  } else {
    stderrBuffer = '';
  }
  
  // Check each complete line with very aggressive pattern matching
  const filteredLines = lines.filter(line => {
    if (!line || line.trim().length === 0) return true; // Keep empty lines
    
    // More aggressive pattern matching for Autofill errors (case-insensitive, partial matches)
    const isAutofillError = 
      /autofill/i.test(line) && (
        /enable/i.test(line) ||
        /setAddresses/i.test(line) ||
        /wasn't found/i.test(line) ||
        /failed/i.test(line) ||
        /ERROR:CONSOLE/i.test(line)
      );
    
    const isCacheError =
      /Unable to move the cache/i.test(line) ||
      /Unable to create cache/i.test(line) ||
      /Gpu Cache Creation failed/i.test(line);
    
    // Suppress if it matches any error pattern
    return !(isAutofillError || isCacheError);
  });
  
  // Write filtered lines
  if (filteredLines.length > 0 || stderrBuffer) {
    const toWrite = filteredLines.join('\n') + (stderrBuffer && hasNewline ? '\n' + stderrBuffer : stderrBuffer);
    if (toWrite) {
      return originalStderrWrite(toWrite, encoding, fd);
    }
  }
  
  return true; // Suppressed everything
};

console.error = (...args) => {
  const message = args.join(' ');
  // Filter out cache-related and Autofill errors
  if (
    message.includes('Unable to move the cache') ||
    message.includes('Unable to create cache') ||
    message.includes('Gpu Cache Creation failed') ||
    message.includes("'Autofill.enable' wasn't found") ||
    message.includes("'Autofill.setAddresses' wasn't found") ||
    message.includes('Request Autofill.enable failed') ||
    message.includes('Request Autofill.setAddresses failed')
  ) {
    return; // Suppress these harmless errors
  }
  originalConsoleError.apply(console, args);
};

// Load environment variables from electron-app directory
// This ensures .env file is loaded before any modules that need it
require('dotenv').config({ path: path.join(__dirname, '../../.env') });

// Import our modules
const WindowTracker = require('./windows/windowTracker');
const ProcessMonitor = require('./processes/processMonitor');
const ScreenshotCapture = require('./capture/screenshotCapture');
const OCRService = require('./ocr/ocrService');
const workosAuth = require('./auth/workosAuth');

let mainWindow;
let toolbarWindow;
let authWindow = null;

// Initialize trackers
const windowTracker = new WindowTracker();
const processMonitor = new ProcessMonitor();
const screenshotCapture = new ScreenshotCapture();
const ocrService = new OCRService();

function createMainWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      preload: path.join(__dirname, '../preload/preload.js'),
      nodeIntegration: false,
      contextIsolation: true,
      // Disable features that cause errors
      enableBlinkFeatures: '',
      // Suppress DevTools protocol errors
      devTools: isDev,
      // Disable Autofill
      autoplayPolicy: 'no-user-gesture-required',
    },
  });

  // Intercept console messages from DevTools to suppress Autofill errors
  if (isDev) {
    // Intercept console messages from the renderer process (including DevTools)
    mainWindow.webContents.on('console-message', (event, level, message, line, sourceId) => {
      // Suppress Autofill-related console errors
      if (
        message.includes('Autofill.enable') ||
        message.includes('Autofill.setAddresses') ||
        message.includes("'Autofill.enable' wasn't found") ||
        message.includes("'Autofill.setAddresses' wasn't found") ||
        message.includes('Request Autofill')
      ) {
        event.preventDefault(); // Suppress this message
      }
    });

    // Also intercept DevTools WebContents console messages
    mainWindow.webContents.on('devtools-opened', () => {
      const devToolsWebContents = mainWindow.webContents.devToolsWebContents;
      if (devToolsWebContents) {
        // Intercept console messages from DevTools itself
        devToolsWebContents.on('console-message', (event, level, message) => {
          if (
            message.includes('Autofill.enable') ||
            message.includes('Autofill.setAddresses') ||
            message.includes("'Autofill.enable' wasn't found") ||
            message.includes("'Autofill.setAddresses' wasn't found") ||
            message.includes('Request Autofill')
          ) {
            event.preventDefault(); // Suppress this message
          }
        });
      }
    });
  }

  if (isDev) {
    mainWindow.loadURL('http://localhost:5173');
    mainWindow.webContents.openDevTools();
  } else {
    mainWindow.loadFile(path.join(__dirname, '../renderer/index.html'));
  }
}

function createToolbarWindow() {
  toolbarWindow = new BrowserWindow({
    width: 400,
    height: 60,
    frame: false,
    alwaysOnTop: true,
    transparent: true,
    webPreferences: {
      preload: path.join(__dirname, '../preload/preload.js'),
      nodeIntegration: false,
      contextIsolation: true,
      // Disable features that cause errors
      enableBlinkFeatures: '',
    },
  });

  // Position at bottom of screen
  const { screen } = require('electron');
  const primaryDisplay = screen.getPrimaryDisplay();
  const { width, height } = primaryDisplay.workAreaSize;
  
  toolbarWindow.setPosition(0, height - 60);
  toolbarWindow.setResizable(false);

  if (isDev) {
    toolbarWindow.loadURL('http://localhost:5173/toolbar.html');
  } else {
    toolbarWindow.loadFile(path.join(__dirname, '../renderer/toolbar.html'));
  }
}

app.whenReady().then(() => {
  // Configure session to suppress Autofill protocol errors
  const defaultSession = session.defaultSession;
  
  // Set permission handler to deny autofill permissions
  defaultSession.setPermissionRequestHandler((webContents, permission, callback) => {
    if (permission === 'autofill' || permission.includes('autofill')) {
      callback(false); // Deny autofill permissions
    } else {
      callback(true);
    }
  });
  
  createMainWindow();
  createToolbarWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createMainWindow();
      createToolbarWindow();
    }
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

// IPC Handlers

// Window tracking
ipcMain.handle('get-windows', async () => {
  return windowTracker.getAllWindows();
});

ipcMain.handle('get-window-info', async (event, hwnd) => {
  return windowTracker.getWindowInfo(hwnd);
});

ipcMain.handle('start-tracking', async () => {
  windowTracker.startTracking((windowInfo) => {
    if (mainWindow && !mainWindow.isDestroyed()) {
      mainWindow.webContents.send('window-focus-change', windowInfo);
    }
  });
  
  processMonitor.startMonitoring(
    (process) => {
      if (mainWindow && !mainWindow.isDestroyed()) {
        mainWindow.webContents.send('process-launch', process);
      }
    },
    (process) => {
      if (mainWindow && !mainWindow.isDestroyed()) {
        mainWindow.webContents.send('process-termination', process);
      }
    }
  );
});

ipcMain.handle('stop-tracking', async () => {
  windowTracker.stopTracking();
  processMonitor.stopMonitoring();
});

// Process monitoring
ipcMain.handle('get-processes', async () => {
  return processMonitor.getAllProcesses();
});

// Screenshot capture
ipcMain.handle('capture-screen', async (event, options) => {
  return screenshotCapture.captureScreen(options);
});

ipcMain.handle('capture-window', async (event, hwnd) => {
  const windowInfo = windowTracker.getWindowInfo(hwnd);
  if (windowInfo && windowInfo.rect) {
    return screenshotCapture.captureWindow(hwnd, windowInfo.rect);
  }
  throw new Error('Window not found or no rect available');
});

// OCR
ipcMain.handle('extract-text', async (event, imagePath, options) => {
  return ocrService.extractText(imagePath, options);
});

ipcMain.handle('extract-text-region', async (event, imagePath, region) => {
  return ocrService.extractTextFromRegion(imagePath, region);
});

ipcMain.handle('extract-terminal-command', async (event, imagePath, region) => {
  return ocrService.extractTerminalCommand(imagePath, region);
});

// Settings (placeholder)
ipcMain.handle('get-settings', async () => {
  return {};
});

ipcMain.handle('save-settings', async (event, settings) => {
  // TODO: Implement settings persistence
  return true;
});

// WorkOS Authentication Handlers
ipcMain.handle('workos-get-auth-url', async () => {
  try {
    return workosAuth.getAuthorizationUrl();
  } catch (error) {
    console.error('Failed to get auth URL:', error);
    throw error;
  }
});

ipcMain.handle('workos-start-auth', async () => {
  try {
    const authUrl = workosAuth.getAuthorizationUrl();
    
    // Create a new window for OAuth flow
    authWindow = new BrowserWindow({
      width: 500,
      height: 700,
      show: false,
      webPreferences: {
        nodeIntegration: false,
        contextIsolation: true,
      },
    });

    // Show window when ready
    authWindow.once('ready-to-show', () => {
      authWindow.show();
    });

    // Handle OAuth callback - check URL on navigation
    const handleCallback = async (url) => {
      try {
        const urlObj = new URL(url);
        const code = urlObj.searchParams.get('code');
        const error = urlObj.searchParams.get('error');
        
        if (error) {
          throw new Error(error);
        }
        
        if (code && (urlObj.pathname.includes('/auth/callback') || urlObj.searchParams.has('code'))) {
          const authResult = await workosAuth.exchangeCodeForToken(code);
          
          // Send auth result to main window
          if (mainWindow && !mainWindow.isDestroyed()) {
            mainWindow.webContents.send('workos-auth-success', authResult);
          }
          
          // Close auth window
          if (authWindow) {
            authWindow.close();
            authWindow = null;
          }
          return true;
        }
      } catch (error) {
        console.error('Auth error:', error);
        if (mainWindow && !mainWindow.isDestroyed()) {
          mainWindow.webContents.send('workos-auth-error', error.message || 'Authentication failed');
        }
        if (authWindow) {
          authWindow.close();
          authWindow = null;
        }
        return true;
      }
      return false;
    };

    // Handle redirects
    authWindow.webContents.on('will-redirect', async (event, navigationUrl) => {
      if (await handleCallback(navigationUrl)) {
        event.preventDefault();
      }
    });

    // Handle navigation
    authWindow.webContents.on('did-navigate', async (event, url) => {
      await handleCallback(url);
    });

    // Handle window closed
    authWindow.on('closed', () => {
      authWindow = null;
    });

    // Load auth URL
    authWindow.loadURL(authUrl);
    
    return { success: true };
  } catch (error) {
    console.error('Failed to start auth:', error);
    throw error;
  }
});

ipcMain.handle('workos-start-sso', async (event, organizationId) => {
  try {
    const authUrl = workosAuth.getSSOAuthorizationUrl(organizationId);
    
    // Create a new window for SSO flow
    authWindow = new BrowserWindow({
      width: 500,
      height: 700,
      show: false,
      webPreferences: {
        nodeIntegration: false,
        contextIsolation: true,
      },
    });

    authWindow.once('ready-to-show', () => {
      authWindow.show();
    });

    // Handle SSO callback
    const handleSSOCallback = async (url) => {
      try {
        const urlObj = new URL(url);
        const code = urlObj.searchParams.get('code');
        const error = urlObj.searchParams.get('error');
        
        if (error) {
          throw new Error(error);
        }
        
        if (code && (urlObj.pathname.includes('/auth/callback') || urlObj.searchParams.has('code'))) {
          const authResult = await workosAuth.exchangeCodeForToken(code);
          
          if (mainWindow && !mainWindow.isDestroyed()) {
            mainWindow.webContents.send('workos-auth-success', authResult);
          }
          
          if (authWindow) {
            authWindow.close();
            authWindow = null;
          }
          return true;
        }
      } catch (error) {
        console.error('SSO auth error:', error);
        if (mainWindow && !mainWindow.isDestroyed()) {
          mainWindow.webContents.send('workos-auth-error', error.message || 'SSO authentication failed');
        }
        if (authWindow) {
          authWindow.close();
          authWindow = null;
        }
        return true;
      }
      return false;
    };

    authWindow.webContents.on('will-redirect', async (event, navigationUrl) => {
      if (await handleSSOCallback(navigationUrl)) {
        event.preventDefault();
      }
    });

    authWindow.webContents.on('did-navigate', async (event, url) => {
      await handleSSOCallback(url);
    });

    authWindow.on('closed', () => {
      authWindow = null;
    });

    authWindow.loadURL(authUrl);
    
    return { success: true };
  } catch (error) {
    console.error('Failed to start SSO auth:', error);
    throw error;
  }
});

ipcMain.handle('workos-get-user', async () => {
  return workosAuth.getCurrentUser();
});

ipcMain.handle('workos-get-access-token', async () => {
  return workosAuth.getAccessToken();
});

ipcMain.handle('workos-is-authenticated', async () => {
  return workosAuth.isAuthenticated();
});

ipcMain.handle('workos-logout', async () => {
  workosAuth.logout();
  return { success: true };
});

// Cleanup on app quit
app.on('before-quit', async () => {
  await ocrService.terminate();
  if (authWindow) {
    authWindow.close();
  }
});

