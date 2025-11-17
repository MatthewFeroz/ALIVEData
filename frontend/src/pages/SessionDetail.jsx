import React, { useState } from 'react'
import { useParams } from 'react-router-dom'
import ReactMarkdown from 'react-markdown'
import { useQuery, useMutation, useAction } from 'convex/react'
import { api } from '../../convex/_generated/api'
import { createWorker } from 'tesseract.js'
import FileUpload from '../components/FileUpload'
import LoadingSpinner from '../components/LoadingSpinner'

export default function SessionDetail() {
  const { sessionId } = useParams()
  const [ocrText, setOcrText] = useState('')
  const [uploading, setUploading] = useState(false)
  const [processingOCR, setProcessingOCR] = useState(false)
  const [generating, setGenerating] = useState(false)
  const [error, setError] = useState(null)
  const [activeTab, setActiveTab] = useState('upload')

  // Use Convex queries
  const session = useQuery(api.sessions.getSession, { sessionId })
  const screenshots = useQuery(api.files.listScreenshots, { sessionId })
  const documentation = useQuery(api.documentation.getDocumentation, { sessionId })

  // Use Convex mutations and actions
  const generateUploadUrl = useMutation(api.files.generateUploadUrl)
  const uploadScreenshot = useMutation(api.files.uploadScreenshot)
  const summarizeTextAction = useAction(api.ai.summarizeText)
  const saveDocumentation = useMutation(api.documentation.saveDocumentation)

  const loading = session === undefined

  const handleUpload = async (file) => {
    try {
      setUploading(true)
      setError(null)
      
      // Get upload URL from Convex
      const uploadUrl = await generateUploadUrl({})
      
      // Upload file to Convex storage
      const result = await fetch(uploadUrl, {
        method: "POST",
        headers: { "Content-Type": file.type },
        body: file,
      })
      
      if (!result.ok) {
        const errorText = await result.text()
        throw new Error(`Upload failed: ${result.statusText} - ${errorText}`)
      }
      
      // Convex storage returns the storageId as a string
      const storageId = await result.text()
      
      if (!storageId || storageId.trim() === '') {
        throw new Error(`Invalid storage ID received: empty response`)
      }

      // Create screenshot record
      await uploadScreenshot({
        sessionId,
        filename: file.name,
        fileId: storageId,
        size: file.size,
      })

      // Screenshots will automatically update via Convex query!
    } catch (err) {
      setError('Failed to upload screenshot: ' + (err.message || String(err)))
      console.error('Upload error:', err)
    } finally {
      setUploading(false)
    }
  }

  const handleProcessOCR = async (screenshot) => {
    try {
      setProcessingOCR(true)
      setError(null)
      
      if (!screenshot || !screenshot.url) {
        throw new Error('Screenshot URL is required for OCR processing')
      }
      
      console.log('Processing OCR for screenshot:', screenshot.url)
      
      // Process OCR in the browser using Tesseract.js
      const worker = await createWorker('eng')
      try {
        const { data } = await worker.recognize(screenshot.url)
        setOcrText(data.text.trim())
        setActiveTab('ocr')
      } finally {
        await worker.terminate()
      }
    } catch (err) {
      setError('Failed to process OCR: ' + (err.message || String(err)))
      console.error('OCR error:', err)
    } finally {
      setProcessingOCR(false)
    }
  }

  const handleGenerateDocumentation = async () => {
    try {
      setGenerating(true)
      setError(null)
      
      if (!ocrText || !ocrText.trim()) {
        throw new Error('Please process OCR first to extract text from the image')
      }
      
      console.log('Generating documentation from OCR text...')
      
      // Call the action to generate documentation
      const documentation = await summarizeTextAction({
        ocrText,
      })
      
      console.log('Documentation generated, saving...')
      
      // Save the documentation
      await saveDocumentation({
        sessionId,
        ocrText,
        documentation,
      })
      
      setActiveTab('documentation')
      // Documentation will automatically update via Convex query!
    } catch (err) {
      setError('Failed to generate documentation: ' + (err.message || String(err)))
      console.error('Documentation error:', err)
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

  if (!session) {
    return (
      <div className="text-center py-12 text-gray-400">
        <p className="text-xl mb-4">Session not found</p>
      </div>
    )
  }

  return (
    <div>
      <h1 className="text-3xl font-bold mb-6">
        Session: {session.sessionId}
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
            Screenshots ({screenshots?.length || 0})
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
          {!screenshots || screenshots.length === 0 ? (
            <p className="text-gray-400">No screenshots uploaded yet</p>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {screenshots.map((screenshot) => (
                <div
                  key={screenshot._id}
                  className="bg-alive-button border border-gray-700 rounded-lg overflow-hidden"
                >
                  {screenshot.url && (
                    <img
                      src={screenshot.url}
                      alt={screenshot.filename}
                      className="w-full h-48 object-cover"
                      onError={(e) => {
                        e.target.style.display = 'none'
                      }}
                    />
                  )}
                  <div className="p-4">
                    <p className="text-sm text-gray-400 mb-2">
                      {screenshot.filename}
                    </p>
                    <button
                      onClick={() => handleProcessOCR(screenshot)}
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
          {documentation?.content ? (
            <div className="bg-alive-button border border-gray-700 rounded-lg p-6 overflow-auto">
              <div className="prose prose-invert prose-lg max-w-none prose-headings:text-white prose-headings:font-bold prose-p:text-gray-300 prose-p:leading-relaxed prose-a:text-alive-active prose-a:no-underline hover:prose-a:underline prose-strong:text-white prose-strong:font-semibold prose-code:text-alive-active prose-code:bg-gray-800 prose-code:px-1 prose-code:py-0.5 prose-code:rounded prose-code:text-sm prose-pre:bg-gray-900 prose-pre:border prose-pre:border-gray-700 prose-blockquote:border-l-alive-active prose-blockquote:text-gray-300 prose-ul:text-gray-300 prose-ol:text-gray-300 prose-li:marker:text-gray-500 prose-hr:border-gray-700">
                <ReactMarkdown
                  components={{
                    code: ({ node, inline, className, children, ...props }) => {
                      const match = /language-(\w+)/.exec(className || '')
                      return !inline && match ? (
                        <pre className="bg-gray-900 border border-gray-700 rounded-lg p-4 overflow-x-auto">
                          <code className={className} {...props}>
                            {children}
                          </code>
                        </pre>
                      ) : (
                        <code className="bg-gray-800 text-alive-active px-1.5 py-0.5 rounded text-sm font-mono" {...props}>
                          {children}
                        </code>
                      )
                    },
                  }}
                >
                  {documentation.content}
                </ReactMarkdown>
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
