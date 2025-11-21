import React from 'react'
import { useAuth } from '@workos-inc/authkit-react'
import { useNavigate } from 'react-router-dom'
import LoadingSpinner from '../components/LoadingSpinner'

export default function Callback() {
  const { isLoading, user, signIn } = useAuth()
  const navigate = useNavigate()

  React.useEffect(() => {
    console.log("Callback State:", { isLoading, user, hasCode: window.location.search.includes("code") });
    if (!isLoading && user) {
      navigate('/')
    }
  }, [isLoading, user, navigate])

  if (!isLoading && !user) {
     return (
        <div className="min-h-screen flex flex-col items-center justify-center bg-alive-dark text-white">
           <p className="text-xl mb-4">Sign in incomplete.</p>
           <div className="flex gap-4">
              <button onClick={() => signIn()} className="bg-alive-active px-4 py-2 rounded">Try Again</button>
              <button onClick={() => navigate('/')} className="bg-gray-600 px-4 py-2 rounded">Go Home</button>
           </div>
           <pre className="mt-8 text-xs text-gray-500 bg-black p-4 rounded">
             Debug: User is null, Loading is false. Check console for details.
           </pre>
        </div>
     )
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-alive-dark">
      <div className="text-center">
        <LoadingSpinner size="lg" />
        <p className="text-white mt-4">Completing sign in...</p>
      </div>
    </div>
  )
}