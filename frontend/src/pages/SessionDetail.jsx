import React, { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import ReactMarkdown from 'react-markdown'
import { sessionsAPI } from '../services/api'
import FileUpload from '../components/FileUpload'
import LoadingSpinner from '../components/LoadingSpinner'

export default function SessionDetail() {
  const { sessionId } = useParams()
  const [session, setSession] = useState(null)
  const [screenshots, setScreenshots] = useState([])
  const [documentation, setDocumentation] = useState(null)
  const [ocrText, setOcrText] = useState('')
  const [loading, setLoading] = useState(true)
  const [uploading, setUploading] = useState(false)
  const [processingOCR, setProcessingOCR] = useState(false)
  const [generating, setGenerating] = useState(false)
  const [error, setError] = useState(null)
  const [activeTab, setActiveTab] = useState('upload')

  useEffect(() => {
    loadSession()
    loadScreenshots()
  }, [sessionId])

  const loadSession = async () => {
    try {
      setLoading(true)
      const data = await sessionsAPI.get(sessionId)
      setSession(data)
    } catch (err) {
      setError('Failed to load session: ' + err.message)
    } finally {
      setLoading(false)
    }
  }

  const loadScreenshots = async () => {
    try {
      const data = await sessionsAPI.listScreenshots(sessionId)
      setScreenshots(data.screenshots || [])
    } catch (err) {
      console.error('Failed to load screenshots:', err)
    }
  }

  const handleUpload = async (file) => {
    try {
      setUploading(true)
      setError(null)
      await sessionsAPI.uploadScreenshot(sessionId, file, (progress) => {
        console.log('Upload progress:', progress)
      })
      await loadScreenshots()
    } catch (err) {
      setError('Failed to upload screenshot: ' + err.message)
    } finally {
      setUploading(false)
    }
  }

  const handleProcessOCR = async (filename) => {
    try {
      setProcessingOCR(true)
      setError(null)
      const data = await sessionsAPI.processOCR(sessionId, {
        screenshot_id: filename,
      })
      setOcrText(data.text)
      setActiveTab('ocr')
    } catch (err) {
      setError('Failed to process OCR: ' + err.message)
    } finally {
      setProcessingOCR(false)
    }
  }

  const handleGenerateDocumentation = async () => {
    try {
      setGenerating(true)
      setError(null)
      const data = await sessionsAPI.generateDocumentation(sessionId, {
        ocr_text: ocrText,
      })
      setDocumentation(data.documentation)
      setActiveTab('documentation')
    } catch (err) {
      setError('Failed to generate documentation: ' + err.message)
    } finally {
      setGenerating(false)
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
      <h1 className="text-3xl font-bold mb-6">
        Session: {session?.session_id}
      </h1>

      {error && (
        <div className="bg-red-900 bg-opacity-50 border border-red-700 text-red-200 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      {/* Tabs */}
      <div className="border-b border-gray-700 mb-6">
        <nav className="flex space-x-8">
          <button
            onClick={() => setActiveTab('upload')}
            className={`py-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'upload'
                ? 'border-alive-active text-alive-active'
                : 'border-transparent text-gray-400 hover:text-gray-300'
            }`}
          >
            Upload Screenshot
          </button>
          <button
            onClick={() => setActiveTab('screenshots')}
            className={`py-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'screenshots'
                ? 'border-alive-active text-alive-active'
                : 'border-transparent text-gray-400 hover:text-gray-300'
            }`}
          >
            Screenshots ({screenshots.length})
          </button>
          <button
            onClick={() => setActiveTab('ocr')}
            className={`py-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'ocr'
                ? 'border-alive-active text-alive-active'
                : 'border-transparent text-gray-400 hover:text-gray-300'
            }`}
          >
            OCR Text
          </button>
          <button
            onClick={() => setActiveTab('documentation')}
            className={`py-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'documentation'
                ? 'border-alive-active text-alive-active'
                : 'border-transparent text-gray-400 hover:text-gray-300'
            }`}
          >
            Documentation
          </button>
        </nav>
      </div>

      {/* Upload Tab */}
      {activeTab === 'upload' && (
        <div>
          <FileUpload
            onUpload={handleUpload}
            disabled={uploading}
          />
          {uploading && (
            <div className="mt-4">
              <LoadingSpinner />
              <p className="text-center text-gray-400 mt-2">Uploading...</p>
            </div>
          )}
        </div>
      )}

      {/* Screenshots Tab */}
      {activeTab === 'screenshots' && (
        <div>
          {screenshots.length === 0 ? (
            <p className="text-gray-400">No screenshots uploaded yet</p>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {screenshots.map((screenshot, index) => (
                <div
                  key={index}
                  className="bg-alive-button border border-gray-700 rounded-lg overflow-hidden"
                >
                  <img
                    src={`http://localhost:8000${screenshot.path}`}
                    alt={`Screenshot ${index + 1}`}
                    className="w-full h-48 object-cover"
                    onError={(e) => {
                      // Fallback if image fails to load
                      e.target.style.display = 'none'
                    }}
                  />
                  <div className="p-4">
                    <p className="text-sm text-gray-400 mb-2">
                      {screenshot.filename}
                    </p>
                    <button
                      onClick={() => handleProcessOCR(screenshot.filename)}
                      disabled={processingOCR}
                      className="w-full bg-alive-active hover:bg-red-600 text-white text-sm py-2 px-4 rounded transition-colors disabled:opacity-50"
                    >
                      {processingOCR ? 'Processing...' : 'Process OCR'}
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* OCR Tab */}
      {activeTab === 'ocr' && (
        <div>
          {ocrText ? (
            <div>
              <textarea
                value={ocrText}
                onChange={(e) => setOcrText(e.target.value)}
                className="w-full h-64 bg-alive-button border border-gray-700 rounded-lg p-4 text-white font-mono text-sm"
                placeholder="OCR text will appear here..."
              />
              <button
                onClick={handleGenerateDocumentation}
                disabled={!ocrText || generating}
                className="mt-4 bg-alive-active hover:bg-red-600 text-white font-semibold py-2 px-6 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {generating ? 'Generating...' : 'Generate Documentation'}
              </button>
            </div>
          ) : (
            <p className="text-gray-400">
              Upload a screenshot and process OCR to see text here
            </p>
          )}
        </div>
      )}

      {/* Documentation Tab */}
      {activeTab === 'documentation' && (
        <div>
          {documentation ? (
            <div className="bg-alive-button border border-gray-700 rounded-lg p-6">
              <div className="prose prose-invert max-w-none">
                <ReactMarkdown>{documentation}</ReactMarkdown>
              </div>
            </div>
          ) : (
            <p className="text-gray-400">
              Generate documentation to see it here
            </p>
          )}
        </div>
      )}
    </div>
  )
}

