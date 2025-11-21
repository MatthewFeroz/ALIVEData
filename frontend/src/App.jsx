import React from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { useAuth, useConvexAuth } from './utils/authHooks'
import Layout from './components/Layout'
import Auth from './components/Auth'
import Landing from './pages/Landing'
import SessionsList from './pages/SessionsList'
import SessionDetail from './pages/SessionDetail'
import Settings from './pages/Settings'
import Callback from './pages/Callback'
import Login from './pages/Login'
import LoadingSpinner from './components/LoadingSpinner'
import DemoBanner from './components/DemoBanner'

function ProtectedRoute({ children }) {
  const { isAuthenticated, isLoading } = useConvexAuth()
  
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-alive-dark">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  if (!isAuthenticated) {
    return <Auth />
  }

  return children
}

function App() {
  const { isAuthenticated, isLoading } = useConvexAuth()
  const { user } = useAuth()

  // Debug logging
  React.useEffect(() => {
    console.log('App - Auth state:', { 
      authKitUser: user ? { id: user.id, email: user.email } : null,
      isLoading, 
      isAuthenticated,
      pathname: window.location.pathname
    })
  }, [user, isLoading, isAuthenticated])

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-alive-dark">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  return (
    <Router>
      <DemoBanner />
      <Routes>
        <Route 
          path="/" 
          element={
            isAuthenticated ? <Landing /> : <Auth />
          } 
        />
        <Route 
          path="/callback" 
          element={<Callback />}
        />
        <Route 
          path="/login" 
          element={<Login />}
        />
        <Route 
          path="/sessions" 
          element={
            <ProtectedRoute>
              <Layout><SessionsList /></Layout>
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/sessions/:sessionId" 
          element={
            <ProtectedRoute>
              <Layout><SessionDetail /></Layout>
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/settings" 
          element={
            <ProtectedRoute>
              <Layout><Settings /></Layout>
            </ProtectedRoute>
          } 
        />
      </Routes>
    </Router>
  )
}

export default App
