import React from 'react'

export default function DemoBanner() {
  const isDemoMode = import.meta.env.VITE_DEMO_MODE === 'true'
  
  if (!isDemoMode) {
    return null
  }

  return (
    <div className="bg-yellow-600 text-white px-4 py-2 text-center text-sm font-semibold">
      🎭 DEMO MODE: Authentication is disabled. All features are accessible without login.
    </div>
  )
}


