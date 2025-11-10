import React, { useEffect } from 'react';
import { useAuth } from '@workos-inc/authkit-react';

/**
 * Callback component to handle AuthKit redirect
 * This component is rendered when WorkOS redirects back after authentication
 */
const Callback: React.FC = () => {
  const { user, isLoading } = useAuth();

  useEffect(() => {
    // AuthKitProvider will automatically handle the callback
    // Once authenticated, the user will be available
    if (user && !isLoading) {
      // Redirect will be handled by the parent App component
      // which checks for user authentication
    }
  }, [user, isLoading]);

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
      <div style={{ textAlign: 'center' }}>
        <h2>Completing sign in...</h2>
        {isLoading && <p>Please wait while we sign you in.</p>}
        {user && <p>Sign in successful! Redirecting...</p>}
      </div>
    </div>
  );
};

export default Callback;

