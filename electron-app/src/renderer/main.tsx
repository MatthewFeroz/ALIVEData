import React from 'react';
import ReactDOM from 'react-dom/client';
import { AuthKitProvider } from '@workos-inc/authkit-react';
import App from './App';
import './index.css';

// Get Client ID from environment or use a default
// In Electron, we'll need to pass this from the main process or use an env var
const clientId = import.meta.env.VITE_WORKOS_CLIENT_ID || '';

// Check if clientId is missing and show helpful error
if (!clientId && window.location.hostname === 'localhost') {
  console.warn('⚠️ WORKOS_CLIENT_ID not configured. Please create a .env file with your WorkOS Client ID.');
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <AuthKitProvider
      clientId={clientId}
      redirectUri={window.location.origin + '/callback'}
      devMode={true} // Use devMode for Electron (stores refresh token in localStorage)
    >
      <App />
    </AuthKitProvider>
  </React.StrictMode>
);

