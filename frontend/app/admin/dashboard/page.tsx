"use client"
import React, { useEffect, useState } from 'react'

export default function AdminDashboard(){
  const [stats, setStats] = useState<any>(null)
  const [filters, setFilters] = useState({ domain: '', year: '', attendance: '' })
  
  const fetchStats = async () => {
    try {
      const res = await fetch('/api/stats')
      if (res.ok) setStats(await res.json())
    } catch (e) {
      console.error('Failed to fetch stats:', e)
    }
  }

  const downloadCSV = async () => {
    try {
      const params = new URLSearchParams()
      if (filters.domain) params.set('domain', filters.domain)
      if (filters.year) params.set('year', filters.year)
      if (filters.attendance) params.set('attendance', filters.attendance)
      const token = localStorage.getItem('admin_token')
      const res = await fetch('/api/admin/export?' + params.toString(), { 
        headers: { 'Authorization': token ? `Bearer ${token}` : '' } 
      })
      if (!res.ok) { alert('Export failed'); return }
      const blob = await res.blob()
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = 'teams_export.csv'
      a.click()
      URL.revokeObjectURL(url)
    } catch (e) {
      alert('Error exporting CSV')
    }
  }

  useEffect(() => {
    fetchStats()
    try {
      const ws = new WebSocket((location.protocol === 'https:' ? 'wss://' : 'ws://') + location.host + '/api/ws/stats')
      ws.onmessage = () => fetchStats()
      return () => ws.close()
    } catch (e) {
      console.log('WebSocket not available')
    }
  }, [])

  return (
    <main className="min-h-screen p-8 bg-black text-white">
      <div className="max-w-6xl mx-auto p-6 bg-gray-900 rounded-lg border border-cyan-500">
        <h2 className="text-3xl font-bold text-cyan-400 mb-6">Admin Dashboard</h2>
        
        {!stats && <p className="text-gray-400 text-center py-8">Loading stats...</p>}
        
        {stats && (
          <>
            <div className="flex gap-2 mb-6 flex-wrap">
              <select 
                value={filters.domain} 
                onChange={(e) => setFilters(f => ({...f, domain: e.target.value}))} 
                className="p-2 bg-gray-800 rounded border border-gray-600 text-white"
              >
                <option value="">All Domains</option>
                <option value="Explainable AI">Explainable AI</option>
                <option value="Cybersecurity">Cybersecurity</option>
                <option value="Sustainability">Sustainability</option>
                <option value="Data Intelligence">Data Intelligence</option>
              </select>
              
              <select 
                value={filters.year} 
                onChange={(e) => setFilters(f => ({...f, year: e.target.value}))} 
                className="p-2 bg-gray-800 rounded border border-gray-600 text-white"
              >
                <option value="">All Years</option>
                <option value="1">Year 1</option>
                <option value="2">Year 2</option>
                <option value="3">Year 3</option>
                <option value="4">Year 4</option>
              </select>
              
              <select 
                value={filters.attendance} 
                onChange={(e) => setFilters(f => ({...f, attendance: e.target.value}))} 
                className="p-2 bg-gray-800 rounded border border-gray-600 text-white"
              >
                <option value="">All Status</option>
                <option value="true">Checked In</option>
                <option value="false">Not Checked In</option>
              </select>
              
              <button 
                onClick={downloadCSV} 
                className="ml-auto px-6 py-2 bg-green-600 rounded font-bold hover:bg-green-700"
              >
                📥 Export CSV
              </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="p-4 bg-gray-800 rounded border border-cyan-500">
                <p className="text-sm text-gray-400">Total Teams</p>
                <p className="text-4xl font-bold text-cyan-400">{stats.total_teams || 0}</p>
              </div>
              
              <div className="p-4 bg-gray-800 rounded border border-cyan-500">
                <p className="text-sm text-gray-400">Total Participants</p>
                <p className="text-4xl font-bold text-pink-400">{stats.total_participants || 0}</p>
              </div>
              
              <div className="p-4 bg-gray-800 rounded border border-cyan-500">
                <p className="text-sm text-gray-400">Checked In</p>
                <p className="text-4xl font-bold text-green-400">{stats.checked_in || 0}</p>
              </div>
            </div>

            {stats.domain_distribution && (
              <div className="mt-6 p-4 bg-gray-800 rounded border border-cyan-500">
                <h3 className="text-lg font-bold text-cyan-400 mb-3">Domain Distribution</h3>
                <div className="space-y-2">
                  {Object.entries(stats.domain_distribution).map(([domain, count]: [string, any]) => (
                    <div key={domain} className="flex justify-between items-center">
                      <span className="text-gray-300">{domain}</span>
                      <span className="font-bold text-pink-400">{count}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </main>
  )
}

