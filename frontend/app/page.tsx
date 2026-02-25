'use client'
import React, { useEffect, useRef, useState } from 'react'
import Link from 'next/link'
import { motion } from 'framer-motion'

// Neural Network Background Component
const NeuralNetwork = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext('2d')
    if (!ctx) return

    canvas.width = canvas.offsetWidth
    canvas.height = canvas.offsetHeight

    const particles: Array<{ x: number; y: number; vx: number; vy: number }> = []
    const particleCount = 50

    // Create particles
    for (let i = 0; i < particleCount; i++) {
      particles.push({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        vx: (Math.random() - 0.5) * 0.5,
        vy: (Math.random() - 0.5) * 0.5
      })
    }

    const animate = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height)
      ctx.strokeStyle = 'rgba(0, 229, 255, 0.1)'
      ctx.lineWidth = 1

      // Update and draw particles
      particles.forEach((p, i) => {
        p.x += p.vx
        p.y += p.vy

        if (p.x < 0 || p.x > canvas.width) p.vx *= -1
        if (p.y < 0 || p.y > canvas.height) p.vy *= -1

        // Draw connections
        particles.slice(i + 1).forEach(p2 => {
          const dx = p.x - p2.x
          const dy = p.y - p2.y
          const dist = Math.sqrt(dx * dx + dy * dy)

          if (dist < 150) {
            ctx.globalAlpha = 1 - dist / 150
            ctx.beginPath()
            ctx.moveTo(p.x, p.y)
            ctx.lineTo(p2.x, p2.y)
            ctx.stroke()
            ctx.globalAlpha = 1
          }
        })

        // Draw particle
        ctx.fillStyle = `rgba(0, 229, 255, ${0.5 + 0.5 * Math.sin(Date.now() / 1000 + i)})`
        ctx.beginPath()
        ctx.arc(p.x, p.y, 2, 0, Math.PI * 2)
        ctx.fill()
      })

      requestAnimationFrame(animate)
    }

    animate()
  }, [])

  return <canvas ref={canvasRef} className="absolute inset-0 opacity-30" />
}

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
      delayChildren: 0.3
    }
  }
}

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.8, ease: "easeOut" }
  }
}

const glowVariants = {
  initial: { boxShadow: '0 0 20px rgba(0, 229, 255, 0.5)' },
  animate: {
    boxShadow: [
      '0 0 20px rgba(0, 229, 255, 0.5)',
      '0 0 40px rgba(0, 229, 255, 0.8)',
      '0 0 20px rgba(0, 229, 255, 0.5)'
    ],
    transition: { duration: 3, repeat: Infinity }
  }
}

