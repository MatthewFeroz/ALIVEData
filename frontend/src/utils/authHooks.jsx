// Wrapper hooks that switch between demo and real auth based on VITE_DEMO_MODE
import { useAuth as useWorkOSAuth } from '@workos-inc/authkit-react'
import { useConvexAuth as useRealConvexAuth } from 'convex/react'
import { useDemoAuth, useDemoConvexAuth } from './demoAuth'

const isDemoMode = import.meta.env.VITE_DEMO_MODE === 'true'

// Wrapper for WorkOS auth hook
export function useAuth() {
  if (isDemoMode) {
    return useDemoAuth()
  }
  return useWorkOSAuth()
}

// Wrapper for Convex auth hook
export function useConvexAuth() {
  if (isDemoMode) {
    return useDemoConvexAuth()
  }
  return useRealConvexAuth()
}

