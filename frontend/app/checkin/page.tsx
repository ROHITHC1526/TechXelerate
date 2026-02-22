"use client"
import React, { useEffect, useRef, useState } from 'react'
import AttendanceModal from '@/components/AttendanceModal'

export default function Checkin() {
  const [message, setMessage] = useState('')
  const [scanning, setScanning] = useState(false)
  const [qrData, setQrData] = useState<string | null>(null)
  const [accessKey, setAccessKey] = useState('')
  const [isVerifying, setIsVerifying] = useState(false)
  const [teamDetails, setTeamDetails] = useState<any>(null)
  const [showModal, setShowModal] = useState(false)
  const videoRef = useRef<HTMLVideoElement | null>(null)
  const scannerRef = useRef<any>(null)

  const handleResult = async (val: { data: string } | string) => {
    const data = typeof val === 'string' ? val : val.data
    if (!data) return
    
    setQrData(data)
    setMessage('✅ QR Code scanned. Verifying...')
    setIsVerifying(true)
    
    try {
      // Call the attendance endpoint with the QR data
      const resp = await fetch('http://localhost:8000/api/attendance/scan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ qr_data: data })
      })
      
      if (resp.ok) {
        const result = await resp.json()
        setMessage(`✅ CHECK-IN SUCCESSFUL!`)
        setTeamDetails(result)
        setShowModal(true)
        
        // Stop scanner
        if (scannerRef.current) {
          scannerRef.current.stop()
          setScanning(false)
        }
      } else {
        const j = await resp.json().catch(() => ({}))
        setMessage(`❌ Check-in failed. ${j.detail || 'Invalid QR code.'}`)
      }
    } catch (e) {
      setMessage('❌ Network error during verification.')
    } finally {
      setIsVerifying(false)
    }
  }

  const handleCheckin = async () => {
    if (!qrData) {
      setMessage('❌ Please scan QR code first')
      return
    }

    setIsVerifying(true)
    try {
      const resp = await fetch('http://localhost:8000/api/attendance/scan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ qr_data: qrData })
      })
      
      if (resp.ok) {
        const data = await resp.json()
        setMessage(`✅ CHECK-IN SUCCESSFUL!`)
        setTeamDetails(data)
        setShowModal(true)
        setQrData(null)
        setAccessKey('')
      } else {
        const j = await resp.json().catch(() => ({}))
        setMessage(`❌ ${j.detail || 'Check-in failed'}`)
      }
    } catch (e) {
      setMessage('❌ Network error')
    } finally {
      setIsVerifying(false)
    }
  }

  const resetScanner = async () => {
    setQrData(null)
    setAccessKey('')
    setMessage('')
    setShowModal(false)
    setTeamDetails(null)
    try {
      const mod = await import('qr-scanner')
      const QrScanner = (mod && (mod as any).default) || mod
      QrScanner.WORKER_PATH = 'https://unpkg.com/qr-scanner@1.4.0/qr-scanner-worker.min.js'
      if (videoRef.current) {
        scannerRef.current = new QrScanner(
          videoRef.current,
          (result: { data: string } | string) => handleResult(result)
        )
        await scannerRef.current.start()
        setScanning(true)
      }
    } catch (err) {
      setMessage('Camera unavailable')
    }
  }

  const handleModalClose = () => {
    setShowModal(false)
    resetScanner()
  }

  useEffect(() => {
    let mounted = true
    const setup = async () => {
      try {
        const mod = await import('qr-scanner')
        const QrScanner = (mod && (mod as any).default) || mod
        QrScanner.WORKER_PATH = 'https://unpkg.com/qr-scanner@1.4.0/qr-scanner-worker.min.js'
        if (!mounted) return
        if (videoRef.current) {
          scannerRef.current = new QrScanner(
            videoRef.current,
            (result: { data: string } | string) => handleResult(result)
          )
          await scannerRef.current.start()
          setScanning(true)
        }
      } catch (err) {
        setMessage('📱 Camera unavailable - use image upload below')
      }
    }
    setup()
    return () => {
      mounted = false
      if (scannerRef.current) scannerRef.current.stop()
    }
  }, [])

  const onFile = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files && e.target.files[0]
    if (!f) return
    try {
      const mod = await import('qr-scanner')
      const QrScanner = (mod && (mod as any).default) || mod
      const data = await QrScanner.scanImage(f)
      if (typeof data === 'string') {
        handleResult(data)
      } else {
        handleResult(data.data)
      }
    } catch (err) {
      setMessage('❌ Could not read image')
    }
  }

  return (
    <main className="min-h-screen bg-black text-white p-8 relative">
      <div className="absolute inset-0 opacity-10">
        <div className="w-full h-full" style={{
          backgroundImage: 'linear-gradient(0deg, transparent 24%, rgba(0, 229, 255, 0.1) 25%, rgba(0, 229, 255, 0.1) 26%, transparent 27%, transparent 74%, rgba(0, 229, 255, 0.1) 75%, rgba(0, 229, 255, 0.1) 76%, transparent 77%, transparent), linear-gradient(90deg, transparent 24%, rgba(0, 229, 255, 0.1) 25%, rgba(0, 229, 255, 0.1) 26%, transparent 27%, transparent 74%, rgba(0, 229, 255, 0.1) 75%, rgba(0, 229, 255, 0.1) 76%, transparent 77%, transparent)',
          backgroundSize: '60px 60px'
        }}></div>
      </div>

      <div className="max-w-3xl mx-auto relative z-10">
        <div className="mb-8">
          <h1 className="text-4xl font-black text-transparent bg-clip-text bg-gradient-to-r from-green-400 to-cyan-400 mb-2">
            ✅ ATTENDANCE CHECK-IN
          </h1>
          <p className="text-gray-400 font-mono">Scan QR + Enter Code to Mark Presence</p>
        </div>

        <div className="border border-green-500/30 rounded-xl p-8 bg-green-500/5 backdrop-blur-sm space-y-6">
          {/* Status Message */}
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

          {!qrData ? (
            <>
              {/* Camera Scanner */}
              <div className="space-y-4">
                <div>
                  <label className="block text-sm text-green-300 mb-3 font-mono font-bold">
                    {scanning ? '🎥 CAMERA ACTIVE - SCAN QR CODE' : '📷 CAMERA SCANNER'}
                  </label>
                  <video
                    ref={videoRef}
                    className="w-full rounded-lg border-2 border-green-500/50 bg-gray-900 aspect-video object-cover"
                    muted
                    playsInline
                  />
                </div>

                {/* File Upload */}
                <div className="space-y-3">
                  <label className="block text-sm text-green-300 font-mono font-bold">📁 OR UPLOAD QR IMAGE</label>
                  <div className="relative border-2 border-dashed border-green-500/50 rounded-lg p-6 hover:border-green-400 transition text-center cursor-pointer group/upload">
                    <input
                      type="file"
                      accept="image/*"
                      onChange={onFile}
                      className="absolute inset-0 opacity-0 cursor-pointer"
                    />
                    <div className="space-y-2">
                      <div className="text-3xl">📸</div>
                      <p className="text-green-400 group-hover/upload:text-green-300 transition font-mono">
                        Click to upload image
                      </p>
                      <p className="text-xs text-gray-500 font-mono">PNG, JPG up to 10MB</p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Instructions */}
              <div className="border-t border-gray-700 pt-6 bg-gray-900/30 rounded-lg p-4">
                <h3 className="text-sm font-bold text-cyan-400 mb-3 font-mono">📋 STEP 1: SCAN QR CODE</h3>
                <ol className="space-y-2 text-xs text-gray-400 font-mono">
                  <li>✓ Allow camera access when prompted</li>
                  <li>✓ Position QR code in frame for auto-scan</li>
                  <li>✓ Or upload a QR image file</li>
                </ol>
              </div>
            </>
          ) : (
            <>
              {/* Access Key Entry - Only if QR failed */}
              <div className="space-y-4 border-t border-gray-700 pt-6">
                <div className="bg-yellow-500/20 border border-yellow-500/50 p-4 rounded-lg mb-6">
                  <p className="text-yellow-300 text-sm font-mono">
                    ⚠️ QR verification failed. Please enter your unique access key manually.
                  </p>
                </div>
                <div>
                  <label className="block text-sm text-blue-300 font-mono font-bold mb-3">
                    🔐 ENTER ACCESS KEY
                  </label>
                  <div className="space-y-3">
                    <input
                      type="text"
                      value={accessKey}
                      onChange={(e) => setAccessKey(e.target.value.toUpperCase())}
                      placeholder="UNIQUE-ACCESS-KEY"
                      className="w-full p-4 bg-gray-900/50 rounded-lg text-white border-2 border-blue-500/50 focus:border-blue-400 focus:outline-none text-lg tracking-widest font-mono font-bold"
                    />
                    <p className="text-xs text-gray-500 text-center font-mono">
                      Check your team ID card for the unique access key
                    </p>
                  </div>
                </div>

                <button
                  onClick={handleCheckin}
                  disabled={!accessKey || isVerifying || accessKey.length === 0}
                  className="w-full py-4 bg-gradient-to-r from-green-600 to-green-500 rounded-lg font-bold text-lg hover:shadow-lg hover:shadow-green-500/50 transition disabled:opacity-50"
                >
                  {isVerifying ? '⏳ VERIFYING...' : '✅ VERIFY & CHECK-IN'}
                </button>

                <button
                  onClick={resetScanner}
                  className="w-full py-3 bg-gray-800 hover:bg-gray-700 rounded-lg font-bold transition"
                >
                  🔄 SCAN AGAIN
                </button>
              </div>

              <div className="border-t border-gray-700 pt-4 bg-gray-900/30 rounded-lg p-4">
                <p className="text-xs text-gray-400 font-mono">
                  <strong>QR Scan Failed:</strong> Using manual access key verification instead.
                </p>
              </div>
            </>
          )}
        </div>
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
