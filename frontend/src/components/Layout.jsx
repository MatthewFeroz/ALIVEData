import React from 'react'
import { Link, useLocation } from 'react-router-dom'

export default function Layout({ children }) {
  const location = useLocation()

  return (
    <div className="min-h-screen bg-alive-dark text-white">
      <nav className="bg-alive-button border-b border-gray-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex">
              <Link
                to="/"
                className="flex items-center px-4 text-xl font-bold text-white hover:text-alive-active transition-colors"
              >
                ALIVE Data
              </Link>
              <div className="flex space-x-4 ml-8">
                <Link
                  to="/"
                  className={`flex items-center px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                    location.pathname === '/'
                      ? 'bg-alive-hover text-white'
                      : 'text-gray-300 hover:bg-alive-hover hover:text-white'
                  }`}
                >
                  Sessions
                </Link>
                <Link
                  to="/settings"
                  className={`flex items-center px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                    location.pathname === '/settings'
                      ? 'bg-alive-hover text-white'
                      : 'text-gray-300 hover:bg-alive-hover hover:text-white'
                  }`}
                >
                  Settings
                </Link>
              </div>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {children}
      </main>
    </div>
  )
}