export default function Home() {
  return (
    <main className="relative bg-black text-white overflow-hidden">
      {/* Background */}
      <div className="fixed inset-0 z-0">
        <NeuralNetwork />
        <div className="absolute inset-0 bg-gradient-to-b from-black via-transparent to-black opacity-60" />
      </div>

      {/* Hero Section */}
      <section className="relative z-10 min-h-screen flex items-center justify-center px-4 sm:px-6 lg:px-8 pt-20 pb-32">
        <motion.div initial="hidden" animate="visible" variants={containerVariants}>
          <div className="max-w-5xl mx-auto w-full">
          {/* Tagline */}
          <motion.div variants={itemVariants}>
            <div className="text-center mb-8">
            <div className="inline-block px-4 py-2 rounded-full border border-cyan-500/50 bg-cyan-500/10 backdrop-blur-sm mb-6">
              <span className="text-cyan-400 font-mono text-sm">✨ TechXelarate2026</span>
            </div>
            </div>
          </motion.div>

          {/* Main Headline */}
          <motion.div variants={itemVariants}>
            <div className="mb-12 text-center">
            <h1 className="text-5xl sm:text-7xl font-black mb-6 bg-gradient-to-r from-cyan-400 via-purple-400 to-cyan-400 bg-clip-text text-transparent animate-pulse">
              6-HOUR
              <br />
              INNOVATION
              <br />
              HACKATHON
            </h1>
            <p className="text-lg sm:text-xl text-gray-300 max-w-2xl mx-auto leading-relaxed">
              Build the future with cutting-edge AI, cybersecurity, sustainability, and data intelligence solutions
            </p>
            </div>
          </motion.div>

          {/* CTA Buttons */}
          <motion.div variants={itemVariants}>
            <div className="flex gap-4 justify-center flex-wrap">
            <motion.div animate="animate" initial="initial" variants={glowVariants}>
              <Link
                href="/registration"
                className="px-8 sm:px-12 py-4 bg-gradient-to-r from-cyan-500 to-purple-500 rounded-lg font-bold text-lg hover:scale-105 transition-transform duration-300 inline-block"
              >
                🚀 REGISTER NOW
              </Link>
            </motion.div>
            <Link
              href="/checkin"
              className="px-8 sm:px-12 py-4 border-2 border-cyan-500 rounded-lg font-bold text-lg hover:bg-cyan-500/10 transition-all duration-300 inline-block"
            >
              ✅ CHECK IN
            </Link>
            </div>
          </motion.div>
          </div>
        </motion.div>
      </section>

      {/* Domains Section */}
      <section className="relative z-10 py-24 px-4 sm:px-6 lg:px-8">
        <div className="max-w-6xl mx-auto">
          <motion.div
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8 }}
          >
            <div>
            <h2 className="text-4xl font-black text-center mb-4 bg-gradient-to-r from-cyan-400 to-purple-400 bg-clip-text text-transparent">
              🎯 COMPETITION TRACKS
            </h2>
            <p className="text-center text-gray-400 mb-16 max-w-2xl mx-auto">
              Choose your specialty and compete in your domain of expertise
            </p>
            </div>
          </motion.div>

          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            variants={containerVariants}
          >
            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[
              { icon: '🤖', title: 'Explainable AI', desc: 'Build interpretable AI systems' },
              { icon: '🔒', title: 'Cybersecurity', desc: 'Secure the digital frontier' },
              { icon: '🌱', title: 'Sustainability', desc: 'Tech for a green future' },
              { icon: '📊', title: 'Data Intelligence', desc: 'Unlock insights from data' }
            ].map((domain, i) => (
              <motion.div
                key={i}
                variants={itemVariants}
              >
                <div className="group relative p-6 rounded-xl border border-cyan-500/30 bg-gradient-to-br from-cyan-500/10 to-purple-500/10 backdrop-blur-sm hover:border-cyan-400 transition-all duration-300 overflow-hidden">
                <div className="absolute inset-0 bg-gradient-to-r from-cyan-500/0 to-purple-500/0 group-hover:from-cyan-500/10 group-hover:to-purple-500/10 transition-all duration-300" />
                <div className="relative z-10">
                  <div className="text-4xl mb-3">{domain.icon}</div>
                  <h3 className="text-xl font-bold text-cyan-300 mb-2">{domain.title}</h3>
                  <p className="text-gray-400 text-sm">{domain.desc}</p>
                </div>
                </div>
              </motion.div>
            ))}
            </div>
          </motion.div>
        </div>
      </section>

      {/* Timeline Section */}
      <section className="relative z-10 py-24 px-4 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto">
          <motion.div
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8 }}
          >
            <div>
            <h2 className="text-4xl font-black text-center mb-4 bg-gradient-to-r from-purple-400 to-cyan-400 bg-clip-text text-transparent">
              ⏰ EVENT TIMELINE
            </h2>
            </div>
          </motion.div>

          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            variants={containerVariants}
          >
            <div className="space-y-8 mt-16">
            {[
              { time: '09:00 AM', event: 'Registration Attendance', icon: '📝' },
              { time: '09:30 AM', event: 'Opening Ceremony ', icon: '🎤' },
              { time: '10:00 AM', event: 'Hackathon Starts', icon: '🚀' },
              { time: '01:00 PM', event: 'Lunch Break', icon: '🍽️' },
              { time: '04:00 PM', event: 'Project Submissions', icon: '📤' },
              { time: '04:45 PM', event: 'Judging & Presentations', icon: '🏆' }
            ].map((item, i) => (
              <motion.div key={i} variants={itemVariants}>
                <div className="flex gap-6 items-start">
                <div className="flex-shrink-0">
                  <div className="flex items-center justify-center h-12 w-12 rounded-full bg-gradient-to-r from-cyan-500 to-purple-500">
                    <span className="text-lg">{item.icon}</span>
                  </div>
                </div>
                <div className="flex-1 border-l-2 border-cyan-500/30 pl-6">
                  <p className="text-cyan-400 font-mono font-bold">{item.time}</p>
                  <p className="text-gray-300 mt-1">{item.event}</p>
                </div>
                </div>
              </motion.div>
            ))}
            </div>
          </motion.div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="relative z-10 py-24 px-4 sm:px-6 lg:px-8">
        <div className="max-w-5xl mx-auto">
          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            variants={containerVariants}
          >
            <div className="grid md:grid-cols-3 gap-8">
            {[
              { stat: '6', label: 'Hours of Innovation', icon: '⏱️' },
              { stat: '4', label: 'Competition Tracks', icon: '🎯' },
              { stat: '$30K', label: 'Prize Pool', icon: '💰' }
            ].map((item, i) => (
              <motion.div
                key={i}
                variants={itemVariants}
              >
                <div className="text-center p-8 rounded-xl border border-purple-500/30 bg-gradient-to-br from-purple-500/10 to-cyan-500/10 backdrop-blur-sm">
                <div className="text-5xl mb-4">{item.icon}</div>
                <p className="text-4xl font-black bg-gradient-to-r from-cyan-400 to-purple-400 bg-clip-text text-transparent mb-2">
                  {item.stat}
                </p>
                <p className="text-gray-400">{item.label}</p>
                </div>
              </motion.div>
            ))}
            </div>
          </motion.div>
        </div>
      </section>

      {/* Footer CTA */}
      <section className="relative z-10 py-24 px-4 sm:px-6 lg:px-8 border-t border-cyan-500/20">
        <div className="max-w-3xl mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8 }}
          >
            <div>
            <h2 className="text-4xl font-black mb-6 bg-gradient-to-r from-cyan-400 to-purple-400 bg-clip-text text-transparent">
              Ready to Innovate?
            </h2>
            <p className="text-gray-300 mb-8 text-lg">
              Join the most exciting hackathon event. Build something extraordinary.
            </p>
            <motion.div animate="animate" initial="initial" variants={glowVariants}>
              <Link
                href="/registration"
                className="inline-block px-12 py-4 bg-gradient-to-r from-cyan-500 to-purple-500 rounded-lg font-bold text-lg hover:scale-105 transition-transform duration-300"
              >
                🎉 REGISTER YOUR TEAM
              </Link>
            </motion.div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Footer */}
      <footer className="relative z-10 border-t border-cyan-500/20 py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-6xl mx-auto">
          <div className="grid md:grid-cols-4 gap-8 mb-12">
            <div>
              <h3 className="text-cyan-400 font-bold mb-4">🌐 HACKATHON</h3>
              <p className="text-gray-400 text-sm">Innovate. Build. Win.</p>
            </div>
            <div>
              <h4 className="text-gray-300 font-bold mb-4">Quick Links</h4>
              <ul className="space-y-2 text-gray-400 text-sm">
                <li>
  <a
    href="https://lbrce.ac.in/"
    target="_blank"
    rel="noopener noreferrer"
    className="hover:text-cyan-400 transition"
  >
    About
  </a>
