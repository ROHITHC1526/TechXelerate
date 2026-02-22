"use client"
import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'

export default function Startup() {
  const router = useRouter()
  const [progress, setProgress] = useState(0)
  const [isComplete, setIsComplete] = useState(false)

  useEffect(() => {
    // Animate from 0 to 100 over 3.5 seconds
    const interval = setInterval(() => {
      setProgress(prev => {
        const next = prev + (100 / 35)
        if (next >= 100) {
          setIsComplete(true)
          clearInterval(interval)
          return 100
        }
        return next
      })
    }, 100)

    return () => clearInterval(interval)
  }, [])

  useEffect(() => {
    // Redirect when complete
    if (isComplete) {
      const timer = setTimeout(() => {
        // set short-lived cookie so middleware will allow access to root
        try {
          document.cookie = 'skipStartup=1; max-age=10; path=/'
        } catch (e) {
          // ignore in non-browser environments
        }
        router.push('/') // Go to root which redirects to home via middleware
      }, 800)
      return () => clearTimeout(timer)
    }
  }, [isComplete, router])

  const rotation = (progress / 100) * 180 - 90

  return (
    <div className="min-h-screen bg-black text-white flex items-center justify-center overflow-hidden relative">
      <style>{`
        @keyframes floatBubble {
          0%, 100% { transform: translateY(0px) translateX(0px); }
          25% { transform: translateY(-30px) translateX(15px); }
          50% { transform: translateY(-60px) translateX(-20px); }
          75% { transform: translateY(-30px) translateX(25px); }
        }
        @keyframes pulse-glow {
          0%, 100% { opacity: 0.3; }
          50% { opacity: 0.8; }
        }
        @keyframes rotate-slow {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
        @keyframes scan-line {
          0% { transform: translateY(-100%); }
          100% { transform: translateY(100%); }
        }
      `}</style>

      {/* Animated grid background */}
      <div className="absolute inset-0 opacity-5 overflow-hidden">
        <div className="absolute w-full h-full" style={{
          backgroundImage: 'linear-gradient(0deg, transparent 24%, rgba(0, 229, 255, 0.1) 25%, rgba(0, 229, 255, 0.1) 26%, transparent 27%, transparent 74%, rgba(0, 229, 255, 0.1) 75%, rgba(0, 229, 255, 0.1) 76%, transparent 77%, transparent), linear-gradient(90deg, transparent 24%, rgba(0, 229, 255, 0.1) 25%, rgba(0, 229, 255, 0.1) 26%, transparent 27%, transparent 74%, rgba(0, 229, 255, 0.1) 75%, rgba(0, 229, 255, 0.1) 76%, transparent 77%, transparent)',
          backgroundSize: '80px 80px'
        }}></div>
      </div>

      {/* Floating animated bubbles - Network nodes */}
      <div className="absolute inset-0 overflow-hidden">
        {/* Large bubbles */}
        <div 
          className="absolute w-64 h-64 bg-gradient-to-br from-cyan-500/30 to-blue-500/20 rounded-full blur-3xl"
          style={{
            top: '-100px',
            right: '-100px',
            animation: 'floatBubble 8s ease-in-out infinite',
            filter: 'drop-shadow(0 0 30px rgba(0, 200, 150, 0.4))'
          }}
        ></div>
        
        <div 
          className="absolute w-80 h-80 bg-gradient-to-br from-purple-500/30 to-pink-500/20 rounded-full blur-3xl"
          style={{
            bottom: '-120px',
            left: '-100px',
            animation: 'floatBubble 9s ease-in-out infinite 1s',
            filter: 'drop-shadow(0 0 30px rgba(147, 51, 234, 0.4))'
          }}
        ></div>

        <div 
          className="absolute w-72 h-72 bg-gradient-to-br from-green-500/30 to-cyan-500/20 rounded-full blur-3xl"
          style={{
            top: '50%',
            left: '-80px',
            animation: 'floatBubble 10s ease-in-out infinite 2s',
            filter: 'drop-shadow(0 0 30px rgba(34, 197, 94, 0.4))'
          }}
        ></div>

        {/* Medium bubbles */}
        <div 
          className="absolute w-48 h-48 bg-gradient-to-br from-cyan-400/40 rounded-full blur-2xl"
          style={{
            top: '20%',
            right: '10%',
            animation: 'floatBubble 7s ease-in-out infinite 0.5s',
            filter: 'drop-shadow(0 0 20px rgba(0, 229, 255, 0.5))'
          }}
        ></div>

        <div 
          className="absolute w-56 h-56 bg-gradient-to-br from-pink-500/30 rounded-full blur-2xl"
          style={{
            bottom: '15%',
            right: '-60px',
            animation: 'floatBubble 8.5s ease-in-out infinite 1.5s',
            filter: 'drop-shadow(0 0 20px rgba(236, 72, 153, 0.4))'
          }}
        ></div>
      </div>

      {/* Content Container */}
      <div className="relative z-20 text-center space-y-8 px-6 max-w-2xl">
        {/* Animated HackAthon Title */}
        <div className="space-y-4">
          <div className="flex items-center justify-center gap-3 mb-6">
            <div className="w-2 h-2 bg-cyan-400 rounded-full animate-pulse"></div>
            <h2 className="text-sm font-mono text-cyan-400 tracking-widest">HACKATHON SYSTEMS</h2>
            <div className="w-2 h-2 bg-cyan-400 rounded-full animate-pulse"></div>
          </div>
          
          <h1 className="text-7xl font-black text-transparent bg-clip-text bg-gradient-to-r from-cyan-300 via-green-300 to-blue-400">
            SYSTEM BOOT
          </h1>
          
          <p className="text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-400 font-bold text-lg">
            INITIALIZING NETWORK • DEPLOYING CODE • BUILDING FUTURES
          </p>
        </div>

        {/* Network Speedometer Gauge */}
        <div className="flex justify-center py-8">
          <div className="relative w-full max-w-md">
            {/* Outer glow */}
            <div 
              className="absolute inset-0 rounded-full blur-xl opacity-50"
              style={{
                background: `conic-gradient(from 180deg, rgba(0, 200, 150, 0.3) 0deg, rgba(100, 200, 255, 0.3) ${progress * 1.8}deg, rgba(30, 40, 50, 0.2) ${progress * 1.8}deg, transparent 360deg)`,
              }}
            ></div>

            {/* Gauge SVG */}
            <svg className="w-full aspect-square" viewBox="0 0 300 180" style={{filter: 'drop-shadow(0 0 25px rgba(0, 200, 150, 0.4))'}}>
              <defs>
                <linearGradient id="needleGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stopColor="rgba(0, 255, 200, 1)" />
                  <stop offset="100%" stopColor="rgba(100, 200, 255, 1)" />
                </linearGradient>
              </defs>

              {/* Gauge background arc */}
              <path
                d="M 40 160 A 120 120 0 0 1 260 160"
                fill="none"
                stroke="rgba(20, 30, 40, 1)"
                strokeWidth="14"
                strokeLinecap="round"
              />
              
              {/* Colored progress zones */}
              <path
                d="M 40 160 A 120 120 0 0 1 260 160"
                fill="none"
                stroke="url(#needleGradient)"
                strokeWidth="14"
                strokeLinecap="round"
                strokeDasharray={`${(120 * Math.PI * progress) / 100}, ${120 * Math.PI}`}
                opacity="0.8"
              />

              {/* Tick marks */}
              {[0, 25, 50, 75, 100].map((val) => {
                const angle = (val / 100) * Math.PI
                const x1 = 150 + 125 * Math.cos(angle)
                const y1 = 160 - 125 * Math.sin(angle)
                const x2 = 150 + 108 * Math.cos(angle)
                const y2 = 160 - 108 * Math.sin(angle)
                return (
                  <line key={val} x1={x1} y1={y1} x2={x2} y2={y2} stroke="rgba(100, 200, 255, 0.6)" strokeWidth="2" />
                )
              })}

              {/* Needle */}
              <line
                x1="150"
                y1="160"
                x2={150 + 110 * Math.cos((rotation * Math.PI) / 180)}
                y2={160 - 110 * Math.sin((rotation * Math.PI) / 180)}
                stroke="url(#needleGradient)"
                strokeWidth="6"
                strokeLinecap="round"
                style={{
                  transition: 'all 0.12s linear',
                  filter: 'drop-shadow(0 0 8px rgba(0, 200, 150, 1))'
                }}
              />

              {/* Center dot */}
              <circle cx="150" cy="160" r="12" fill="rgba(0, 200, 150, 1)" />
              <circle cx="150" cy="160" r="8" fill="rgba(0, 255, 200, 0.8)" />
            </svg>

            {/* Percentage display */}
            <div className="absolute inset-0 flex items-center justify-center pt-12">
              <div className="text-center">
                <div className="text-6xl font-black text-transparent bg-clip-text bg-gradient-to-r from-cyan-300 to-green-400">
                  {Math.floor(progress)}%
                </div>
                <div className="text-xs text-cyan-400 font-mono mt-2 tracking-widest">LOADING</div>
              </div>
            </div>
          </div>
        </div>

        {/* Status Messages & Progress Bar */}
        <div className="space-y-4 pt-4">
          {/* Dynamic status text */}
          <p className="text-sm font-mono text-green-400 min-h-6">
            {progress < 15 && '🔧 Initializing network modules...'}
            {progress >= 15 && progress < 35 && '📡 Establishing connections...'}
            {progress >= 35 && progress < 55 && '⚙️ Loading core systems...'}
            {progress >= 55 && progress < 75 && '🌐 Synchronizing data streams...'}
            {progress >= 75 && progress < 90 && '✓ Finalizing deployment...'}
            {progress >= 90 && progress < 100 && '⚡ Almost ready...'}
            {progress >= 100 && '✅ SYSTEM ONLINE'}
          </p>

          {/* Linear progress bar */}
          <div className="w-full max-w-xs mx-auto h-1 bg-gray-900/50 rounded-full overflow-hidden border border-cyan-500/30">
            <div 
              className="h-full bg-gradient-to-r from-cyan-500 via-green-400 to-blue-500 rounded-full"
              style={{
                width: `${progress}%`,
                transition: 'width 0.12s linear',
                boxShadow: '0 0 10px rgba(0, 200, 150, 0.8)'
              }}
            ></div>
          </div>

          {/* Status bars */}
          <div className="flex justify-center gap-1">
            {[0, 1, 2, 3, 4].map(i => (
              <div
                key={i}
                className="w-1.5 h-8 bg-gradient-to-t from-cyan-500 to-green-400 rounded-full"
                style={{
                  opacity: progress > i * 20 ? 1 : 0.2,
                  transition: 'opacity 0.2s ease',
                  boxShadow: progress > i * 20 ? '0 0 10px rgba(0, 200, 150, 0.8)' : 'none'
                }}
              />
            ))}
          </div>
        </div>

        {/* Footer text */}
        <div className="text-xs text-gray-500 font-mono pt-4">
          <p>▓▓▓▓▓▓▓▓▓▓ {Math.floor(progress)}% Complete ▓▓▓▓▓▓▓▓▓▓</p>
        </div>
      </div>

      {/* Corner network nodes */}
      <div className="absolute top-6 right-6 z-10">
        <div className="w-3 h-3 bg-cyan-400 rounded-full animate-pulse"></div>
        <div className="absolute w-8 h-8 border border-cyan-400/30 rounded-full" style={{animation: 'rotate-slow 3s linear infinite'}}></div>
      </div>

      <div className="absolute bottom-6 left-6 z-10">
        <div className="w-3 h-3 bg-green-400 rounded-full animate-pulse" style={{animationDelay: '0.5s'}}></div>
        <div className="absolute w-8 h-8 border border-green-400/30 rounded-full" style={{animation: 'rotate-slow 4s linear infinite reverse'}}></div>
      </div>
    </div>
  )
}