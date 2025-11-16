/**
 * API client for ALIVE Data backend
 */

import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Sessions API
export const sessionsAPI = {
  // Create a new session
  create: async (data = {}) => {
    const response = await api.post('/sessions', data)
    return response.data
  },

  // List all sessions
  list: async () => {
    const response = await api.get('/sessions')
    return response.data
  },

  // Get session details
  get: async (sessionId) => {
    const response = await api.get(`/sessions/${sessionId}`)
    return response.data
  },

  // Upload screenshot
  uploadScreenshot: async (sessionId, file, onProgress) => {
    const formData = new FormData()
    formData.append('file', file)

    const response = await api.post(
      `/sessions/${sessionId}/screenshots`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          if (onProgress && progressEvent.total) {
            const percentCompleted = Math.round(
              (progressEvent.loaded * 100) / progressEvent.total
            )
            onProgress(percentCompleted)
          }
        },
      }
    )
    return response.data
  },

  // Process OCR
  processOCR: async (sessionId, data) => {
    const response = await api.post(`/sessions/${sessionId}/ocr`, data)
    return response.data
  },

  // Generate documentation
  generateDocumentation: async (sessionId, data) => {
    const response = await api.post(
      `/sessions/${sessionId}/generate`,
      data
    )
    return response.data
  },

  // Get documentation file
  getDocumentation: async (sessionId) => {
    const response = await api.get(
      `/sessions/${sessionId}/documentation`,
      { responseType: 'blob' }
    )
    return response.data
  },

  // List screenshots
  listScreenshots: async (sessionId) => {
    const response = await api.get(`/sessions/${sessionId}/screenshots`)
    return response.data
  },
}

export default api

