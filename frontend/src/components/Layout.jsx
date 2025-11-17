import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import { useAuth } from '@workos-inc/authkit-react'

export default function Layout({ children }) {
  const location = useLocation()
  const { user, signOut } = useAuth()
  
  // Check both AuthKit and Convex auth
  const convexAuthUserId = typeof window !== 'undefined' ? sessionStorage.getItem('convex_auth_userId') : null
  const convexAuthAuthenticated = typeof window !== 'undefined' ? sessionStorage.getItem('convex_auth_authenticated') === 'true' : false
  const isAuthenticated = !!user || (convexAuthAuthenticated && convexAuthUserId)

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
                      // Clear Convex auth from sessionStorage
                      sessionStorage.removeItem('convex_auth_userId')
                      sessionStorage.removeItem('convex_auth_authenticated')
                      
                      // Sign out from AuthKit if available
                      if (signOut) {
                        await signOut()
                      }
                      
                      // Redirect to home (will show Auth component)
                      window.location.href = '/'
                    } catch (error) {
                      console.error('Sign out error:', error)
                      // Still clear sessionStorage and redirect
                      sessionStorage.removeItem('convex_auth_userId')
                      sessionStorage.removeItem('convex_auth_authenticated')
                      window.location.href = '/'
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