</li>

<li>
  <a
    href="https://www.instagram.com/lbrce_1?igsh=MXFweHBwcW5rdWt4Zw=="
    target="_blank"
    rel="noopener noreferrer"
    className="hover:text-cyan-400 transition"
  >
    Instagram
  </a>
</li>

<li>
  <a
    href="https://www.facebook.com/share/1CyEmqbaaP/"
    target="_blank"
    rel="noopener noreferrer"
    className="hover:text-cyan-400 transition"
  >
    Facebook
  </a>
</li>

<li>
  <a
    href="https://x.com/lbrce1"
    target="_blank"
    rel="noopener noreferrer"
    className="hover:text-cyan-400 transition"
  >
    Twitter
  </a>
</li>

<li>
  <a
    href="https://lbrce.ac.in/quicklinks_pages/contact.php"
    target="_blank"
    rel="noopener noreferrer"
    className="hover:text-cyan-400 transition"
  >
    Contact
  </a>
</li>
              </ul>
            </div>
            <div>
              <h4 className="text-gray-300 font-bold mb-4">Contact</h4>
              <p className="text-gray-400 text-sm">Email: hackathon@cse.edu</p>
              <p className="text-gray-400 text-sm">Phone: +91-XXX-XXXX</p>
            </div>
            <div>
              <h4 className="text-gray-300 font-bold mb-4">Follow Us</h4>
              <div className="flex gap-3">
                <a href="#" className="w-10 h-10 rounded-full bg-cyan-500/20 flex items-center justify-center hover:bg-cyan-500/40 transition">
                  f
                </a>
                <a href="#" className="w-10 h-10 rounded-full bg-cyan-500/20 flex items-center justify-center hover:bg-cyan-500/40 transition">
                  𝕏
                </a>
                <a href="#" className="w-10 h-10 rounded-full bg-cyan-500/20 flex items-center justify-center hover:bg-cyan-500/40 transition">
                  📱
                </a>
              </div>
            </div>
          </div>
          <div className="border-t border-cyan-500/20 pt-8 text-center text-gray-400 text-sm">
            <p>© 2026 CSE AI & ML Hackathon. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </main>
  )
}
