import React from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Landing from './pages/Landing'
import SessionsList from './pages/SessionsList'
import SessionDetail from './pages/SessionDetail'
import Settings from './pages/Settings'

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/sessions" element={<Layout><SessionsList /></Layout>} />
        <Route path="/sessions/:sessionId" element={<Layout><SessionDetail /></Layout>} />
        <Route path="/settings" element={<Layout><Settings /></Layout>} />
      </Routes>
    </Router>
  )
}

export default App

