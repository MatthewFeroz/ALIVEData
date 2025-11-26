import React, { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import LoadingSpinner from '../components/LoadingSpinner'
import { useServerAuth } from '../utils/serverAuth'

export default function Callback() {
  const { exchangeCodeForTokens, user, isLoading: authLoading } = useServerAuth()
  const navigate = useNavigate()
  const [status, setStatus] = useState('processing')
  const [error, setError] = useState(null)
  const exchangeAttempted = useRef(false)
  
  // Get code from URL
  const urlParams = new URLSearchParams(window.location.search)
  const code = urlParams.get('code')
  const errorParam = urlParams.get('error')
  const errorDescription = urlParams.get('error_description')

  useEffect(() => {
    // Log initial state
    console.log('Callback page loaded:', {
      hasCode: !!code,
      code: code ? code.substring(0, 10) + '...' : null,
      error: errorParam,
      user: user ? user.email : null,
    })

    // If already authenticated, redirect home
    if (user) {
      console.log('Already authenticated, redirecting home')
      navigate('/', { replace: true })
      return
    }

    // If there's an OAuth error, show it
    if (errorParam) {
      setStatus('error')
      setError(`OAuth error: ${errorParam} - ${errorDescription || 'Unknown error'}`)
      return
    }

    // If no code, show error
    if (!code) {
      setStatus('error')
      setError('No authorization code received. Please try signing in again.')
      return
    }

    // Exchange the code for tokens (only once)
    if (!exchangeAttempted.current) {
      exchangeAttempted.current = true
      
      const redirectUri = import.meta.env.VITE_WORKOS_REDIRECT_URI || `${window.location.origin}/callback`
      
      console.log('Exchanging code for tokens via Convex backend...')
      setStatus('exchanging')
      
      exchangeCodeForTokens(code, redirectUri)
        .then((result) => {
          if (result.success) {
            console.log('Auth successful!')
            setStatus('success')
            // Small delay to show success message
            setTimeout(() => {
              navigate('/', { replace: true })
            }, 500)
          } else {
            console.error('Token exchange failed:', result.error)
            setStatus('error')
            setError(result.error || 'Token exchange failed')
          }
        })
        .catch((e) => {
          console.error('Token exchange error:', e)
          setStatus('error')
          setError(e.message || 'Unknown error during authentication')
        })
    }
  }, [code, errorParam, errorDescription, user, navigate, exchangeCodeForTokens])

  // Show loading state
  if (status === 'processing' || status === 'exchanging' || authLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-alive-dark">
        <div className="text-center">
          <LoadingSpinner size="lg" />
          <p className="text-white mt-4">
            {status === 'exchanging' ? 'Completing sign in...' : 'Processing...'}
          </p>
        </div>
      </div>
    )
  }

  // Show success (brief, before redirect)
  if (status === 'success') {
    return (
      <div className="min-h-screen flex items-center justify-center bg-alive-dark">
        <div className="text-center">
          <div className="text-green-500 text-4xl mb-4">✓</div>
          <p className="text-white">Sign in successful! Redirecting...</p>
        </div>
      </div>
    )
  }

  // Show error
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-alive-dark text-white">
      <div className="text-red-500 text-4xl mb-4">✗</div>
      <p className="text-xl mb-4">Sign in failed</p>
      <p className="text-gray-400 mb-6 text-center max-w-md">
        {error || 'An unexpected error occurred during authentication.'}
      </p>
      <div className="flex gap-4">
        <button 
          onClick={() => {
            window.location.href = '/'
          }} 
          className="bg-alive-active hover:bg-red-600 px-6 py-2 rounded transition-colors"
        >
          Try Again
        </button>
        <button 
          onClick={() => navigate('/')} 
          className="bg-gray-600 hover:bg-gray-500 px-6 py-2 rounded transition-colors"
        >
          Go Home
        </button>
      </div>
      
      <details className="mt-8 text-xs text-gray-500 bg-black p-4 rounded max-w-lg" open>
        <summary className="cursor-pointer mb-2">Debug Info</summary>
        <pre className="whitespace-pre-wrap">
{`Status: ${status}
Error: ${error || 'none'}
Had Code: ${!!code}
OAuth Error: ${errorParam || 'none'}
Error Description: ${errorDescription || 'none'}`}
        </pre>
      </details>
    </div>
  )
}
