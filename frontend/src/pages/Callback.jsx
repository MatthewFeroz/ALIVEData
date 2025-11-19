import React from 'react'
import { useAuth } from '@workos-inc/authkit-react'
import { useNavigate } from 'react-router-dom'
import LoadingSpinner from '../components/LoadingSpinner'

export default function Callback() {
  const { isLoading, user } = useAuth()
  const navigate = useNavigate()

  React.useEffect(() => {
    if (!isLoading && user) {
      navigate('/')
    } else if (!isLoading && !user) {
      // If loading finished but no user, something went wrong or we are just visiting /callback without code
      // But AuthKit should handle the code exchange before isLoading becomes false?
      // We'll give it a moment or redirect to login
      // navigate('/login')
    }
  }, [isLoading, user, navigate])

  return (
    <div className="min-h-screen flex items-center justify-center bg-alive-dark">
      <div className="text-center">
        <LoadingSpinner size="lg" />
        <p className="text-white mt-4">Completing sign in...</p>
      </div>
    </div>
  )
}
