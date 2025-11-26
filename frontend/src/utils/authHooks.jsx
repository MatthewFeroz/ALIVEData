// Wrapper hooks that switch between demo and real auth based on VITE_DEMO_MODE
import { useServerAuth, useServerConvexAuth } from './serverAuth'
import { useDemoAuth, useDemoConvexAuth } from './demoAuth'

const isDemoMode = import.meta.env.VITE_DEMO_MODE === 'true'

// Wrapper for auth hook
export function useAuth() {
  if (isDemoMode) {
    return useDemoAuth()
  }
  return useServerAuth()
}

// Wrapper for Convex auth hook
export function useConvexAuth() {
  if (isDemoMode) {
    return useDemoConvexAuth()
  }
  return useServerConvexAuth()
}
