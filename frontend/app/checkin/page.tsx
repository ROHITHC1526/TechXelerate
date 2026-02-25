"use client"
import React, { useState } from 'react'
import AttendanceModal from '@/components/AttendanceModal'

export default function Checkin() {
  const [message, setMessage] = useState('')
  const [teamId, setTeamId] = useState('')
  const [isVerifying, setIsVerifying] = useState(false)
  const [teamDetails, setTeamDetails] = useState<any>(null)
  const [showModal, setShowModal] = useState(false)

  // derive API base from environment so that the frontend can
  // target whatever backend URL is appropriate (localhost:8000 in dev,
  // maybe /api proxy in production). Defaults to empty string which
  // causes fetch to be relative to the current origin.
  const API_BASE = process.env.NEXT_PUBLIC_API_URL || ''

  const handleCheckin = async () => {
    const id = teamId.trim().toUpperCase()
    if (!id) {
      setMessage('❌ Please enter Team ID')
      return
    }
    setIsVerifying(true)
    try {
      const resp = await fetch(`${API_BASE}/api/attendance/checkin`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ team_id: id })
      })
      const data = await resp.json()
      if (resp.ok && data.status === 'success') {
        setMessage('✅ CHECK-IN SUCCESSFUL!')
        // fetch team details for modal
        const tresp = await fetch(`${API_BASE}/api/team/${id}`)
        if (tresp.ok) setTeamDetails(await tresp.json())
        setShowModal(true)
      } else {
        setMessage(`❌ ${data.detail || data.message || 'Check-in failed'}`)
      }
    } catch (e) {
      setMessage('❌ Network error (ensure backend is running and API_URL is set)')
    } finally {
      setIsVerifying(false)
    }
  }



  const handleModalClose = () => {
    setShowModal(false)
    setTeamId('')
    setTeamDetails(null)
    setMessage('')
  }



  return (
    <main className="min-h-screen bg-black text-white p-8 relative">
      <div className="absolute inset-0 opacity-10">
        <div className="w-full h-full" style={{
          backgroundImage: 'linear-gradient(0deg, transparent 24%, rgba(0, 229, 255, 0.1) 25%, rgba(0, 229, 255, 0.1) 26%, transparent 27%, transparent 74%, rgba(0, 229, 255, 0.1) 75%, rgba(0, 229, 255, 0.1) 76%, transparent 77%, transparent), linear-gradient(90deg, transparent 24%, rgba(0, 229, 255, 0.1) 25%, rgba(0, 229, 255, 0.1) 26%, transparent 27%, transparent 74%, rgba(0, 229, 255, 0.1) 75%, rgba(0, 229, 255, 0.1) 76%, transparent 77%, transparent)',
          backgroundSize: '60px 60px'
        }}></div>
      </div>

      <div className="max-w-md mx-auto relative z-10 space-y-6">
        <div className="mb-8">
          <h1 className="text-4xl font-black text-transparent bg-clip-text bg-gradient-to-r from-green-400 to-cyan-400 mb-2">
            ✅ ATTENDANCE CHECK-IN
          </h1>
          <p className="text-gray-400 font-mono">Enter Team ID to mark attendance</p>
        </div>

        {message && (
          <div className={`p-4 rounded-lg border text-sm font-mono font-bold ${
            message.includes('SUCCESSFUL')
              ? 'bg-green-500/20 border-green-500/50 text-green-300'
              : message.includes('✅')
              ? 'bg-blue-500/20 border-blue-500/50 text-blue-300'
              : 'bg-red-500/20 border-red-500/50 text-red-300'
          }`}>
            {message}
          </div>
        )}

        <div className="space-y-4">
          <label className="block text-sm text-cyan-300 font-mono font-bold">Team ID</label>
          <input
            type="text"
            value={teamId}
            onChange={(e) => setTeamId(e.target.value.toUpperCase())}
            placeholder="HACKCSM-001"
            className="w-full p-4 bg-gray-900/50 rounded-lg text-white border-2 border-cyan-500/50 focus:border-cyan-400 focus:outline-none text-lg tracking-widest font-mono font-bold"
          />
        </div>

        <button
          onClick={handleCheckin}
          disabled={!teamId || isVerifying}
          className="w-full py-4 bg-gradient-to-r from-green-600 to-green-500 rounded-lg font-bold text-lg hover:shadow-lg hover:shadow-green-500/50 transition disabled:opacity-50"
        >
          {isVerifying ? '⏳ CHECKING IN...' : '✅ CHECK IN'}
        </button>
      </div>

      {/* Attendance Success Modal */}
      <AttendanceModal 
        isOpen={showModal} 
        teamDetails={teamDetails} 
        onClose={handleModalClose} 
      />
    </main>
  )
}
