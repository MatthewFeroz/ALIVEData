import React from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useMutation } from 'convex/react'
import { useAuth } from '../utils/authHooks'
import { api } from '../../convex/_generated/api'

export default function Landing() {
  const navigate = useNavigate()
  const { user, isLoading: authLoading, signOut } = useAuth()

  // Check both AuthKit and Convex auth (sessionStorage fallback)
  const convexAuthUserId = typeof window !== 'undefined' ? sessionStorage.getItem('convex_auth_userId') : null
  const convexAuthAuthenticated = typeof window !== 'undefined' ? sessionStorage.getItem('convex_auth_authenticated') === 'true' : false
  const isAuthenticated = !!user || (convexAuthAuthenticated && convexAuthUserId)

  const createSessionMutation = useMutation(api.sessions.createSession)
  const [creating, setCreating] = React.useState(false)

  const handleGetStarted = async () => {
    try {
      setCreating(true)
      const sessionId = await createSessionMutation({})
      if (sessionId) {
        navigate(`/sessions/${sessionId}`)
      }
    } catch (err) {
      console.error('Error creating session:', err)
      // Still navigate to sessions list if creation fails
      navigate('/sessions')
    } finally {
      setCreating(false)
    }
  }

  return (
    <div className="min-h-screen">
      {/* Navigation */}
      <nav className="bg-alive-button/50 backdrop-blur-sm border-b border-gray-800 fixed w-full top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <Link
                to="/"
                className="text-xl font-bold text-white hover:text-alive-active transition-colors"
              >
                ALIVE Data
              </Link>
            </div>
            <div className="flex items-center space-x-4">
              {isAuthenticated ? (
                <>
                  <Link
                    to="/sessions"
                    className="text-gray-300 hover:text-white transition-colors"
                  >
                    Sessions
                  </Link>
                  <Link
                    to="/settings"
                    className="text-gray-300 hover:text-white transition-colors"
                  >
                    Settings
                  </Link>
                  <button
                    onClick={async () => {
                      try {
                        // Clear Convex auth from sessionStorage
                        if (typeof window !== 'undefined') {
                          sessionStorage.removeItem('convex_auth_userId')
                          sessionStorage.removeItem('convex_auth_authenticated')
                        }
                        // Sign out from AuthKit if available
                        if (signOut) {
                          await signOut()
                        }
                        // Redirect to home (will show Auth component)
                        window.location.href = '/'
                      } catch (error) {
                        console.error('Sign out error:', error)
                        // Still clear sessionStorage and redirect
                        if (typeof window !== 'undefined') {
                          sessionStorage.removeItem('convex_auth_userId')
                          sessionStorage.removeItem('convex_auth_authenticated')
                        }
                        window.location.href = '/'
                      }
                    }}
                    className="px-4 py-2 text-sm font-medium text-gray-300 hover:text-white hover:bg-alive-hover rounded-md transition-colors"
                  >
                    Sign Out
                  </button>
                </>
              ) : (
                <button
                  onClick={() => navigate('/login')}
                  className="px-4 py-2 bg-alive-active hover:bg-red-600 text-white font-semibold rounded-md transition-colors shadow-lg shadow-red-500/50"
                >
                  Sign In
                </button>
              )}
            </div>
          </div>
        </div>
      </nav>
      {/* Hero Section */}
      <section className="relative overflow-hidden bg-gradient-to-br from-alive-dark via-gray-900 to-alive-dark">
        <div className="absolute inset-0 bg-grid-pattern opacity-5"></div>
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 pb-16 sm:pt-24 sm:pb-20">
          <div className="text-center">
            <h1 className="text-5xl sm:text-6xl lg:text-7xl font-bold text-white mb-6">
              <span className="block">ALIVE</span>
              <span className="block text-alive-active">Data</span>
            </h1>
            <p className="mt-6 text-xl sm:text-2xl text-gray-300 max-w-3xl mx-auto">
              Automatically generate documentation from screenshots using OCR and AI.
              Turn visual workflows into clear, step-by-step guides.
            </p>
            <div className="mt-10 flex flex-col sm:flex-row gap-4 justify-center">
              <button
                onClick={handleGetStarted}
                disabled={creating}
                className="px-8 py-4 bg-alive-active hover:bg-red-600 text-white font-semibold rounded-lg text-lg transition-all transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-red-500/50"
              >
                {creating ? 'Creating Session...' : 'Get Started'}
              </button>
              <Link
                to="/sessions"
                className="px-8 py-4 bg-alive-button hover:bg-alive-hover text-white font-semibold rounded-lg text-lg transition-all border border-gray-700"
              >
                View Sessions
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-alive-dark">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-4xl font-bold text-center text-white mb-12">
            Powerful Features
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="bg-alive-button rounded-lg p-6 border border-gray-700 hover:border-alive-active transition-colors">
              <div className="w-12 h-12 bg-alive-active rounded-lg flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-white mb-2">Screenshot Upload</h3>
              <p className="text-gray-400">
                Upload screenshots of your workflow. Drag and drop or click to select images.
              </p>
            </div>

            <div className="bg-alive-button rounded-lg p-6 border border-gray-700 hover:border-alive-active transition-colors">
              <div className="w-12 h-12 bg-alive-active rounded-lg flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-white mb-2">OCR Processing</h3>
              <p className="text-gray-400">
                Extract text from images using advanced OCR technology. Process multiple screenshots in seconds.
              </p>
            </div>

            <div className="bg-alive-button rounded-lg p-6 border border-gray-700 hover:border-alive-active transition-colors">
              <div className="w-12 h-12 bg-alive-active rounded-lg flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-white mb-2">AI Documentation</h3>
              <p className="text-gray-400">
                Generate clear, step-by-step documentation using AI. Transform raw text into professional guides.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="py-20 bg-gray-900">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-4xl font-bold text-center text-white mb-12">
            How It Works
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div className="text-center">
              <div className="w-16 h-16 bg-alive-active rounded-full flex items-center justify-center mx-auto mb-4 text-2xl font-bold text-white">
                1
              </div>
              <h3 className="text-lg font-semibold text-white mb-2">Create Session</h3>
              <p className="text-gray-400 text-sm">
                Start a new documentation session
              </p>
            </div>
            <div className="text-center">
              <div className="w-16 h-16 bg-alive-active rounded-full flex items-center justify-center mx-auto mb-4 text-2xl font-bold text-white">
                2
              </div>
              <h3 className="text-lg font-semibold text-white mb-2">Upload Screenshots</h3>
              <p className="text-gray-400 text-sm">
                Add screenshots of your workflow
              </p>
            </div>
            <div className="text-center">
              <div className="w-16 h-16 bg-alive-active rounded-full flex items-center justify-center mx-auto mb-4 text-2xl font-bold text-white">
                3
              </div>
              <h3 className="text-lg font-semibold text-white mb-2">Process OCR</h3>
              <p className="text-gray-400 text-sm">
                Extract text from images automatically
              </p>
            </div>
            <div className="text-center">
              <div className="w-16 h-16 bg-alive-active rounded-full flex items-center justify-center mx-auto mb-4 text-2xl font-bold text-white">
                4
              </div>
              <h3 className="text-lg font-semibold text-white mb-2">Generate Docs</h3>
              <p className="text-gray-400 text-sm">
                AI creates professional documentation
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-r from-alive-active to-red-600">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-4xl font-bold text-white mb-4">
            Ready to Get Started?
          </h2>
          <p className="text-xl text-red-100 mb-8">
            Create your first session and start generating documentation in minutes.
          </p>
          <button
            onClick={handleGetStarted}
            disabled={creating}
            className="px-8 py-4 bg-white text-alive-active font-semibold rounded-lg text-lg transition-all transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg"
          >
            {creating ? 'Creating Session...' : 'Start Creating Documentation'}
          </button>
        </div>
      </section>
    </div>
  )
}

