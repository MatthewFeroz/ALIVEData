import React from 'react'
import ReactDOM from 'react-dom/client'
import { ConvexReactClient, ConvexProvider } from 'convex/react'
import { ConvexProviderWithAuth } from 'convex/react'
import { ServerAuthProvider, useServerAuth } from './utils/serverAuth'
import { DemoAuthProvider } from './utils/demoAuth'
import App from './App'
import './index.css'

const convexUrl = import.meta.env.VITE_CONVEX_URL
const workosClientId = import.meta.env.VITE_WORKOS_CLIENT_ID
const isDemoMode = import.meta.env.VITE_DEMO_MODE === 'true'

// Debug: log environment on load
console.log('Environment:', {
  convexUrl: convexUrl ? 'set' : 'missing',
  workosClientId: workosClientId ? 'set' : 'missing',
  isDemoMode,
  origin: typeof window !== 'undefined' ? window.location.origin : 'N/A',
})

if (!convexUrl) {
  console.error('Missing VITE_CONVEX_URL environment variable')
}

if (!workosClientId && !isDemoMode) {
  console.error('Missing VITE_WORKOS_CLIENT_ID environment variable')
}

// Only create Convex client if URL is available
const convex = convexUrl ? new ConvexReactClient(convexUrl) : null

// Custom auth hook for Convex that uses our server auth
function useConvexServerAuth() {
  const { isLoading, isAuthenticated, accessToken } = useServerAuth()
  
  const fetchAccessToken = React.useCallback(async ({ forceRefreshToken }) => {
    return accessToken || null
  }, [accessToken])

  return {
    isLoading,
    isAuthenticated,
    fetchAccessToken,
  }
}

function ConfigurationError({ message }) {
  return (
    <div className="min-h-screen flex items-center justify-center bg-alive-dark p-4">
      <div className="max-w-md w-full bg-yellow-900 bg-opacity-50 border border-yellow-700 rounded-lg p-8">
        <h2 className="text-2xl font-bold text-white mb-4">Configuration Required</h2>
        <p className="text-yellow-200 mb-4">{message}</p>
        <p className="text-yellow-300 text-sm">
          Location: <code className="bg-black bg-opacity-50 px-2 py-1 rounded">frontend/.env.local</code>
        </p>
      </div>
    </div>
  )
}

function AppWithAuth() {
  // Demo mode: bypass auth entirely
  if (isDemoMode) {
    if (!convex) {
      return <ConfigurationError message="Demo mode still requires VITE_CONVEX_URL" />
    }
    
    return (
      <DemoAuthProvider>
        <ConvexProvider client={convex}>
          <App />
        </ConvexProvider>
      </DemoAuthProvider>
    )
  }

  // Production mode: use server-side auth
  if (!convex) {
    return <ConfigurationError message="Please set VITE_CONVEX_URL in your .env.local file" />
  }

  return (
    <ConvexProviderWithAuth client={convex} useAuth={useConvexServerAuth}>
      <App />
    </ConvexProviderWithAuth>
  )
}

// Error boundary
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

function Root() {
  if (isDemoMode) {
    return <AppWithAuth />
  }
  
  if (!workosClientId) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-alive-dark p-4">
        <div className="max-w-md w-full bg-yellow-900 bg-opacity-50 border border-yellow-700 rounded-lg p-8">
          <h2 className="text-2xl font-bold text-white mb-4">Configuration Required</h2>
          <p className="text-yellow-200 mb-4">
            Please set <code className="bg-black bg-opacity-50 px-2 py-1 rounded">VITE_WORKOS_CLIENT_ID</code>
          </p>
          <p className="text-yellow-300 text-xs mt-4 pt-4 border-t border-yellow-800">
            💡 Set <code className="bg-black bg-opacity-50 px-2 py-1 rounded">VITE_DEMO_MODE=true</code> to bypass auth
          </p>
        </div>
      </div>
    )
  }

  return (
    <ServerAuthProvider convexUrl={convexUrl}>
      <AppWithAuth />
    </ServerAuthProvider>
  )
}

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <ErrorBoundary>
      <Root />
    </ErrorBoundary>
  </React.StrictMode>,
)
