"use client"
import React, { useState } from 'react'

import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import * as z from 'zod'

const schema = z.object({
  team_name: z.string().min(2, 'Team name required'),
  leader_name: z.string().min(2, 'Leader name required'),
  leader_email: z.string().email('Valid email required'),
  leader_phone: z.string().min(10, 'Phone required'),
  college_name: z.string().min(2, 'College name required'),
  year: z.string().min(1, 'Select year'),
  domain: z.string().min(1, 'Select domain'),
  members: z.array(z.object({
    name: z.string().min(2, 'Name required'),
    email: z.string().email('Valid email'),
    phone: z.string().min(10, 'Phone required')
  })).min(0).max(2, 'Maximum 2 additional members (3 total including leader)'),
  terms_accepted: z.boolean().refine(v => v === true, 'Accept terms'),
})

type FormData = z.infer<typeof schema>


export default function Registration() {
  const { register, handleSubmit, formState: { errors, isSubmitting }, watch, setValue } = useForm<FormData>({
    resolver: zodResolver(schema),
    mode: 'onBlur',
    defaultValues: {
      members: []
    }
  })

  const members = watch('members')
  const [showTerms, setShowTerms] = useState(false)

  function formatServerError(j: any) {
    if (!j) return ''
    if (typeof j === 'string') return j
    if (typeof j.detail === 'string') return j.detail
    // pydantic/zod style errors
    if (Array.isArray(j)) return j.map(x => typeof x === 'string' ? x : JSON.stringify(x)).join('; ')
    if (typeof j === 'object') {
      if (j.message) return j.message
      try {
        return JSON.stringify(j)
      } catch (e) {
        return String(j)
      }
    }
    return String(j)
  }

  const [otpOpen, setOtpOpen] = useState(false)
  const [otpEmail, setOtpEmail] = useState('')
  const [otp, setOtp] = useState('')
  const [loading, setLoading] = useState(false)
  const [registered, setRegistered] = useState<any>(null)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  const addMember = () => {
    if (members.length < 2) {
      setValue('members', [...members, { name: '', email: '', phone: '' }])
    } else {
      setError('❌ Maximum 2 additional members allowed (3 total including leader)')
    }
  }

  const removeMember = (index: number) => {
    if (members.length > 1) {
      setValue('members', members.filter((_, i) => i !== index))
    } else {
      setError('❌ At least 1 team member is required')
    }
  }



  const onSubmit = async (data: FormData) => {
    setError('')
    setSuccess('')
    setLoading(true)
    setOtpEmail(data.leader_email)

    try {
      // Prepare JSON payload for simple registration
const payloadMembers = [
          // include leader at top so backend always gets a leader record
          {
            name: data.leader_name,
            email: data.leader_email,
            phone: data.leader_phone,
            is_team_leader: true
          },
          ...data.members.map((m) => ({
            name: m.name,
            email: m.email,
            phone: m.phone,
            is_team_leader: false
          }))
        ]

        const payload = {
          team_name: data.team_name,
          leader_name: data.leader_name,
          leader_email: data.leader_email,
          leader_phone: data.leader_phone,
          college_name: data.college_name,
          year: data.year,
          domain: data.domain,
          team_members: payloadMembers,
          terms_accepted: data.terms_accepted
        }

      const res = await fetch('http://localhost:8000/api/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      })

      if (res.ok) {
        const j = await res.json()
        setError('')
        
        if (j && j.otp) {
          setSuccess(`🔐 OTP (Dev Mode): ${j.otp} - Check console logs or use this OTP for testing`)
          console.log('DEV MODE OTP:', j.otp)
          console.warn('⚠️ Development mode active. OTP returned in response. Fix email configuration for production.')
        } else if (j && j.warning) {
          setSuccess(`⚠️ ${j.message}. Check email configuration.`)
        } else {
          setSuccess(`✅ OTP sent to ${data.leader_email}. Check your inbox (including spam folder) for the 6-digit code.`)
        }
        setOtpOpen(true)
      } else {
        const j = await res.json()
        setError(formatServerError(j) || 'Registration failed')
      }
    } catch (e: any) {
      setError('Network error: unable to connect to server. Check if backend is running on http://localhost:8000')
    } finally {
      setLoading(false)
    }
  }


  const verifyOtp = async () => {
    if (!otp || otp.length !== 6) {
      setError('Enter 6-digit OTP')
      return
    }

    setLoading(true)
    setError('')

    try {
      const res = await fetch('http://localhost:8000/api/verify-otp', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ leader_email: otpEmail, otp: otp })
      })

      if (res.ok) {
        const j = await res.json()
        setRegistered(j)
        setOtpOpen(false)
        setSuccess('Registration successful!')
      } else {
        const j = await res.json()
        setError(formatServerError(j) || 'OTP verification failed')
      }
    } catch (e: any) {
      setError('Network error during verification')
    } finally {
      setLoading(false)
    }
  }

  if (registered) {
    return (
      <main className="min-h-screen bg-black text-white flex items-center justify-center p-8 relative">
        <div className="absolute inset-0 opacity-10">
          <div className="w-full h-full" style={{
            backgroundImage: 'linear-gradient(0deg, transparent 24%, rgba(0, 229, 255, 0.1) 25%, rgba(0, 229, 255, 0.1) 26%, transparent 27%, transparent 74%, rgba(0, 229, 255, 0.1) 75%, rgba(0, 229, 255, 0.1) 76%, transparent 77%, transparent), linear-gradient(90deg, transparent 24%, rgba(0, 229, 255, 0.1) 25%, rgba(0, 229, 255, 0.1) 26%, transparent 27%, transparent 74%, rgba(0, 229, 255, 0.1) 75%, rgba(0, 229, 255, 0.1) 76%, transparent 77%, transparent)',
            backgroundSize: '60px 60px'
          }}></div>
        </div>
        <div className="max-w-2xl w-full relative z-10">
          <div className="border-2 border-green-500/50 rounded-xl p-8 bg-green-500/5 backdrop-blur-sm">
            <div className="text-center space-y-6">
              <div className="text-6xl animate-pulse">✅</div>
              <h2 className="text-4xl font-black text-green-400">REGISTRATION COMPLETE</h2>
              <div className="space-y-3 text-lg">
                <p className="text-gray-300">Your team has been registered successfully</p>
                <div className="p-4 bg-gray-900/50 border border-green-500/30 rounded-lg">
                  <p className="text-xs text-gray-500 mb-1">TEAM ID</p>
                  <p className="text-3xl font-mono font-bold text-green-300">{registered.team_id}</p>
                </div>
                <p className="text-gray-400 text-sm">Check email for OTP confirmation and ID card</p>
              </div>
            </div>
          </div>
        </div>
      </main>
    )
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
        <div className="mb-8 flex flex-col md:flex-row md:items-center md:justify-between">
          <div>
            <h1 className="text-4xl font-black text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-purple-400 mb-2">
              ⚙ TEAM REGISTRATION
            </h1>
            <p className="text-gray-400 font-mono">Network your skills. Build something great.</p>
          </div>

        </div>

        <div className="border border-cyan-500/30 rounded-xl p-8 bg-cyan-500/5 backdrop-blur-sm">
          {otpOpen ? (
            <div className="space-y-6">
              <div>
                <h3 className="text-2xl font-bold text-cyan-400 mb-2">🔐 VERIFY OTP</h3>
                <p className="text-gray-400">6-digit code sent to <span className="text-green-400 font-mono">{otpEmail}</span></p>
                <p className="text-gray-500 text-sm mt-2">OTP expires in 5 minutes. Check spam folder if not found.</p>
              </div>

              {success && (
                <div className="p-4 bg-green-500/20 border border-green-500/50 rounded-lg text-green-300 text-sm font-mono">
                  ✅ {success}
                </div>
              )}

              {error && (
                <div className="p-4 bg-red-500/20 border border-red-500/50 rounded-lg text-red-300 text-sm font-mono">
                  ❌ {error}
                </div>
              )}

              <input
                type="text"
                maxLength={6}
                value={otp}
                onChange={(e) => setOtp(e.target.value.replace(/\D/g, ''))}
                placeholder="000000"
                className="w-full p-4 bg-gray-900/50 rounded-lg text-white border-2 border-gray-700 focus:border-cyan-500 focus:outline-none text-center text-3xl tracking-widest font-mono font-bold"
              />

              <div className="flex gap-3">
                <button
                  onClick={verifyOtp}
                  disabled={loading || otp.length !== 6}
                  className="flex-1 py-3 bg-gradient-to-r from-cyan-600 to-cyan-500 rounded-lg font-bold disabled:opacity-50 hover:shadow-lg hover:shadow-cyan-500/50 transition"
                >
                  {loading ? 'VERIFYING...' : 'VERIFY'}
                </button>
                <button
                  onClick={() => {
                    setOtpOpen(false)
                    setOtp('')
                    setError('')
                    setSuccess('')
                  }}
                  className="flex-1 py-3 bg-gray-800 hover:bg-gray-700 rounded-lg font-bold transition"
                >
                  BACK
                </button>
              </div>
            </div>
          ) : (
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
              {error && (
                <div className="p-4 bg-red-500/20 border border-red-500/50 rounded-lg text-red-300 text-sm font-mono">
                  ❌ {error}
                </div>
              )}



              {/* Team Section */}
              <div className="space-y-4 pb-6 border-b border-gray-700">
                <h3 className="text-lg font-bold text-cyan-400">🖥️ TEAM INFO</h3>
                
                <div>
                  <label className="block text-xs text-cyan-300 mb-2 font-mono">TEAM NAME</label>
                  <input {...register('team_name')} placeholder="Your team name" className="w-full p-3 bg-gray-900/50 rounded-lg text-white border-2 border-gray-700 focus:border-cyan-500 focus:outline-none" />
                  {errors.team_name && <p className="text-red-400 text-xs mt-1">{errors.team_name.message}</p>}
                </div>
              </div>

              {/* Leader Section */}
              <div className="space-y-4 pb-6 border-b border-gray-700">
                <h3 className="text-lg font-bold text-purple-400">👤 TEAM LEADER</h3>
                
                <div>
                  <label className="block text-xs text-purple-300 mb-2 font-mono">NAME</label>
                  <input {...register('leader_name')} placeholder="Leader full name" className="w-full p-3 bg-gray-900/50 rounded-lg text-white border-2 border-gray-700 focus:border-purple-500 focus:outline-none" />
                  {errors.leader_name && <p className="text-red-400 text-xs mt-1">{errors.leader_name.message}</p>}
                </div>

                <div>
                  <label className="block text-xs text-purple-300 mb-2 font-mono">EMAIL</label>
                  <input {...register('leader_email')} type="email" placeholder="leader@example.com" className="w-full p-3 bg-gray-900/50 rounded-lg text-white border-2 border-gray-700 focus:border-purple-500 focus:outline-none" />
                  {errors.leader_email && <p className="text-red-400 text-xs mt-1">{errors.leader_email.message}</p>}
                </div>

                <div>
                  <label className="block text-xs text-purple-300 mb-2 font-mono">PHONE</label>
                  <input {...register('leader_phone')} type="tel" placeholder="10-digit phone number" className="w-full p-3 bg-gray-900/50 rounded-lg text-white border-2 border-gray-700 focus:border-purple-500 focus:outline-none" />
                  {errors.leader_phone && <p className="text-red-400 text-xs mt-1">{errors.leader_phone.message}</p>}
                </div>


              </div>

              {/* College Section */}
              <div className="space-y-4 pb-6 border-b border-gray-700">
                <h3 className="text-lg font-bold text-green-400">🏫 COLLEGE DETAILS</h3>
                
                <div>
                  <label className="block text-xs text-green-300 mb-2 font-mono">COLLEGE</label>
                  <input {...register('college_name')} placeholder="College name" className="w-full p-3 bg-gray-900/50 rounded-lg text-white border-2 border-gray-700 focus:border-green-500 focus:outline-none" />
                  {errors.college_name && <p className="text-red-400 text-xs mt-1">{errors.college_name.message}</p>}
                </div>

                <div className="grid grid-cols-1 gap-3">
                  <div>
                    <label className="block text-xs text-green-300 mb-2 font-mono">YEAR</label>
                    <select {...register('year')} className="w-full p-3 bg-gray-900/50 rounded-lg text-white border-2 border-gray-700 focus:border-green-500 focus:outline-none">
                      <option value="">Select year</option>
                      <option value="I">I</option>
                      <option value="II">II</option>
                      <option value="III">III</option>
                      <option value="IV">IV</option>
                    </select>
                    {errors.year && <p className="text-red-400 text-xs mt-1">{errors.year.message}</p>}
                  </div>
                </div>
              </div>

              {/* Domain Section */}
              <div className="space-y-4 pb-6 border-b border-gray-700">
                <h3 className="text-lg font-bold text-pink-400">🎯 TRACK SELECTION</h3>
                
                <div>
                  <label className="block text-xs text-pink-300 mb-2 font-mono">SELECT THEME</label>
                  <select {...register('domain')} className="w-full p-3 bg-gray-900/50 rounded-lg text-white border-2 border-gray-700 focus:border-pink-500 focus:outline-none">
                    <option value="">Choose your competition theme</option>
                    <option value="Agriculture">🌾 Agriculture</option>
                    <option value="Ocean Technology">🌊 Ocean Technology</option>
                    <option value="Women Safety">👩‍🦰 Women Safety</option>
                    <option value="Smart Automation">🤖 Smart Automation</option>
                    <option value="Forest/Wildlife">🌲 Forest/Wildlife</option>
                    <option value="Life Science">🧬 Life Science</option>
                    <option value="Food Tech">🥗 Food Tech</option>
                    <option value="Healthcare/Bio">⚕️ Healthcare/Bio</option>
                    <option value="Social Cause">❤️ Social Cause</option>
                    <option value="Rural Dev">🏘️ Rural Development</option>
                    <option value="IoT">📡 IoT</option>
                    <option value="AI">🤖 Artificial Intelligence</option>
                    <option value="ML">🧠 Machine Learning</option>
                    <option value="Data Science">📊 Data Science</option>
                    <option value="Waste Management">♻️ Waste Management</option>
                    <option value="Heritage/Culture">🏛️ Heritage/Culture</option>
                    <option value="Robotics/Drones">🚁 Robotics/Drones</option>
                    <option value="Toys/Games">🎮 Toys/Games</option>
                    <option value="Tourism">✈️ Tourism</option>
                    <option value="Green Tech">🌿 Green Tech</option>
                    <option value="Education">📚 Education</option>
                    <option value="Disaster Management">🚨 Disaster Management</option>
                    <option value="Environment/Climate">🌍 Environment/Climate</option>
                  </select>
                  {errors.domain && <p className="text-red-400 text-xs mt-1">{errors.domain.message}</p>}
                </div>
              </div>

              {/* Team Members Section with Photo Upload */}
<div className="space-y-4 pb-6 border-b border-gray-700">

  <div className="flex items-center justify-between">
    <h3 className="text-lg font-bold text-blue-400">
      👥 ADDITIONAL MEMBERS ({members.length} / 2)
    </h3>
    <button
      type="button"
      onClick={addMember}
      className="px-3 py-1 bg-blue-600 hover:bg-blue-500 rounded text-sm font-bold transition"
    >
      + ADD
    </button>
  </div>

  <p className="text-xs text-gray-400 mt-1">
    Leader's information is taken from above; add up to two more participants.
  </p>

  <div className="space-y-4">
    {members.map((_, idx) => (
      <div
        key={idx}
        className="p-4 bg-gray-900/30 rounded-lg border border-blue-500/30 space-y-3"
      >
        <div className="flex items-center justify-between">
          <span className="text-blue-300 font-mono text-sm">
            Member #{idx + 1}
          </span>
          {members.length > 0 && (
            <button
              type="button"
              onClick={() => removeMember(idx)}
              className="text-red-400 hover:text-red-300 text-sm font-bold"
            >
              ✕ Remove
            </button>
          )}
        </div>

        <div>
          <label className="block text-xs text-blue-300 mb-1 font-mono">
            NAME
          </label>
          <input
            {...register(`members.${idx}.name`)}
            placeholder="Full name"
            className="w-full p-2 bg-gray-800/50 rounded text-white border border-gray-600 focus:border-blue-500 focus:outline-none text-sm"
          />
          {errors.members?.[idx]?.name && (
            <p className="text-red-400 text-xs mt-1">
              {errors.members[idx]?.name?.message}
            </p>
          )}
        </div>

        <div>
          <label className="block text-xs text-blue-300 mb-1 font-mono">
            EMAIL
          </label>
          <input
            {...register(`members.${idx}.email`)}
            type="email"
            placeholder="email@example.com"
            className="w-full p-2 bg-gray-800/50 rounded text-white border border-gray-600 focus:border-blue-500 focus:outline-none text-sm"
          />
          {errors.members?.[idx]?.email && (
            <p className="text-red-400 text-xs mt-1">
              {errors.members[idx]?.email?.message}
            </p>
          )}
        </div>

        <div>
          <label className="block text-xs text-blue-300 mb-1 font-mono">
            PHONE
          </label>
          <input
            {...register(`members.${idx}.phone`)}
            type="tel"
            placeholder="10-digit phone"
            className="w-full p-2 bg-gray-800/50 rounded text-white border border-gray-600 focus:border-blue-500 focus:outline-none text-sm"
          />
          {errors.members?.[idx]?.phone && (
            <p className="text-red-400 text-xs mt-1">
              {errors.members[idx]?.phone?.message}
            </p>
          )}
        </div>

      </div>
    ))}
  </div>

  {errors.members && (
    <p className="text-red-400 text-xs">
      {typeof errors.members.message === 'string'
        ? errors.members.message
        : ''}
    </p>
  )}

</div>

              {/* Terms Section */}
              <div className="space-y-4 pt-4">
                <label className="flex items-start gap-3 cursor-pointer group">
                  <input type="checkbox" {...register('terms_accepted')} className="mt-1 w-5 h-5 accent-cyan-500" />
                  <span onClick={() => setShowTerms(true)} className="text-gray-300 group-hover:text-cyan-400 text-sm cursor-pointer">I agree to terms & conditions and confirm all information is accurate (click to view)</span>
                </label>
                {errors.terms_accepted && <p className="text-red-400 text-xs">{errors.terms_accepted.message}</p>}

                {/* Terms Modal */}
                {showTerms && (
                  <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70">
                    <div className="max-w-2xl w-full bg-gray-900 rounded-lg p-6 border border-cyan-500/30">
                      <h3 className="text-xl font-bold text-cyan-300 mb-3">Hackathon Terms & Conditions</h3>
                      <div className="text-sm text-gray-300 space-y-2 max-h-64 overflow-y-auto mb-4">
                        <p>1. All participants must be students or enrolled attendees.</p>
                        <p>2. Projects must be built during the hackathon timeframe.</p>
                        <p>3. Respect intellectual property and do not use proprietary code without permission.</p>
                        <p>4. Teams must not include professional developers hired for the project.</p>
                        <p>5. Follow the code of conduct; harassment or discriminatory behavior is prohibited.</p>
                        <p>6. The organizers reserve the right to disqualify teams violating rules.</p>
                        <p>7. By participating you agree to public demo and judging of your project.</p>
                      </div>
                      <div className="flex gap-3 justify-end">
                        <button onClick={() => setShowTerms(false)} className="px-4 py-2 bg-gray-800 hover:bg-gray-700 rounded">Back</button>
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* Submit Button */}
              <button
                type="submit"
                disabled={isSubmitting || loading}
                className="w-full py-4 bg-gradient-to-r from-cyan-500 to-purple-500 rounded-lg font-bold text-lg hover:shadow-lg hover:shadow-cyan-500/50 transition disabled:opacity-50"
              >
                {isSubmitting || loading ? '⏳ REGISTERING...' : '🚀 REGISTER TEAM'}
              </button>
            </form>
          )}
        </div>
      </div>
    </main>
  )
}
