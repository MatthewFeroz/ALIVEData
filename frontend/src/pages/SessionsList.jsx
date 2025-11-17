import React, { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useQuery, useMutation } from 'convex/react'
import { api } from '../../convex/_generated/api'
import LoadingSpinner from '../components/LoadingSpinner'

export default function SessionsList() {
  const navigate = useNavigate()
  const [error, setError] = useState(null)
  const [creating, setCreating] = useState(false)

  // Use Convex query hook - automatically updates in real-time!
  const sessions = useQuery(api.sessions.listSessions)
  const createSessionMutation = useMutation(api.sessions.createSession)

  const loading = sessions === undefined

  // Debug: Log Convex connection status
  useEffect(() => {
    console.log('Convex URL:', import.meta.env.VITE_CONVEX_URL)
    console.log('Sessions query result:', sessions)
    console.log('Create mutation available:', !!createSessionMutation)
  }, [sessions, createSessionMutation])

  const createSession = async () => {
    try {
      setCreating(true)
      setError(null)
      console.log('Creating session...')
      const sessionId = await createSessionMutation({})
      console.log('Session created:', sessionId)
      // Redirect to new session
      if (sessionId) {
        navigate(`/sessions/${sessionId}`)
      } else {
        setError('Session created but no ID returned')
        setCreating(false)
      }
    } catch (err) {
      console.error('Error creating session:', err)
      setError('Failed to create session: ' + (err.message || String(err)))
      setCreating(false)
    }
  }

  const formatDate = (dateString) => {
    if (!dateString) return 'Unknown'
    try {
      const date = new Date(dateString)
      return date.toLocaleString()
    } catch {
      return dateString
    }
  }

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Sessions</h1>
        <button
          onClick={createSession}
          disabled={creating}
          className="bg-alive-active hover:bg-red-600 text-white font-semibold py-2 px-4 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {creating ? 'Creating...' : '+ New Session'}
        </button>
      </div>

      {error && (
        <div className="bg-red-900 bg-opacity-50 border border-red-700 text-red-200 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      {!sessions || sessions.length === 0 ? (
        <div className="text-center py-12 text-gray-400">
          <p className="text-xl mb-4">No sessions yet</p>
          <p>Create a new session to get started</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {sessions.map((session) => (
            <Link
              key={session._id}
              to={`/sessions/${session.sessionId}`}
              className="bg-alive-button hover:bg-alive-hover border border-gray-700 rounded-lg p-6 transition-colors"
            >
              <h3 className="text-lg font-semibold mb-2">
                {session.sessionId}
              </h3>
              <p className="text-sm text-gray-400 mb-1">
                Started: {formatDate(new Date(session.startTime).toISOString())}
              </p>
              {session.pcName && (
                <p className="text-sm text-gray-400">PC: {session.pcName}</p>
              )}
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}

