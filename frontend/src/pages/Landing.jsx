import React from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useMutation } from 'convex/react'
import { useAuth } from '../utils/authHooks'
import { api } from '../../convex/_generated/api'

// Company logos placeholder component
function CompanyLogo({ name }) {
  return (
    <div className="company-logo flex items-center justify-center h-8 px-6 text-alive-muted font-display font-semibold text-lg tracking-wide">
      {name}
    </div>
  )
}

// Demo window component showing the tool in action
function DemoWindow() {
  const [currentStep, setCurrentStep] = React.useState(0)
  const steps = [
    { title: 'Upload Screenshots', status: 'completed' },
    { title: 'Processing OCR...', status: 'active' },
    { title: 'Generating Documentation', status: 'pending' },
  ]

  React.useEffect(() => {
    const interval = setInterval(() => {
      setCurrentStep((prev) => (prev + 1) % 4)
    }, 2000)
    return () => clearInterval(interval)
  }, [])

  return (
    <div className="demo-window rounded-2xl overflow-hidden w-full max-w-4xl mx-auto animate-float">
      {/* Window Header */}
      <div className="demo-window-header px-4 py-3 flex items-center gap-3">
        <div className="flex gap-2">
          <div className="traffic-light red"></div>
          <div className="traffic-light yellow"></div>
          <div className="traffic-light green"></div>
        </div>
        <div className="flex-1 text-center">
          <span className="text-xs text-alive-muted font-mono">ALIVE Data — Session Active</span>
        </div>
        <div className="w-16"></div>
      </div>
      
      {/* Window Content */}
      <div className="p-6 min-h-[350px]">
        {/* Simulated IDE Layout */}
        <div className="grid grid-cols-12 gap-4 h-full">
          {/* Sidebar */}
          <div className="col-span-3 space-y-3">
            <div className="text-xs font-mono text-alive-muted uppercase tracking-wider mb-4">Files</div>
            {['screenshot_01.png', 'screenshot_02.png', 'screenshot_03.png'].map((file, i) => (
              <div 
                key={file}
                className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm transition-all ${
                  i === currentStep % 3 
                    ? 'bg-alive-active/20 text-alive-accent border border-alive-active/30' 
                    : 'text-alive-muted hover:bg-alive-hover'
                }`}
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
                <span className="font-mono text-xs">{file}</span>
              </div>
            ))}
          </div>
          
          {/* Main Content */}
          <div className="col-span-6 bg-alive-dark/50 rounded-xl p-4 border border-alive-border">
            <div className="text-xs font-mono text-alive-muted mb-4">Processing Pipeline</div>
            <div className="space-y-3">
              {steps.map((step, i) => (
                <div 
                  key={step.title}
                  className={`flex items-center gap-3 p-3 rounded-lg transition-all duration-500 ${
                    i < currentStep ? 'bg-green-500/10 border border-green-500/20' :
                    i === currentStep ? 'bg-alive-active/10 border border-alive-active/30' :
                    'bg-alive-button border border-alive-border'
                  }`}
                >
                  <div className={`w-6 h-6 rounded-full flex items-center justify-center ${
                    i < currentStep ? 'bg-green-500' :
                    i === currentStep ? 'bg-alive-active animate-pulse' :
                    'bg-alive-hover'
                  }`}>
                    {i < currentStep ? (
                      <svg className="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                      </svg>
                    ) : (
                      <span className="text-xs text-white font-mono">{i + 1}</span>
                    )}
                  </div>
                  <span className={`text-sm font-medium ${
                    i <= currentStep ? 'text-white' : 'text-alive-muted'
                  }`}>
                    {step.title}
                  </span>
                  {i === currentStep && (
                    <div className="ml-auto flex gap-1">
                      <div className="w-1.5 h-1.5 bg-alive-active rounded-full animate-pulse"></div>
                      <div className="w-1.5 h-1.5 bg-alive-active rounded-full animate-pulse" style={{animationDelay: '0.2s'}}></div>
                      <div className="w-1.5 h-1.5 bg-alive-active rounded-full animate-pulse" style={{animationDelay: '0.4s'}}></div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
          
          {/* Output Panel */}
          <div className="col-span-3 bg-alive-dark/50 rounded-xl p-4 border border-alive-border">
            <div className="text-xs font-mono text-alive-muted mb-4">Output</div>
            <div className="space-y-2 font-mono text-xs">
              <div className="text-green-400">✓ OCR Complete</div>
              <div className="text-alive-accent">→ Analyzing content...</div>
              <div className="text-alive-muted opacity-50">◦ Generating docs</div>
            </div>
            <div className="mt-4 p-3 bg-alive-button rounded-lg border border-alive-border">
              <div className="text-xs text-alive-muted mb-2">Generated:</div>
              <div className="text-sm text-white/80 leading-relaxed">
                <span className="typing-cursor">Step 1: Click the menu button</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

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
      navigate('/sessions')
    } finally {
      setCreating(false)
    }
  }

  const companies = [
    'Acme Corp',
    'TechFlow',
    'DataSync',
    'CloudBase',
    'NextGen AI',
    'DevOps Pro',
  ]

  return (
    <div className="min-h-screen bg-alive-dark">
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
              
              {isAuthenticated && (
                <button
                  onClick={handleGetStarted}
                  disabled={creating}
                  className="btn-glow px-4 py-2 bg-alive-active hover:bg-alive-accent text-white text-sm font-semibold rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                  </svg>
                  {creating ? 'Creating...' : 'New Session'}
                </button>
              )}
            </div>

            {/* Center: Navigation Links */}
            <div className="hidden md:flex items-center gap-1">
              <Link
                to="/"
                className="px-4 py-2 text-sm font-medium text-white/90 hover:text-white hover:bg-white/5 rounded-lg transition-colors"
              >
                Home
              </Link>
              {isAuthenticated && (
                <>
                  <Link
                    to="/sessions"
                    className="px-4 py-2 text-sm font-medium text-white/70 hover:text-white hover:bg-white/5 rounded-lg transition-colors"
                  >
                    Sessions
                  </Link>
                  <Link
                    to="/settings"
                    className="px-4 py-2 text-sm font-medium text-white/70 hover:text-white hover:bg-white/5 rounded-lg transition-colors"
                  >
                    Settings
                  </Link>
                </>
              )}
              <a
                href="#features"
                className="px-4 py-2 text-sm font-medium text-white/70 hover:text-white hover:bg-white/5 rounded-lg transition-colors"
              >
                Features
              </a>
              <a
                href="#how-it-works"
                className="px-4 py-2 text-sm font-medium text-white/70 hover:text-white hover:bg-white/5 rounded-lg transition-colors"
              >
                How It Works
              </a>
            </div>

            {/* Right: Auth Actions */}
            <div className="flex items-center gap-4">
              {isAuthenticated ? (
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
                      if (typeof window !== 'undefined') {
                        sessionStorage.removeItem('convex_auth_userId')
                        sessionStorage.removeItem('convex_auth_authenticated')
                      }
                      window.location.href = '/'
                    }
                  }}
                  className="px-4 py-2 text-sm font-medium text-white/70 hover:text-white hover:bg-white/5 rounded-lg transition-colors"
                >
                  Sign Out
                </button>
              ) : (
                <button
                  onClick={() => navigate('/login')}
                  className="btn-glow px-5 py-2.5 bg-alive-active hover:bg-alive-accent text-white text-sm font-semibold rounded-lg transition-all shadow-lg shadow-alive-active/20"
                >
                  Sign In
                </button>
              )}
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative min-h-screen flex flex-col justify-center overflow-hidden bg-hero-gradient">
        {/* Background Effects */}
        <div className="absolute inset-0 bg-dot-pattern opacity-30"></div>
        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-transparent to-alive-dark"></div>
        
        <div className="relative max-w-7xl mx-auto px-6 lg:px-8 pt-32 pb-20">
          {/* Hero Text */}
          <div className="text-center mb-16">
            <h1 className="font-display text-5xl sm:text-6xl lg:text-7xl font-bold text-white mb-6 animate-fade-in">
              Built to make you{' '}
              <span className="text-alive-accent">extraordinarily</span>
              <br />
              productive, ALIVE Data is the
              <br />
              best way to document with AI.
            </h1>
            <p className="mt-6 text-lg sm:text-xl text-white/60 max-w-2xl mx-auto font-body animate-slide-up stagger-2">
              Automatically generate documentation from screenshots using OCR and AI.
              Turn visual workflows into clear, step-by-step guides.
            </p>
            
            {/* CTA Buttons */}
            <div className="mt-10 flex flex-col sm:flex-row gap-4 justify-center animate-slide-up stagger-3">
              <button
                onClick={handleGetStarted}
                disabled={creating}
                className="btn-glow px-8 py-4 bg-alive-active hover:bg-alive-accent text-white font-semibold rounded-xl text-lg transition-all transform hover:scale-[1.02] disabled:opacity-50 disabled:cursor-not-allowed shadow-xl shadow-alive-active/30 flex items-center justify-center gap-2"
              >
                {creating ? 'Creating Session...' : 'Get Started Free'}
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
                </svg>
              </button>
              <Link
                to="/sessions"
                className="px-8 py-4 bg-white/5 hover:bg-white/10 text-white font-semibold rounded-xl text-lg transition-all border border-white/10 hover:border-white/20"
              >
                View Sessions
              </Link>
            </div>
          </div>

          {/* Demo Window */}
          <div className="animate-slide-up stagger-4">
            <DemoWindow />
          </div>
        </div>
      </section>

      {/* Trusted By Section */}
      <section className="py-20 bg-alive-surface border-t border-alive-border">
        <div className="max-w-7xl mx-auto px-6 lg:px-8">
          <p className="text-center text-sm text-alive-muted font-medium uppercase tracking-wider mb-10">
            Trusted every day by developers and teams worldwide
          </p>
          <div className="flex flex-wrap items-center justify-center gap-8 md:gap-12 lg:gap-16">
            {companies.map((company) => (
              <CompanyLogo key={company} name={company} />
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-24 bg-alive-dark">
        <div className="max-w-7xl mx-auto px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="font-display text-4xl sm:text-5xl font-bold text-white mb-4">
              Powerful Features
            </h2>
            <p className="text-lg text-white/60 max-w-2xl mx-auto">
              Everything you need to transform screenshots into professional documentation
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {[
              {
                icon: (
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                ),
                title: 'Screenshot Upload',
                description: 'Drag and drop screenshots of your workflow. Support for PNG, JPG, and more.',
              },
              {
                icon: (
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                ),
                title: 'OCR Processing',
                description: 'Advanced text extraction powered by state-of-the-art OCR technology.',
              },
              {
                icon: (
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                ),
                title: 'AI Documentation',
                description: 'Generate clear, step-by-step guides using cutting-edge AI models.',
              },
            ].map((feature, i) => (
              <div
                key={feature.title}
                className="group gradient-border rounded-2xl p-6 hover:scale-[1.02] transition-transform duration-300"
              >
                <div className="w-12 h-12 bg-alive-active/20 rounded-xl flex items-center justify-center mb-4 text-alive-accent group-hover:bg-alive-active/30 transition-colors">
                  {feature.icon}
                </div>
                <h3 className="text-xl font-display font-semibold text-white mb-2">
                  {feature.title}
                </h3>
                <p className="text-white/60 font-body">
                  {feature.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section id="how-it-works" className="py-24 bg-alive-surface border-t border-alive-border">
        <div className="max-w-7xl mx-auto px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="font-display text-4xl sm:text-5xl font-bold text-white mb-4">
              How It Works
            </h2>
            <p className="text-lg text-white/60 max-w-2xl mx-auto">
              From screenshots to documentation in four simple steps
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            {[
              { step: 1, title: 'Create Session', desc: 'Start a new documentation session' },
              { step: 2, title: 'Upload Screenshots', desc: 'Add screenshots of your workflow' },
              { step: 3, title: 'Process OCR', desc: 'Extract text from images automatically' },
              { step: 4, title: 'Generate Docs', desc: 'AI creates professional documentation' },
            ].map((item, i) => (
              <div key={item.step} className="text-center group">
                <div className="relative mb-6">
                  <div className="w-16 h-16 bg-alive-active/20 rounded-2xl flex items-center justify-center mx-auto text-2xl font-display font-bold text-alive-accent group-hover:bg-alive-active/30 group-hover:scale-110 transition-all duration-300">
                    {item.step}
                  </div>
                  {i < 3 && (
                    <div className="hidden md:block absolute top-1/2 left-[calc(50%+40px)] w-[calc(100%-80px)] h-px bg-gradient-to-r from-alive-border to-transparent"></div>
                  )}
                </div>
                <h3 className="text-lg font-display font-semibold text-white mb-2">
                  {item.title}
                </h3>
                <p className="text-sm text-white/50">
                  {item.desc}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24 bg-gradient-to-b from-alive-surface to-alive-dark border-t border-alive-border">
        <div className="max-w-4xl mx-auto px-6 lg:px-8 text-center">
          <h2 className="font-display text-4xl sm:text-5xl font-bold text-white mb-6">
            Ready to transform your
            <br />
            <span className="text-alive-accent">documentation workflow?</span>
          </h2>
          <p className="text-lg text-white/60 mb-10 max-w-xl mx-auto">
            Start creating professional documentation from screenshots in minutes, not hours.
          </p>
          <button
            onClick={handleGetStarted}
            disabled={creating}
            className="btn-glow px-10 py-5 bg-alive-active hover:bg-alive-accent text-white font-semibold rounded-xl text-lg transition-all transform hover:scale-[1.02] disabled:opacity-50 disabled:cursor-not-allowed shadow-2xl shadow-alive-active/40 animate-glow"
          >
            {creating ? 'Creating Session...' : 'Start Creating Documentation'}
          </button>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-8 bg-alive-dark border-t border-alive-border">
        <div className="max-w-7xl mx-auto px-6 lg:px-8">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <div className="text-sm text-alive-muted">
              © 2024 ALIVE Data. All rights reserved.
            </div>
            <div className="flex items-center gap-6">
              <a href="#" className="text-sm text-alive-muted hover:text-white transition-colors">Privacy</a>
              <a href="#" className="text-sm text-alive-muted hover:text-white transition-colors">Terms</a>
              <a href="#" className="text-sm text-alive-muted hover:text-white transition-colors">Contact</a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}
