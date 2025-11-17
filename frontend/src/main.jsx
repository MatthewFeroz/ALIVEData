import React from 'react'
import ReactDOM from 'react-dom/client'
import { ConvexReactClient } from 'convex/react'
import { AuthKitProvider, useAuth } from '@workos-inc/authkit-react'
import { ConvexProviderWithAuthKit } from '@convex-dev/workos'
import App from './App'
import './index.css'

const convexUrl = import.meta.env.VITE_CONVEX_URL
const workosClientId = import.meta.env.VITE_WORKOS_CLIENT_ID

if (!convexUrl) {
  console.error('Missing VITE_CONVEX_URL environment variable')
  console.error('Please set VITE_CONVEX_URL in .env.local file')
  // Don't throw - let it fail gracefully so user can see the error
}

if (!workosClientId) {
  console.error('Missing VITE_WORKOS_CLIENT_ID environment variable')
  console.error('Please set VITE_WORKOS_CLIENT_ID in .env.local file')
}

// Only create Convex client if URL is available
const convex = convexUrl ? new ConvexReactClient(convexUrl) : null

function AppWithAuth() {
  // If no Convex URL, show error
  if (!convex) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-alive-dark p-4">
        <div className="max-w-md w-full bg-yellow-900 bg-opacity-50 border border-yellow-700 rounded-lg p-8">
          <h2 className="text-2xl font-bold text-white mb-4">Configuration Required</h2>
          <p className="text-yellow-200 mb-4">
            Please set <code className="bg-black bg-opacity-50 px-2 py-1 rounded">VITE_CONVEX_URL</code> in your <code className="bg-black bg-opacity-50 px-2 py-1 rounded">.env.local</code> file
          </p>
          <p className="text-yellow-300 text-sm">
            Location: <code className="bg-black bg-opacity-50 px-2 py-1 rounded">frontend/.env.local</code>
          </p>
        </div>
      </div>
    )
  }

  // Pass the useAuth hook function itself, not the result of calling it
  return (
    <ConvexProviderWithAuthKit client={convex} useAuth={useAuth}>
      <App />
    </ConvexProviderWithAuthKit>
  )
}

// Error boundary to catch and display React errors
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props)
    this.state = { hasError: false, error: null }
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error }
  }

  componentDidCatch(error, errorInfo) {
    console.error('Error caught by boundary:', error, errorInfo)
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen flex items-center justify-center bg-alive-dark p-4">
          <div className="max-w-2xl w-full bg-red-900 bg-opacity-50 border border-red-700 rounded-lg p-8">
            <h2 className="text-2xl font-bold text-white mb-4">Application Error</h2>
            <p className="text-red-200 mb-4">{this.state.error?.message || String(this.state.error)}</p>
            <details className="text-red-300 text-sm">
              <summary className="cursor-pointer mb-2">Stack trace</summary>
              <pre className="bg-black bg-opacity-50 p-4 rounded overflow-auto text-xs">
                {this.state.error?.stack}
              </pre>
            </details>
            <button
              onClick={() => window.location.reload()}
              className="mt-4 px-4 py-2 bg-alive-active hover:bg-red-600 text-white rounded"
            >
              Reload Page
            </button>
          </div>
        </div>
      )
    }

    return this.props.children
  }
}

// Get redirect URI from environment or use default
const getRedirectUri = () => {
  if (typeof window !== 'undefined') {
    return import.meta.env.VITE_WORKOS_REDIRECT_URI || `${window.location.origin}/callback`
  }
  return import.meta.env.VITE_WORKOS_REDIRECT_URI || 'http://localhost:5000/callback'
}

function Root() {
  const redirectUri = getRedirectUri()
  
  if (!workosClientId) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-alive-dark p-4">
        <div className="max-w-md w-full bg-yellow-900 bg-opacity-50 border border-yellow-700 rounded-lg p-8">
          <h2 className="text-2xl font-bold text-white mb-4">Configuration Required</h2>
          <p className="text-yellow-200 mb-4">
            Please set <code className="bg-black bg-opacity-50 px-2 py-1 rounded">VITE_WORKOS_CLIENT_ID</code> in your <code className="bg-black bg-opacity-50 px-2 py-1 rounded">.env.local</code> file
          </p>
          <p className="text-yellow-300 text-sm mb-2">
            Get your Client ID from WorkOS Dashboard → Configuration
          </p>
          <p className="text-yellow-300 text-xs mt-4">
            Current URL: {typeof window !== 'undefined' ? window.location.origin : 'N/A'}
            <br />
            Expected redirect URI: {redirectUri}
          </p>
        </div>
      </div>
    )
  }

  return (
    <AuthKitProvider 
      clientId={workosClientId}
      redirectUri={redirectUri}
      // Configure to work with Convex backend
      // The ConvexProviderWithAuthKit will handle backend authentication
    >
      <AppWithAuth />
    </AuthKitProvider>
  )
}

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <ErrorBoundary>
      <Root />
    </ErrorBoundary>
  </React.StrictMode>,
)

