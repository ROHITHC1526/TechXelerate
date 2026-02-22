"use client"
import React from 'react'

interface TeamDetails {
  team_id: string
  team_name: string
  leader_name: string
  domain: string
  team_members?: any[]
  member_count?: number
  participant?: string
  role?: string
  checkin_time?: string
}

interface AttendanceModalProps {
  isOpen: boolean
  teamDetails: TeamDetails | null
  onClose: () => void
}

export default function AttendanceModal({ isOpen, teamDetails, onClose }: AttendanceModalProps) {
  if (!isOpen || !teamDetails) return null

  const memberCount = teamDetails.member_count || (teamDetails.team_members?.length || 0)

  return (
    <div className="fixed inset-0 bg-black/70 flex items-center justify-center p-4 z-50">
      <div className="bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 border-2 border-green-500 rounded-xl p-8 max-w-md w-full shadow-2xl shadow-green-500/50 animate-in fade-in duration-300">
        {/* Success Header */}
        <div className="text-center mb-8 space-y-3">
          <div className="text-6xl animate-bounce">✅</div>
          <h2 className="text-3xl font-black text-transparent bg-clip-text bg-gradient-to-r from-green-400 to-cyan-400">
            CHECK-IN SUCCESSFUL!
          </h2>
          <p className="text-green-300 font-mono text-sm">Team has been marked present</p>
        </div>

        {/* Team Details Card */}
        <div className="space-y-6 mb-8">
          {/* Participant Info */}
          {teamDetails.participant && (
            <div className="bg-green-500/10 border border-green-500/30 rounded-lg p-4">
              <p className="text-green-300 text-xs font-mono font-bold mb-1">👤 PARTICIPANT</p>
              <p className="text-white font-bold text-lg">{teamDetails.participant}</p>
              {teamDetails.role && (
                <p className="text-green-400 text-sm font-mono mt-1">Role: {teamDetails.role}</p>
              )}
            </div>
          )}

          {/* Team Information */}
          <div className="space-y-4 bg-gray-800/50 rounded-lg p-5 border border-gray-700">
            <div>
              <p className="text-cyan-300 text-xs font-mono font-bold mb-1">🏆 TEAM ID</p>
              <p className="text-white font-mono font-bold text-lg tracking-wide">{teamDetails.team_id}</p>
            </div>

            <div className="border-t border-gray-700 pt-4">
              <p className="text-cyan-300 text-xs font-mono font-bold mb-1">📋 TEAM NAME</p>
              <p className="text-white font-bold text-lg">{teamDetails.team_name}</p>
            </div>

            <div className="border-t border-gray-700 pt-4">
              <p className="text-cyan-300 text-xs font-mono font-bold mb-1">👨‍💼 TEAM LEAD</p>
              <p className="text-white font-bold text-lg">{teamDetails.leader_name}</p>
            </div>

            <div className="border-t border-gray-700 pt-4">
              <p className="text-cyan-300 text-xs font-mono font-bold mb-1">🎯 DOMAIN/TRACK</p>
              <p className="text-purple-300 font-bold text-lg">{teamDetails.domain}</p>
            </div>

            {memberCount > 0 && (
              <div className="border-t border-gray-700 pt-4">
                <p className="text-cyan-300 text-xs font-mono font-bold mb-1">👥 TEAM MEMBERS</p>
                <p className="text-white font-bold text-lg">{memberCount} Member{memberCount !== 1 ? 's' : ''}</p>
              </div>
            )}

            {teamDetails.checkin_time && (
              <div className="border-t border-gray-700 pt-4">
                <p className="text-cyan-300 text-xs font-mono font-bold mb-1">⏰ CHECK-IN TIME</p>
                <p className="text-white font-mono text-sm">
                  {new Date(teamDetails.checkin_time).toLocaleString()}
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Action Buttons */}
        <div className="space-y-3">
          <button
            onClick={onClose}
            className="w-full py-4 bg-gradient-to-r from-green-600 to-green-500 rounded-lg font-bold text-lg hover:shadow-lg hover:shadow-green-500/50 transition text-white"
          >
            ✅ PROCEED TO EVENT
          </button>

          <button
            onClick={onClose}
            className="w-full py-3 bg-gray-800 hover:bg-gray-700 rounded-lg font-bold transition text-gray-200"
          >
            SCAN ANOTHER TEAM
          </button>
        </div>

        {/* Footer */}
        <p className="text-center text-xs text-gray-500 font-mono mt-6">
          🎉 Welcome to TechXelarate 2026!
        </p>
      </div>
    </div>
  )
}
