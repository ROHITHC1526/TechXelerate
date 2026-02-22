import React from 'react'

export default function Download() {
  return (
    <main className="min-h-screen p-8">
      <div className="max-w-3xl mx-auto glass p-6 text-center">
        <h2 className="text-2xl neon-glow">Download ID</h2>
        <p className="mt-4 text-gray-300">Enter your Team ID and Access Key to download the ID card.</p>
        {/* Implementation omitted for brevity; integrate with /api/download-id */}
      </div>
    </main>
  )
}
