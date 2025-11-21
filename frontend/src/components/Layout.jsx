import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import { useAuth, useConvexAuth } from '../utils/authHooks'

export default function Layout({ children }) {
  const location = useLocation()
  const { signOut } = useAuth()
  const { isAuthenticated } = useConvexAuth()

  return (
    <div className="min-h-screen bg-alive-dark text-white">
      <nav className="bg-alive-button border-b border-gray-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center justify-between w-full">
              <div className="flex">
                <Link
                  to="/"
                  className="flex items-center px-4 text-xl font-bold text-white hover:text-alive-active transition-colors"
                >
                  ALIVE Data
                </Link>
                <div className="flex space-x-4 ml-8">
                  <Link
                    to="/"
                    className="flex items-center px-3 py-2 rounded-md text-sm font-medium text-gray-300 hover:bg-alive-hover hover:text-white transition-colors"
                  >
                    Home
                  </Link>
                  <Link
                    to="/sessions"
                    className={`flex items-center px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                      location.pathname.startsWith('/sessions')
                        ? 'bg-alive-hover text-white'
                        : 'text-gray-300 hover:bg-alive-hover hover:text-white'
                    }`}
                  >
                    Sessions
                  </Link>
                  <Link
                    to="/settings"
                    className={`flex items-center px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                      location.pathname === '/settings'
                        ? 'bg-alive-hover text-white'
                        : 'text-gray-300 hover:bg-alive-hover hover:text-white'
                    }`}
                  >
                    Settings
                  </Link>
                </div>
              </div>
              {isAuthenticated && (
                <button
                  onClick={async () => {
                    try {
                      await signOut()
                      // Redirect is usually handled by state change
                    } catch (error) {
                      console.error('Sign out error:', error)
                    }
                  }}
                  className="px-4 py-2 text-sm font-medium text-gray-300 hover:text-white hover:bg-alive-hover rounded-md transition-colors"
                >
                  Sign Out
                </button>
              )}
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {children}
      </main>
    </div>
  )
}
