import { useEffect } from 'react'
import { useAuth } from '../utils/authHooks'
import { useNavigate } from 'react-router-dom'
import LoadingSpinner from '../components/LoadingSpinner'

export default function Login() {
  const { user, isLoading, signIn } = useAuth()
  const navigate = useNavigate()

  useEffect(() => {
    if (!isLoading) {
      if (user) {
        // Already logged in, redirect home
        navigate('/', { replace: true })
      } else {
        // Not logged in, initiate sign in
        console.log('Initiating sign in...')
        signIn()
      }
    }
  }, [user, isLoading, navigate, signIn])

  return (
    <div className="min-h-screen flex items-center justify-center bg-alive-dark">
      <div className="text-center">
        <LoadingSpinner size="lg" />
        <p className="text-white mt-4">Redirecting to sign in...</p>
      </div>
    </div>
  )
}
