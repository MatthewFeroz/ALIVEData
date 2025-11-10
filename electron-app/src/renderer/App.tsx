import React, { useState, useEffect } from 'react';
import { useAuth } from '@workos-inc/authkit-react';
import WindowSelector from './components/WindowSelector';
import RecordingLog from './components/RecordingLog';
import Auth from './components/Auth';
import Callback from './components/Callback';
import { convexService } from './services/convex';

function App() {
  const { user, isLoading, signIn, signOut } = useAuth();
  const [windows, setWindows] = useState<any[]>([]);
  const [isTracking, setIsTracking] = useState(false);
  const [showWindowSelector, setShowWindowSelector] = useState(false);
  const [selectedWindows, setSelectedWindows] = useState<number[]>([]);
  const [selectedProcesses, setSelectedProcesses] = useState<string[]>([]);
  const [sessionId, setSessionId] = useState<string | null>(null);

  // Check if we're on the callback route (AuthKit redirects here)
  const isCallbackRoute = window.location.pathname === '/callback' || window.location.search.includes('code=');

  useEffect(() => {
    // Load windows on mount
    loadWindows();
  }, []);

  const loadWindows = async () => {
    try {
      const windowList = await window.electronAPI.getWindows();
      setWindows(windowList || []);
    } catch (error) {
      console.error('Failed to load windows:', error);
    }
  };

  const handleWindowSelect = (windowHwnds: number[], processes: string[]) => {
    setSelectedWindows(windowHwnds);
    setSelectedProcesses(processes);
    setShowWindowSelector(false);
  };

  const handleLogin = async (loggedInUser: any) => {
    // User is already set via AuthKit's useAuth hook
    // Initialize Convex after login
    // TODO: Get Convex URL from environment or user settings
    // await convexService.initialize(process.env.CONVEX_URL || '');
  };

  const handleLogout = async () => {
    // AuthKit handles logout via signOut
    setIsTracking(false);
    setSessionId(null);
  };

  // Determine current user (needed for tracking functions)
  const skipAuth = import.meta.env.VITE_SKIP_AUTH === 'true';
  const mockUser = skipAuth ? { id: 'dev-user', email: 'dev@example.com' } : null;
  const currentUser = user || mockUser;

  const startTracking = async () => {
    if (selectedWindows.length === 0 && selectedProcesses.length === 0) {
      setShowWindowSelector(true);
      return;
    }

    try {
      // Create session in Convex
      if (currentUser) {
        const newSessionId = await convexService.createSession(currentUser.id);
        setSessionId(newSessionId);
      }

      await window.electronAPI.startTracking();
      setIsTracking(true);
    } catch (error) {
      console.error('Failed to start tracking:', error);
    }
  };

  const stopTracking = async () => {
    try {
      await window.electronAPI.stopTracking();
      
      // End session in Convex
      if (sessionId) {
        await convexService.endSession(sessionId);
        setSessionId(null);
      }
      
      setIsTracking(false);
    } catch (error) {
      console.error('Failed to stop tracking:', error);
    }
  };

  // Show loading state while checking authentication
  if (isLoading) {
    return (
      <div
        style={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          minHeight: '100vh',
          backgroundColor: '#1a1a1a',
          color: '#fff',
        }}
      >
        <div>Loading...</div>
      </div>
    );
  }

  // Show callback component if on callback route
  if (isCallbackRoute) {
    return <Callback />;
  }

  // Show auth if not logged in
  // TEMPORARY: For testing without WorkOS, set SKIP_AUTH=true in .env
  if (!user && !skipAuth) {
    return <Auth onLogin={handleLogin} />;
  }

  if (showWindowSelector) {
    return (
      <WindowSelector
        onSelect={handleWindowSelect}
        onCancel={() => setShowWindowSelector(false)}
      />
    );
  }

  return (
    <div style={{ padding: '20px', fontFamily: 'system-ui', minHeight: '100vh', backgroundColor: '#1a1a1a', color: '#fff' }}>
      {skipAuth && (
        <div style={{ padding: '10px', marginBottom: '20px', backgroundColor: '#ff9800', color: '#000', borderRadius: '4px' }}>
          ⚠️ DEV MODE: Authentication bypassed for testing
        </div>
      )}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h1 style={{ margin: 0 }}>ALIVE Data</h1>
        <div style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
          <span style={{ color: '#888', fontSize: '14px' }}>{currentUser?.email || 'Not logged in'}</span>
          {currentUser && (
            <button
              onClick={async () => {
                await signOut();
                handleLogout();
              }}
              style={{
                padding: '8px 16px',
                fontSize: '14px',
                backgroundColor: '#666',
                color: '#fff',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer',
              }}
            >
              Logout
            </button>
          )}
        </div>
      </div>
      
      <div style={{ marginBottom: '20px' }}>
        <button 
          onClick={isTracking ? stopTracking : startTracking}
          style={{
            padding: '12px 24px',
            fontSize: '16px',
            backgroundColor: isTracking ? '#ff4444' : '#4CAF50',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
            fontWeight: 'bold',
          }}
        >
          {isTracking ? '⏹ Stop Recording' : '▶ Start Recording'}
        </button>
        <button 
          onClick={() => setShowWindowSelector(true)}
          style={{
            padding: '12px 24px',
            fontSize: '16px',
            marginLeft: '10px',
            backgroundColor: '#2196F3',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
          }}
        >
          Select Windows
        </button>
        <button 
          onClick={loadWindows}
          style={{
            padding: '12px 24px',
            fontSize: '16px',
            marginLeft: '10px',
            backgroundColor: '#666',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
          }}
        >
          Refresh Windows
        </button>
      </div>

      {selectedWindows.length > 0 || selectedProcesses.length > 0 ? (
        <div style={{ marginBottom: '20px', padding: '10px', backgroundColor: '#2a2a2a', borderRadius: '4px' }}>
          <strong>Tracking:</strong> {selectedWindows.length} windows, {selectedProcesses.length} processes
        </div>
      ) : null}
      
      <div>
        <h2>Available Windows ({windows.length})</h2>
        <div style={{ maxHeight: '400px', overflowY: 'auto' }}>
          {windows.length === 0 ? (
            <div style={{ padding: '20px', backgroundColor: '#2a2a2a', borderRadius: '4px', textAlign: 'center' }}>
              <p style={{ color: '#888', marginBottom: '10px' }}>
                Window tracking is currently disabled (native modules not available).
              </p>
              <p style={{ color: '#666', fontSize: '14px' }}>
                You can still use the app for other features like screenshots and OCR.
              </p>
            </div>
          ) : (
            windows.map((win, index) => (
              <div
                key={index}
                style={{
                  padding: '12px',
                  margin: '8px 0',
                  backgroundColor: '#2a2a2a',
                  borderRadius: '4px',
                  border: selectedWindows.includes(win.hwnd) ? '2px solid #4CAF50' : '1px solid #333',
                }}
              >
                <strong style={{ color: '#4CAF50' }}>{win.processName || 'Unknown'}</strong>
                <div style={{ color: '#ccc', marginTop: '4px', fontSize: '14px' }}>
                  {win.title || 'Untitled'}
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {isTracking && <RecordingLog isRecording={isTracking} />}
    </div>
  );
}

export default App;

