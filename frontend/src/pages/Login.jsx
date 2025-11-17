// Login page that redirects to WorkOS AuthKit
// Uses Convex HTTP endpoint to avoid CORS - AuthKit can't call WorkOS API from browser
import { useEffect } from 'react'
import { useAuth } from '@workos-inc/authkit-react'
import { useNavigate } from 'react-router-dom'

const workosClientId = import.meta.env.VITE_WORKOS_CLIENT_ID

export default function Login() {
  const { user, isLoading } = useAuth()
  const navigate = useNavigate()

  useEffect(() => {
    console.log('Login page - Auth state:', { user: !!user, isLoading, workosClientId: !!workosClientId })
    
    // If already authenticated, redirect to home
    if (!isLoading && user) {
      console.log('Already authenticated, redirecting to home')
      navigate('/', { replace: true })
      return
    }

    // Redirect to WorkOS - use frontend callback URL so login originates from app
    // This satisfies WorkOS's CSRF protection requirement
    if (!isLoading && !user && workosClientId) {
      // Use frontend callback URL - WorkOS requires login to originate from the app
      const redirectUri = `${window.location.origin}/callback`
      const authorizationUrl = `https://api.workos.com/user_management/authorize?client_id=${workosClientId}&redirect_uri=${encodeURIComponent(redirectUri)}&response_type=code&provider=authkit`
      
      console.log('Redirecting to WorkOS (login initiated from app):', authorizationUrl)
      
      // Redirect immediately - this satisfies WorkOS's Login Initiation endpoint requirement
      window.location.href = authorizationUrl
    } else if (!isLoading && !user && !workosClientId) {
      console.error('Missing VITE_WORKOS_CLIENT_ID - cannot redirect to WorkOS')
    }
  }, [user, isLoading, navigate])

  return (
    <div className="min-h-screen flex items-center justify-center bg-alive-dark">
      <div className="text-center">
        <div className="text-white mb-4">Redirecting to sign in...</div>
      </div>
    </div>
  )
}

