import React, { useState, useEffect } from 'react';
import { useAuth } from '@workos-inc/authkit-react';

interface AuthProps {
  onLogin: (user: any) => void;
}

const Auth: React.FC<AuthProps> = ({ onLogin }) => {
  const { user, isLoading, signIn, signOut } = useAuth();
  const [error, setError] = useState('');
  const [ssoOrganizationId, setSsoOrganizationId] = useState('');
  const [showSSO, setShowSSO] = useState(false);

  // When user is authenticated, notify parent component
  useEffect(() => {
    if (user && !isLoading) {
      // Map AuthKit user to our AuthUser interface
      const authUser = {
        id: user.id,
        email: user.email,
        firstName: user.firstName || undefined,
        lastName: user.lastName || undefined,
      };
      onLogin(authUser);
    }
  }, [user, isLoading, onLogin]);

  const handleLogin = async () => {
    setError('');
    try {
      // Check if clientId is configured
      const clientId = import.meta.env.VITE_WORKOS_CLIENT_ID || '';
      if (!clientId) {
        setError('WorkOS Client ID not configured. Please create a .env file in electron-app/ with WORKOS_CLIENT_ID=your_client_id');
        return;
      }
      await signIn();
      // AuthKit will handle the redirect and callback
    } catch (err: any) {
      setError(err.message || 'Login failed');
    }
  };

  const handleSSOLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!ssoOrganizationId.trim()) {
      setError('Please enter an organization ID');
      return;
    }

    setError('');
    try {
      // For SSO, we'll need to pass organizationId to signIn
      // AuthKit supports this via the signIn method options
      await signIn({ organizationId: ssoOrganizationId });
    } catch (err: any) {
      setError(err.message || 'SSO login failed');
    }
  };

  return (
    <div
      style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        minHeight: '100vh',
        backgroundColor: '#1a1a1a',
      }}
    >
      <div
        style={{
          width: '400px',
          padding: '40px',
          backgroundColor: '#2a2a2a',
          borderRadius: '8px',
          boxShadow: '0 4px 6px rgba(0, 0, 0, 0.3)',
        }}
      >
        <h2 style={{ marginBottom: '30px', textAlign: 'center', color: '#fff' }}>
          ALIVE Data Login
        </h2>

        {error && (
          <div
            style={{
              padding: '10px',
              marginBottom: '20px',
              backgroundColor: '#ff4444',
              color: '#fff',
              borderRadius: '4px',
              fontSize: '14px',
            }}
          >
            {error}
          </div>
        )}

        {!showSSO ? (
          <>
            <div style={{ marginBottom: '30px', textAlign: 'center' }}>
              <p style={{ color: '#ccc', fontSize: '14px', marginBottom: '20px' }}>
                Sign in with WorkOS to continue
              </p>
            </div>

            <button
              onClick={handleLogin}
              disabled={isLoading}
              style={{
                width: '100%',
                padding: '12px',
                fontSize: '16px',
                backgroundColor: isLoading ? '#666' : '#4CAF50',
                color: '#fff',
                border: 'none',
                borderRadius: '4px',
                cursor: isLoading ? 'not-allowed' : 'pointer',
                fontWeight: 'bold',
                marginBottom: '15px',
              }}
            >
              {isLoading ? 'Opening login...' : 'Sign in with WorkOS'}
            </button>

            <div style={{ textAlign: 'center', marginTop: '20px' }}>
              <button
                onClick={() => setShowSSO(true)}
                style={{
                  padding: '10px 20px',
                  backgroundColor: 'transparent',
                  color: '#4A9EFF',
                  border: '1px solid #4A9EFF',
                  borderRadius: '4px',
                  cursor: 'pointer',
                  fontSize: '14px',
                }}
              >
                Sign in with SSO
              </button>
            </div>
          </>
        ) : (
          <>
            <div style={{ marginBottom: '20px' }}>
              <label
                style={{
                  display: 'block',
                  marginBottom: '8px',
                  color: '#ccc',
                  fontSize: '14px',
                }}
              >
                Organization ID
              </label>
              <input
                type="text"
                value={ssoOrganizationId}
                onChange={(e) => setSsoOrganizationId(e.target.value)}
                placeholder="Enter your organization ID"
                style={{
                  width: '100%',
                  padding: '12px',
                  fontSize: '14px',
                  borderRadius: '4px',
                  border: '1px solid #333',
                  backgroundColor: '#1a1a1a',
                  color: '#fff',
                }}
              />
            </div>

            <button
              onClick={handleSSOLogin}
              disabled={isLoading}
              style={{
                width: '100%',
                padding: '12px',
                fontSize: '16px',
                backgroundColor: isLoading ? '#666' : '#4A9EFF',
                color: '#fff',
                border: 'none',
                borderRadius: '4px',
                cursor: isLoading ? 'not-allowed' : 'pointer',
                fontWeight: 'bold',
                marginBottom: '15px',
              }}
            >
              {isLoading ? 'Opening SSO login...' : 'Sign in with SSO'}
            </button>

            <div style={{ textAlign: 'center', marginTop: '20px' }}>
              <button
                onClick={() => {
                  setShowSSO(false);
                  setSsoOrganizationId('');
                  setError('');
                }}
                style={{
                  padding: '10px 20px',
                  backgroundColor: 'transparent',
                  color: '#ccc',
                  border: '1px solid #333',
                  borderRadius: '4px',
                  cursor: 'pointer',
                  fontSize: '14px',
                }}
              >
                Back to regular login
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default Auth;

