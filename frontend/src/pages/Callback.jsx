// Callback page for WorkOS OAuth redirect
// Receives OAuth code from WorkOS, sends it to Convex HTTP endpoint for server-side exchange
// This avoids CORS while satisfying WorkOS's requirement that login originates from the app
import React, { useEffect, useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import LoadingSpinner from '../components/LoadingSpinner'

export default function Callback() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const code = searchParams.get('code') // OAuth code from WorkOS (initial callback)
  const success = searchParams.get('success') // From Convex after server-side exchange
  const userId = searchParams.get('userId') // From Convex after server-side exchange
  const error = searchParams.get('error')
  const [hasProcessed, setHasProcessed] = useState(false)
  
  // CRITICAL: Check for code and redirect IMMEDIATELY before AuthKit processes it
  // This runs synchronously during render, before useEffect
  if (typeof window !== 'undefined' && code && !success && !hasProcessed) {
    const convexUrl = import.meta.env.VITE_CONVEX_URL
    if (convexUrl) {
      const convexSite = convexUrl.replace('.convex.cloud', '.convex.site')
      const convexCallbackUrl = `${convexSite}/workos/callback?code=${encodeURIComponent(code)}`
      // Redirect immediately - this prevents AuthKit from processing the code
      window.location.href = convexCallbackUrl
      // Return early to prevent component from rendering
      return null
    }
  }

  useEffect(() => {
    console.log('Callback - Received:', { 
      code: !!code,
      success, 
      userId,
      error
    })
    
    // Case 1: Received success from Convex after server-side code exchange
    if (success === 'true' && userId && !hasProcessed) {
      setHasProcessed(true)
      
      // Store auth state in sessionStorage
      if (typeof window !== 'undefined') {
        sessionStorage.setItem('convex_auth_userId', userId)
        sessionStorage.setItem('convex_auth_authenticated', 'true')
        console.log('Stored auth in sessionStorage:', { userId })
      }
      
      // Redirect to home - App.jsx will check sessionStorage
      console.log('Redirecting to home - Convex authenticated successfully')
      window.location.href = '/'
    } 
    // Case 2: Error from WorkOS or Convex
    else if (error) {
      console.error('Authentication error:', error)
      navigate('/login', { replace: true })
    } 
    // Case 3: No success, no error, no code - invalid state
    else if (!code && !success && !error && !hasProcessed) {
      // Wait a moment in case redirect is happening, otherwise go to login
      setTimeout(() => {
        if (!hasProcessed) {
          console.warn('No code, success, or error received, redirecting to login')
          navigate('/login', { replace: true })
        }
      }, 1000)
    }
  }, [code, success, userId, error, navigate, hasProcessed])

  // Show loading while AuthKit processes the callback
  return (
    <div className="min-h-screen flex items-center justify-center bg-alive-dark">
      <div className="text-center">
        <LoadingSpinner size="lg" />
        <p className="text-white mt-4">Completing sign in...</p>
        <p className="text-gray-400 text-sm mt-2">Please wait...</p>
      </div>
    </div>
  )
}

