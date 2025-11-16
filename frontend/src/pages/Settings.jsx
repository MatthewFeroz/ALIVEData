import React, { useState, useEffect } from 'react'

export default function Settings() {
  const [apiKey, setApiKey] = useState('')
  const [saved, setSaved] = useState(false)

  useEffect(() => {
    // Load API key from localStorage or .env (client-side only)
    const stored = localStorage.getItem('openai_api_key')
    if (stored) {
      setApiKey(stored)
    }
  }, [])

  const handleSave = () => {
    localStorage.setItem('openai_api_key', apiKey)
    setSaved(true)
    setTimeout(() => setSaved(false), 3000)
  }

  return (
    <div>
      <h1 className="text-3xl font-bold mb-6">Settings</h1>

      <div className="bg-alive-button border border-gray-700 rounded-lg p-6 max-w-2xl">
        <h2 className="text-xl font-semibold mb-4">OpenAI API Configuration</h2>

        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-300 mb-2">
            API Key
          </label>
          <input
            type="password"
            value={apiKey}
            onChange={(e) => setApiKey(e.target.value)}
            placeholder="sk-..."
            className="w-full bg-alive-dark border border-gray-600 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-alive-active"
          />
          <p className="text-xs text-gray-500 mt-2">
            Note: For production, configure API key in backend .env file
          </p>
        </div>

        {apiKey && (
          <div className="mb-4">
            <p className="text-sm text-gray-400">
              Preview: {apiKey.substring(0, 7)}...{apiKey.substring(apiKey.length - 4)}
            </p>
          </div>
        )}

        <button
          onClick={handleSave}
          className="bg-alive-active hover:bg-red-600 text-white font-semibold py-2 px-6 rounded-lg transition-colors"
        >
          {saved ? 'Saved!' : 'Save Key'}
        </button>
      </div>

      <div className="mt-8 bg-alive-button border border-gray-700 rounded-lg p-6 max-w-2xl">
        <h2 className="text-xl font-semibold mb-4">About</h2>
        <p className="text-gray-400">
          ALIVE Data is a tool for automatically generating documentation from
          screenshots and terminal commands using OCR and AI.
        </p>
      </div>
    </div>
  )
}

