import React from 'react'
import { useConvex } from 'convex/react'

export default function ConvexStatus() {
  const convex = useConvex()
  
  return (
    <div className="text-xs text-gray-500 mb-2">
      Convex URL: {import.meta.env.VITE_CONVEX_URL ? '✓ Set' : '✗ Missing'}
    </div>
  )
}

