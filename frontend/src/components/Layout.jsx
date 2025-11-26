import React from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { useMutation } from 'convex/react'
import { useAuth, useConvexAuth } from '../utils/authHooks'
import { api } from '../../convex/_generated/api'

export default function Layout({ children }) {
  const location = useLocation()
  const navigate = useNavigate()
  const { signOut } = useAuth()
  const { isAuthenticated } = useConvexAuth()
  
  const createSessionMutation = useMutation(api.sessions.createSession)
  const [creating, setCreating] = React.useState(false)

  const handleCreateSession = async () => {
    try {
      setCreating(true)
      const sessionId = await createSessionMutation({})
      if (sessionId) {
        navigate(`/sessions/${sessionId}`)
      }
    } catch (err) {
      console.error('Error creating session:', err)
      navigate('/sessions')
    } finally {
      setCreating(false)
    }
  }

  return (
    <div className="min-h-screen bg-alive-dark text-white">
      {/* Navigation */}
      <nav className="fixed w-full top-0 z-50 glass-darker">
        <div className="max-w-7xl mx-auto px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Left: Logo + Create Session Button */}
            <div className="flex items-center gap-6">
              <Link
                to="/"
                className="text-xl font-display font-bold text-white hover:text-alive-accent transition-colors"
              >
                ALIVE Data
              </Link>
              
              <button
                onClick={handleCreateSession}
                disabled={creating}
                className="btn-glow px-4 py-2 bg-alive-active hover:bg-alive-accent text-white text-sm font-semibold rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                </svg>
                {creating ? 'Creating...' : 'New Session'}
              </button>
            </div>

            {/* Center: Navigation Links */}
            <div className="hidden md:flex items-center gap-1">
              <Link
                to="/"
                className={`px-4 py-2 text-sm font-medium rounded-lg transition-colors ${
                  location.pathname === '/'
                    ? 'text-white bg-white/10'
                    : 'text-white/70 hover:text-white hover:bg-white/5'
                }`}
              >
                Home
              </Link>
              <Link
                to="/sessions"
                className={`px-4 py-2 text-sm font-medium rounded-lg transition-colors ${
                  location.pathname.startsWith('/sessions')
                    ? 'text-white bg-white/10'
                    : 'text-white/70 hover:text-white hover:bg-white/5'
                }`}
              >
                Sessions
              </Link>
              <Link
                to="/settings"
                className={`px-4 py-2 text-sm font-medium rounded-lg transition-colors ${
                  location.pathname === '/settings'
                    ? 'text-white bg-white/10'
                    : 'text-white/70 hover:text-white hover:bg-white/5'
                }`}
              >
                Settings
              </Link>
            </div>

            {/* Right: Auth Actions */}
            <div className="flex items-center gap-4">
              {isAuthenticated && (
                <button
                  onClick={async () => {
                    try {
                      if (typeof window !== 'undefined') {
                        sessionStorage.removeItem('convex_auth_userId')
                        sessionStorage.removeItem('convex_auth_authenticated')
                      }
                      if (signOut) {
                        await signOut()
                      }
                      window.location.href = '/'
                    } catch (error) {
                      console.error('Sign out error:', error)
                      window.location.href = '/'
                    }
                  }}
                  className="px-4 py-2 text-sm font-medium text-white/70 hover:text-white hover:bg-white/5 rounded-lg transition-colors"
                >
                  Sign Out
                </button>
              )}
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-6 lg:px-8 py-8 pt-24">
        {children}
      </main>
    </div>
  )
}
