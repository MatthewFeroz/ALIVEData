import React from 'react'
import { useAuth } from '../utils/authHooks'
import { useNavigate, Link } from 'react-router-dom'

export default function Auth() {
  const { user, isLoading } = useAuth()
  const navigate = useNavigate()
  const isAuthenticated = !!user

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-alive-dark">
        <div className="flex flex-col items-center gap-4">
          <div className="w-10 h-10 border-2 border-alive-active border-t-transparent rounded-full animate-spin"></div>
          <span className="text-white/60 font-body">Loading...</span>
        </div>
      </div>
    )
  }

  if (isAuthenticated) {
    return null // User is authenticated, don't show auth UI
  }

  const handleSignIn = () => {
    navigate('/login')
  }

  return (
    <div className="min-h-screen bg-alive-dark relative overflow-hidden">
      {/* Background Effects */}
      <div className="absolute inset-0 bg-hero-gradient"></div>
      <div className="absolute inset-0 bg-dot-pattern opacity-30"></div>
      
      {/* Navigation */}
      <nav className="relative z-10 glass-darker">
        <div className="max-w-7xl mx-auto px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <Link
              to="/"
              className="text-xl font-display font-bold text-white hover:text-alive-accent transition-colors"
            >
              ALIVE Data
            </Link>
            <button
              onClick={handleSignIn}
              className="btn-glow px-5 py-2.5 bg-alive-active hover:bg-alive-accent text-white text-sm font-semibold rounded-lg transition-all shadow-lg shadow-alive-active/20"
            >
              Sign In
            </button>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <div className="relative z-10 flex flex-col items-center justify-center min-h-[calc(100vh-64px)] px-4">
        <div className="text-center mb-12 max-w-2xl">
          <h1 className="font-display text-5xl sm:text-6xl lg:text-7xl font-bold text-white mb-6 animate-fade-in">
            Welcome to
            <br />
            <span className="text-alive-accent">ALIVE Data</span>
          </h1>
          <p className="text-lg sm:text-xl text-white/60 font-body animate-slide-up stagger-2">
            Transform screenshots into professional documentation with AI-powered OCR and intelligent generation.
          </p>
        </div>

        {/* Auth Card */}
        <div className="w-full max-w-md animate-slide-up stagger-3">
          <div className="gradient-border rounded-2xl p-8">
            <h2 className="text-2xl font-display font-bold text-white mb-3 text-center">
              Get Started
            </h2>
            
            <p className="text-white/50 mb-8 text-center font-body">
              Sign in to start creating documentation from screenshots
            </p>

            <button
              onClick={handleSignIn}
              className="btn-glow w-full bg-alive-active hover:bg-alive-accent text-white font-semibold py-4 px-6 rounded-xl transition-all shadow-lg shadow-alive-active/30 flex items-center justify-center gap-3 group"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z" />
              </svg>
              Sign In with WorkOS
              <svg className="w-4 h-4 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
              </svg>
            </button>

            <div className="mt-8 pt-6 border-t border-alive-border">
              <p className="text-xs text-white/40 text-center font-body leading-relaxed">
                Secure authentication powered by WorkOS AuthKit with support for SSO, passwordless login, and enterprise-grade security.
              </p>
            </div>
          </div>
        </div>

        {/* Features Preview */}
        <div className="mt-16 grid grid-cols-3 gap-8 max-w-2xl animate-slide-up stagger-4">
          {[
            { icon: '📸', label: 'Screenshot Upload' },
            { icon: '🔍', label: 'OCR Processing' },
            { icon: '✨', label: 'AI Documentation' },
          ].map((feature) => (
            <div key={feature.label} className="text-center">
              <div className="text-3xl mb-2">{feature.icon}</div>
              <div className="text-sm text-white/50 font-body">{feature.label}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
