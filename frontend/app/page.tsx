  'use client'
  import React, { useEffect, useRef, useState } from 'react'
  import Link from 'next/link'
  import { motion, useViewportScroll, useTransform } from 'framer-motion'
  import BrochurePopup from "./components/BrochurePopup"
  




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

  // STARFIELD BACKGROUND WITH 3D PARALLAX
  const StarField = () => {
    const canvasRef = useRef<HTMLCanvasElement>(null)
    const { scrollY } = useViewportScroll();
    const y = useTransform(scrollY, [0, 2000], [0, -200]);
    useEffect(() => {
      const canvas = canvasRef.current
      if (!canvas) return
      const ctx = canvas.getContext('2d')
      if (!ctx) return
      canvas.width = canvas.offsetWidth
      canvas.height = canvas.offsetHeight

      const stars: Array<{x:number,y:number,z:number,brightness:number}> = []
      const count = 200
      for(let i=0;i<count;i++){
        stars.push({
          x:Math.random()*canvas.width,
          y:Math.random()*canvas.height,
          z:Math.random()*canvas.width,
          brightness: Math.random() * 0.5 + 0.5
        })
      }

      const animate = () => {
        ctx.clearRect(0,0,canvas.width,canvas.height)
        // Background glow
        const gradient = ctx.createRadialGradient(canvas.width/2, canvas.height/2, 0, canvas.width/2, canvas.height/2, canvas.width)
        gradient.addColorStop(0, 'rgba(6,182,212,0.03)')
        gradient.addColorStop(1, 'rgba(0,0,0,0)')
        ctx.fillStyle = gradient
        ctx.fillRect(0, 0, canvas.width, canvas.height)
        
        stars.forEach((s, i) => {
          s.z -= 2
          if(s.z<=0){
            s.z = canvas.width
            s.x = Math.random()*canvas.width
            s.y = Math.random()*canvas.height
            s.brightness = Math.random() * 0.5 + 0.5
          }
          const sx = (s.x - canvas.width/2) * (canvas.width / s.z) + canvas.width/2
          const sy = (s.y - canvas.height/2) * (canvas.width / s.z) + canvas.height/2
          const rad = Math.max((canvas.width / s.z) * 1.5, 0.5)
          
          // Vary star colors based on distance
          const hue = s.z / canvas.width > 0.5 ? 180 : 220 + Math.sin(i) * 20
          const brightness = s.brightness * (1 - s.z / canvas.width)
          ctx.fillStyle = `hsla(${hue}, 100%, ${50 + brightness * 30}%, ${0.4 + brightness * 0.6})`
          ctx.beginPath()
          ctx.arc(sx, sy, rad, 0, Math.PI*2)
          ctx.fill()
          
          // Add glow to closer stars
          if(rad > 1) {
            ctx.fillStyle = `hsla(180, 100%, 60%, ${0.1 * brightness})`
            ctx.beginPath()
            ctx.arc(sx, sy, rad * 3, 0, Math.PI*2)
            ctx.fill()
          }
        })
        requestAnimationFrame(animate)
      }
      animate()
    },[])
    return (
      <motion.div style={{ y }}>
        <div className="absolute inset-0 opacity-20">
          <canvas ref={canvasRef} className="w-full h-full" />
        </div>
      </motion.div>
    )
  }

  // GLOWING PARTICLES BACKGROUND
  const GlowingParticles = () => {
    const canvasRef = useRef<HTMLCanvasElement>(null)
    
    useEffect(() => {
      const canvas = canvasRef.current
      if (!canvas) return
      const ctx = canvas.getContext('2d')
      if (!ctx) return
      canvas.width = canvas.offsetWidth
      canvas.height = canvas.offsetHeight

      const particles: Array<{x:number,y:number,vx:number,vy:number,size:number,opacity:number,color:string}> = []
      const particleCount = 40
      const colors = ['rgba(6,182,212,', 'rgba(99,102,241,', 'rgba(168,85,247,']
      
      for(let i=0;i<particleCount;i++){
        const color = colors[Math.floor(Math.random() * colors.length)]
        particles.push({
          x: Math.random() * canvas.width,
          y: Math.random() * canvas.height,
          vx: (Math.random() - 0.5) * 0.3,
          vy: (Math.random() - 0.5) * 0.3,
          size: Math.random() * 2 + 1,
          opacity: Math.random() * 0.5 + 0.3,
          color: color
        })
      }

      const animate = () => {
        ctx.clearRect(0, 0, canvas.width, canvas.height)
        
        particles.forEach((p, i) => {
          p.x += p.vx
          p.y += p.vy
          p.opacity += (Math.random() - 0.5) * 0.02
          p.opacity = Math.max(0.1, Math.min(0.7, p.opacity))
          
          if(p.x < 0 || p.x > canvas.width) p.vx *= -1
          if(p.y < 0 || p.y > canvas.height) p.vy *= -1
          
          // Draw glow
          const glowGradient = ctx.createRadialGradient(p.x, p.y, 0, p.x, p.y, p.size * 4)
          const color = p.color
          glowGradient.addColorStop(0, color + p.opacity * 0.8 + ')')
          glowGradient.addColorStop(1, color + '0)')
          ctx.fillStyle = glowGradient
          ctx.fillRect(p.x - p.size * 4, p.y - p.size * 4, p.size * 8, p.size * 8)
          
          // Draw core
          ctx.fillStyle = color + p.opacity + ')'
          ctx.beginPath()
          ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2)
          ctx.fill()
        })
        
        requestAnimationFrame(animate)
      }
      animate()
    }, [])
    
    return <canvas ref={canvasRef} className="absolute inset-0 opacity-25" />
  }

  // Navbar with mobile toggle
  const Navbar = () => {
    const [open, setOpen] = useState(false)
    const links = ['About','Coordinators','Register','Location']
    return (
      <nav className="fixed top-0 left-0 right-0 z-20 backdrop-blur-sm bg-black/30 px-6 py-4">
        <div className="flex items-center justify-between">
          <img src="/logo.png" alt="College Logo" className="h-16 w-auto" />
          <div className="hidden md:flex space-x-6">
            {links.map(item => (
              item === 'Register' ? (
                <Link key={item} href="/registration" className="nav-link">
                  {item}
                </Link>
              ) : (
                <a key={item} href={`#${item.toLowerCase()}`} className="nav-link">
                  {item}
                </a>
              )
            ))}
          </div>
          <div className="md:hidden">
            <button onClick={()=>setOpen(!open)} aria-label="Menu">
              <div className={`hamburger ${open?'open':''}`}>
                <span></span><span></span><span></span>
              </div>
            </button>
          </div>
        </div>
        {open && (
          <div className="md:hidden mt-4 flex flex-col space-y-2">
            {links.map(item => (
              item === 'Register' ? (
                <Link key={item} href="/registration" className="nav-link block">
                  {item}
                </Link>
              ) : (
                <a key={item} href={`#${item.toLowerCase()}`} className="nav-link block">
                  {item}
                </a>
              )
            ))}
          </div>
        )}
      </nav>
    )
  }

  // Event Details Card - Glassmorphic
  const EventDetailsCard = () => (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.8, delay: 0.6 }}
    >
      <div className="hero-event-card max-w-2xl mx-auto">
        <div className="hero-event-card-content">
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6, delay: 0.7 }}
          >
            <div className="hero-event-item">
              <span className="text-3xl drop-shadow-lg">📅</span>
              <span className="text-lg text-gray-200">Date: <span className="text-cyan-300 font-bold">14 March 2026</span></span>
            </div>
          </motion.div>
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6, delay: 0.8 }}
          >
            <div className="hero-event-item mt-4">
              <span className="text-3xl drop-shadow-lg">⏰</span>
              <span className="text-lg text-gray-200">Registration Ends: <span className="text-cyan-300 font-bold">11 March 2026</span></span>
            </div>
          </motion.div>
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6, delay: 0.9 }}
          >
            <div className="hero-event-item mt-4">
              <span className="text-3xl drop-shadow-lg">📍</span>
              <span className="text-lg text-gray-200"><span className="text-cyan-300 font-bold">Lakireddy Bali Reddy College,</span> Mylavaram</span>
            </div>
          </motion.div>
        </div>
      </div>
    </motion.div>
  )

  // Countdown timer component
  const Countdown = () => {
    const [timeLeft, setTimeLeft] = useState({ days: 0, hours: 0, minutes: 0, seconds: 0 })

    useEffect(() => {
      const target = new Date('2026-03-14T00:00:00')
      const interval = setInterval(() => {
        const now = new Date()
        const diff = target.getTime() - now.getTime()
        if (diff <= 0) {
          clearInterval(interval)
          return
        }
        const days = Math.floor(diff / (1000 * 60 * 60 * 24))
        const hours = Math.floor((diff / (1000 * 60 * 60)) % 24)
        const minutes = Math.floor((diff / (1000 * 60)) % 60)
        const seconds = Math.floor((diff / 1000) % 60)
        setTimeLeft({ days, hours, minutes, seconds })
      }, 1000)
      return () => clearInterval(interval)
    }, [])

    return (
      <div className="flex gap-4 justify-center flex-wrap mt-6">
        {Object.entries(timeLeft).map(([unit, val]) => (
          <div key={unit} className="countdown-box">
            <p className="text-2xl font-bold animate-pulse">{val}</p>
            <p className="text-xs text-gray-300 uppercase">{unit}</p>
          </div>
        ))}
      </div>
    )
  }

  // Scrolling marquee component
  const Marquee = () => {
    const items = [
      'TECHXELERATE 2026',
      'INNOVATE',
      'BUILD',
      'CREATE',
      'AI POWERED',
      'HACK THE FUTURE',
      'NEXT GEN TECHNOLOGY',
      '6 HOURS INNOVATION'
    ]
    return (
      <div className="relative overflow-hidden py-4">
        <div className="whitespace-nowrap animate-marquee flex gap-8 text-lg font-bold text-cyan-400">
          {items.map((i, idx) => (
            <span key={idx}>{i}</span>
          ))}
          {items.map((i, idx) => (
            <span key={'dup' + idx}>{i}</span>
          ))}
        </div>
      </div>
    )
  }

  export default function Home() {
  

    return (
      <main className="relative bg-black text-white overflow-hidden">
        <BrochurePopup />
        
        {/* Background */}
        <div className="fixed inset-0 z-0">
          <NeuralNetwork />
          <GlowingParticles />
          <StarField />
          <div className="absolute inset-0 grid-overlay" />
          <div className="absolute inset-0 bg-gradient-to-b from-black/80 via-transparent to-black opacity-70" />
          <div className="absolute inset-0 bg-gradient-to-r from-transparent via-cyan-500/5 to-transparent opacity-30 pointer-events-none" />
        </div>

        {/* Hero Section */}
        <Navbar />
        <section className="relative z-10 min-h-screen flex flex-col items-center justify-center px-4 sm:px-6 lg:px-8 pt-20 pb-32">
          <motion.div initial="hidden" animate="visible" variants={containerVariants}>
            {/* College Info */}
            <motion.div variants={itemVariants}>
              <div className="text-center mb-8">
              </div>
            </motion.div>

            {/* College header */}
            <motion.div variants={itemVariants}>
              <div className="text-center mb-12">
                <h2 className="hero-college-header text-2xl sm:text-3xl md:text-4xl mb-2">
                  LAKIREDDY BALI REDDY COLLEGE<br />OF ENGINEERING
                </h2>
                <p className="hero-college-subtext text-lg sm:text-xl md:text-2xl mb-1">MYLAVARAM</p>
                <p className="hero-college-dept text-xs sm:text-sm md:text-base">
                  Department of Computer Science & Engineering (AI AND ML)<br />
                  Accredited by NAAC & NBA | Approved by AICTE & Affiliated to JNTUK
                </p>
              </div>
            </motion.div>

            {/* Hackathon title */}
            <motion.div variants={itemVariants}>
              <div className="mb-12 text-center">
                <h1 className="hero-title text-[26px] sm:text-4xl md:text-5xl lg:text-6xl font-black mb-4 leading-tight tracking-wide">
                  TECHXELERATE<br />2026
                </h1>
              </div>
            </motion.div>

            {/* Event Details and countdown */}
            <motion.div variants={itemVariants}>
              <EventDetailsCard />
              <Countdown />
            </motion.div>

            {/* Register button */}
            <motion.div variants={itemVariants}>
              <div className="mt-10 flex gap-4 justify-center">
                <motion.div animate="animate" initial="initial" variants={glowVariants}>
                  <Link
                    href="/registration"
                    className="px-8 py-4 bg-gradient-to-r from-cyan-500 to-purple-500 rounded-lg font-bold text-lg hover:scale-105 transition-transform duration-300 inline-block"
                  >
                    🚀 REGISTER NOW
                  </Link>
                </motion.div>
              </div>
            </motion.div>
          </motion.div>
        </section>

        {/* Marquee banner */}
        <Marquee />

        {/* About Section */}
        <section id="about" className="relative z-10 py-24 px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8 }}
          >
            <h2 className="text-4xl font-black text-center mb-6 gradient-text">About TECHXELERATE</h2>
            <p className="max-w-3xl mx-auto text-center text-gray-300 leading-relaxed">
              TECHXELERATE 2026 is a national level hackathon organized by the Department of Computer Science and Engineering (AI AND ML) at Lakireddy Bali Reddy College of Engineering, Mylavaram. The event encourages innovators and developers to collaborate, build solutions, and compete while solving real-world problems using emerging technologies.
            </p>
          </motion.div>
        </section>

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
                🎯 23 COMPETITION THEMES
              </h2>
              <p className="text-center text-gray-400 mb-16 max-w-2xl mx-auto">
                Explore 23 diverse domains. Choose your passion and compete in your specialty
              </p>
              </div>
            </motion.div>

            <motion.div
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true }}
              variants={containerVariants}
            >
              <div className="grid sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4">
              {[
                { icon: '🌾', title: 'Agriculture', desc: 'Tech solutions for farming' },
                { icon: '🌊', title: 'Ocean Technology', desc: 'Marine innovations' },
                { icon: '👩‍🦰', title: 'Women Safety', desc: 'Protect and empower' },
                { icon: '🤖', title: 'Smart Automation', desc: 'Automate intelligently' },
                { icon: '🌲', title: 'Forest/Wildlife', desc: 'Conservation technology' },
                { icon: '🧬', title: 'Life Science', desc: 'Biotech innovations' },
                { icon: '🥗', title: 'Food Tech', desc: 'Future of food' },
                { icon: '⚕️', title: 'Healthcare/Bio', desc: 'Medical breakthroughs' },
                { icon: '❤️', title: 'Social Cause', desc: 'Help communities thrive' },
                { icon: '🏘️', title: 'Rural Dev', desc: 'Transform villages' },
                { icon: '📡', title: 'IoT', desc: 'Connected devices' },
                { icon: '🤖', title: 'AI', desc: 'Artificial intelligence' },
                { icon: '🧠', title: 'ML', desc: 'Machine learning' },
                { icon: '📊', title: 'Data Science', desc: 'Data-driven solutions' },
                { icon: '♻️', title: 'Waste Management', desc: 'Circular economy' },
                { icon: '🏛️', title: 'Heritage/Culture', desc: 'Preserve our past' },
                { icon: '🚁', title: 'Robotics/Drones', desc: 'Future automation' },
                { icon: '🎮', title: 'Toys/Games', desc: 'Interactive entertainment' },
                { icon: '✈️', title: 'Tourism', desc: 'Travel tech solutions' },
                { icon: '🌿', title: 'Green Tech', desc: 'Sustainable energy' },
                { icon: '📚', title: 'Education', desc: 'Learning innovations' },
                { icon: '🚨', title: 'Disaster Management', desc: 'Crisis response' },
                { icon: '🌍', title: 'Environment/Climate', desc: 'Combat climate change' }
              ].map((domain, i) => (
                <motion.div
                  key={i}
                  variants={itemVariants}
                >
                  <div className="group relative p-4 rounded-lg border border-cyan-500/30 bg-gradient-to-br from-cyan-500/10 to-purple-500/10 backdrop-blur-sm hover:border-cyan-400 transition-all duration-300 overflow-hidden">
                    <div className="absolute inset-0 bg-gradient-to-r from-cyan-500/0 to-purple-500/0 group-hover:from-cyan-500/10 group-hover:to-purple-500/10 transition-all duration-300" />
                    <div className="relative z-10">
                      <div className="text-3xl mb-2">{domain.icon}</div>
                      <h3 className="text-sm font-bold text-cyan-300 mb-1">{domain.title}</h3>
                      <p className="text-gray-400 text-xs">{domain.desc}</p>
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
                { stat: '23', label: 'Competition Themes', icon: '🎯' },
                { stat: '🎁', label: 'Mystery Prize Pool', icon: '🏆' }
              ].map((item, i) => (
                <motion.div
                  key={i}
                  variants={itemVariants}
                >
                  <div className="text-center p-8 rounded-xl border border-purple-500/30 bg-gradient-to-br from-purple-500/10 to-cyan-500/10 backdrop-blur-sm hover:border-purple-400 transition-all duration-300">
                  <div className="text-5xl mb-4">{item.icon}</div>
                  {i === 2 ? (
                    <div>
                      <p className="text-sm text-purple-300 font-mono mb-3 italic">"The best rewards cannot be predicted, only exceeded"</p>
                      <p className="text-2xl font-black bg-gradient-to-r from-yellow-400 to-orange-400 bg-clip-text text-transparent mb-2">
                        UNLIMITED SURPRISES
                      </p>
                      <p className="text-gray-400 text-xs">🎊 Reveal the possibilities 🎊</p>
                    </div>
                  ) : (
                    <>
                      <p className="text-4xl font-black bg-gradient-to-r from-cyan-400 to-purple-400 bg-clip-text text-transparent mb-2">
                        {item.stat}
                      </p>
                      <p className="text-gray-400">{item.label}</p>
                    </>
                  )}
                  </div>
                </motion.div>
              ))}
              </div>
            </motion.div>
          </div>
        </section>

        {/* Coordinators Section */}
        <section id="coordinators" className="relative z-10 py-24 px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8 }}
          >
            <h2 className="text-4xl font-black text-center mb-12 gradient-text">Student Coordinators</h2>
          </motion.div>
          <div className="grid sm:grid-cols-2 md:grid-cols-4 gap-6">
            {[
              {name:'B. Rohith Mani',phone:'7036636671'},
              {name:'Shaik Sazid Vali',phone:'7396279327'},
              {name:'Sreeram',phone:'8977012479'},
              {name:'Keerthan',phone:'8309209791'},
               {name:'Teja Sai',phone:'9290524027'}
            ].map((c,i)=>(
              <a key={i} href={`tel:+91${c.phone}`} className="coord-card flex flex-col items-center text-center">
                <div className="h-20 w-20 rounded-full bg-gray-800 flex items-center justify-center text-3xl mb-4">👤</div>
                <p className="font-bold text-cyan-300 mb-1">{c.name}</p>
                <p className="text-gray-400 text-sm">+91 {c.phone}</p>
              </a>
            ))}
          </div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8 }}
          >
            <div className="mt-16">
              <h2 className="text-4xl font-black text-center mb-12 gradient-text">Faculty Coordinators</h2>
            </div>
          </motion.div>
          <div className="grid sm:grid-cols-2 md:grid-cols-4 gap-6">
            {[
              {name:'Dr I. Murali Krishna',role:'Professor'},
              {name:'Mr.Lalam Narendra',role:'Assistant Professor'}
            ].map((f,i)=>(
              <div key={i} className="coord-card flex flex-col items-center text-center">
                <div className="h-20 w-20 rounded-full bg-gray-800 flex items-center justify-center text-3xl mb-4">👨‍🏫</div>
                <p className="font-bold text-cyan-300 mb-1">{f.name}</p>
                <p className="text-gray-400 text-sm italic">{f.role}</p>
              </div>
            ))}
          </div>
        </section>

        {/* Location Section */}
        <section id="location" className="relative z-10 py-24 px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8 }}
          >
            <h2 className="text-4xl font-black text-center mb-12 gradient-text">Event Location</h2>
          </motion.div>
          <div className="max-w-3xl mx-auto">
            <p className="text-center text-gray-300 mb-4">
              Lakireddy Bali Reddy College of Engineering<br />Mylavaram, Andhra Pradesh
            </p>
            <div className="w-full h-64 md:h-96 mb-6">
              <iframe
                src="https://www.google.com/maps?q=Lakireddy+Bali+Reddy+College+of+Engineering&output=embed"
                className="w-full h-full rounded-lg border-2 border-cyan-500/30"
                allowFullScreen
                loading="lazy"
              />
            </div>
            <div className="text-center">
              <a
                href="https://maps.google.com/?q=Lakireddy+Bali+Reddy+College+of+Engineering"
                target="_blank" rel="noopener noreferrer"
                className="inline-block px-8 py-3 bg-gradient-to-r from-cyan-500 to-purple-500 rounded-lg font-bold text-lg hover:shadow-[0_0_20px_rgba(6,182,212,0.8)] transition"
              >
                Get Directions
              </a>
            </div>
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
        <footer className="relative z-10 footer-glass">
          <div className="max-w-6xl mx-auto text-center">
            <h3 className="text-2xl font-bold mb-4 gradient-text">TECHXELERATE 2026</h3>
            <p className="text-gray-400 mb-6">Lakireddy Bali Reddy College of Engineering<br />Mylavaram, Andhra Pradesh</p>
            {/* College Details Block */}
            <div className="mb-8 pb-8 border-b border-cyan-500/20">
              <div className="grid md:grid-cols-2 gap-8 max-w-2xl mx-auto text-left md:text-center">
                {/* College Info */}
                <div>
                  <p className="text-cyan-300 font-bold text-sm mb-2">🏛️ COLLEGE</p>
                  <p className="text-gray-300 text-xs leading-relaxed">
                    Lakireddy Bali Reddy College of Engineering<br />
                    <span className="text-cyan-400">(AUTONOMOUS)</span><br />
                    Department of Computer Science & Engineering<br />
                    <span className="text-purple-400">(AI AND ML)</span>
                  </p>
                </div>
                
                {/* Accreditation & Location */}
                <div>
                  <p className="text-cyan-300 font-bold text-sm mb-2">✓ ACCREDITATION</p>
                  <p className="text-gray-300 text-xs leading-relaxed">
                    <span className="text-green-400">✓ NAAC Accredited</span><br />
                    <span className="text-green-400">✓ NBA Accredited</span><br />
                    <span className="text-green-400">✓ AICTE Approved</span><br />
                    <span className="text-green-400">✓ JNTUK Affiliated</span>
                  </p>
                </div>
              </div>
              
              {/* Address & Contact */}
              <div className="max-w-2xl mx-auto mt-6 text-center border-t border-cyan-500/10 pt-4">
                <p className="text-gray-400 text-xs mb-3">
                  📍 Mylavaram, Andhra Pradesh - India<br />
                  📧 lbrcehackcsm@gmail.com
                </p>
              </div>
            </div>
            
            {/* Social Media Links */}
            <div className="mb-6 pb-6 border-t border-cyan-500/20 pt-6">
              <p className="text-cyan-300 font-bold mb-4">Follow Us</p>
              <div className="social-links">
                <a href="https://www.instagram.com/lbrce_1?igsh=MXFweHBwcW5rdWt4Zw==" target="_blank" rel="noopener noreferrer" className="social-link" title="Instagram">
                  📸
                </a>
                <a href="https://www.facebook.com/share/1CyEmqbaaP/" target="_blank" rel="noopener noreferrer" className="social-link" title="Facebook">
                  f
                </a>
                <a href="https://lbrce.ac.in/quicklinks_pages/contact.php" target="_blank" rel="noopener noreferrer" className="social-link" title="LinkedIn">
                  📞
                </a>
                <a href="https://x.com/lbrce1" target="_blank" rel="noopener noreferrer" className="social-link" title="Twitter">
                  𝕏
                </a>
              </div>
            </div>
            
            <p className="text-gray-500 text-sm">© 2026 TECHXELERATE. All rights reserved.</p>
          </div>
        </footer>
      </main>
    )
  }
