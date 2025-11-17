import React from 'react'
import ReactDOM from 'react-dom/client'
import { ConvexProvider, ConvexReactClient } from 'convex/react'
import App from './App'
import './index.css'

const convexUrl = import.meta.env.VITE_CONVEX_URL
if (!convexUrl) {
  console.error('Missing VITE_CONVEX_URL environment variable')
  console.error('Please set VITE_CONVEX_URL in .env.local file')
  // Don't throw - let it fail gracefully so user can see the error
}

const convex = new ConvexReactClient(convexUrl || '')

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <ConvexProvider client={convex}>
      <App />
    </ConvexProvider>
  </React.StrictMode>,
)

