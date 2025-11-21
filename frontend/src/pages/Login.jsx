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
            navigate('/', { replace: true })
        } else {
            // Auto-redirect to WorkOS login
            signIn().catch(err => console.error("Auto-login failed:", err))
        }
    }
  }, [user, isLoading, navigate, signIn])

  const handleLogin = async () => {
    try {
      await signIn()
    } catch (err) {
      console.error("Login failed:", err)
    }
  }

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-alive-dark">
        <LoadingSpinner />
      </div>
    )
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-alive-dark">
       <div className="text-center">
          <p className="text-white mb-4">Redirecting to sign in...</p>
          <button 
            onClick={handleLogin}
            className="bg-alive-active text-white px-6 py-2 rounded"
          >
            Sign In
          </button>
       </div>
    </div>
  )
}
