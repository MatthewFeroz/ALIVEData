import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { sessionsAPI } from '../services/api'
import LoadingSpinner from '../components/LoadingSpinner'

export default function SessionsList() {
  const [sessions, setSessions] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [creating, setCreating] = useState(false)

  useEffect(() => {
    loadSessions()
  }, [])

  const loadSessions = async () => {
    try {
      setLoading(true)
      const data = await sessionsAPI.list()
      setSessions(data.sessions || [])
      setError(null)
    } catch (err) {
      setError('Failed to load sessions: ' + err.message)
    } finally {
      setLoading(false)
    }
  }

  const createSession = async () => {
    try {
      setCreating(true)
      const session = await sessionsAPI.create()
      // Redirect to new session
      window.location.href = `/sessions/${session.session_id}`
    } catch (err) {
      setError('Failed to create session: ' + err.message)
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

      {sessions.length === 0 ? (
        <div className="text-center py-12 text-gray-400">
          <p className="text-xl mb-4">No sessions yet</p>
          <p>Create a new session to get started</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {sessions.map((session) => (
            <Link
              key={session.session_id}
              to={`/sessions/${session.session_id}`}
              className="bg-alive-button hover:bg-alive-hover border border-gray-700 rounded-lg p-6 transition-colors"
            >
              <h3 className="text-lg font-semibold mb-2">
                {session.session_id}
              </h3>
              <p className="text-sm text-gray-400 mb-1">
                Started: {formatDate(session.start_time)}
              </p>
              {session.pc_name && (
                <p className="text-sm text-gray-400">PC: {session.pc_name}</p>
              )}
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}

