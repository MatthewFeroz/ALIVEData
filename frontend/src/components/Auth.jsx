import React from 'react'
import { useAuth } from '../utils/authHooks'
import { useNavigate } from 'react-router-dom'

export default function Auth() {
  const { user, isLoading } = useAuth()
  const navigate = useNavigate()
  const isAuthenticated = !!user

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-alive-dark">
        <div className="text-white">Loading...</div>
      </div>
    )
  }

  if (isAuthenticated) {
    return null // User is authenticated, don't show auth UI
  }

  const handleSignIn = () => {
    // Redirect to login page which uses Convex backend to avoid CORS
    navigate('/login')
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-alive-dark px-4">
      <div className="max-w-md w-full bg-alive-button border border-gray-700 rounded-lg p-8">
        <h2 className="text-2xl font-bold text-white mb-6 text-center">
          Sign In
        </h2>
        
        <p className="text-gray-400 mb-6 text-center">
          Sign in with WorkOS AuthKit to access ALIVE Data
        </p>

        <button
          onClick={handleSignIn}
          className="w-full bg-alive-active hover:bg-red-600 text-white font-semibold py-3 px-4 rounded-lg transition-colors shadow-lg shadow-red-500/50"
        >
          Sign In with WorkOS
        </button>

        <div className="mt-6 pt-6 border-t border-gray-700">
          <p className="text-xs text-gray-500 text-center">
            WorkOS AuthKit provides secure authentication with support for SSO, 
            passwordless login, and more.
          </p>
        </div>
      </div>
    </div>
  )
}

