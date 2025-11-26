import React, { createContext, useContext, useState } from 'react'

// Demo auth context for bypassing WorkOS in demo mode
const DemoAuthContext = createContext(null)

export function DemoAuthProvider({ children }) {
  const [isAuthenticated, setIsAuthenticated] = useState(true) // Always authenticated in demo mode
  const [user] = useState({
    id: 'demo-user-123',
    email: 'demo@example.com',
    firstName: 'Demo',
    lastName: 'User'
  })

  const signIn = async () => {
    setIsAuthenticated(true)
    return Promise.resolve()
  }

  const signOut = async () => {
    setIsAuthenticated(false)
    return Promise.resolve()
  }

  return (
    <DemoAuthContext.Provider value={{
      user,
      isAuthenticated,
      isLoading: false,
      signIn,
      signOut
    }}>
      {children}
    </DemoAuthContext.Provider>
  )
}

export function useDemoAuth() {
  const context = useContext(DemoAuthContext)
  if (!context) {
    throw new Error('useDemoAuth must be used within DemoAuthProvider')
  }
  return context
}

// Mock Convex auth hook for demo mode
export function useDemoConvexAuth() {
  return {
    isAuthenticated: true,
    isLoading: false,
    fetchAuthenticatedConvexJwt: async () => ({ getValue: () => 'demo-token' })
  }
}


