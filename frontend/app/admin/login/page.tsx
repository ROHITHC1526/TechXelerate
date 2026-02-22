"use client"
import React, { useState } from 'react'
import { useRouter } from 'next/navigation'

export default function AdminLogin() {
  const [user, setUser] = useState('')
  const [pass, setPass] = useState('')
  const [loading, setLoading] = useState(false)
  const router = useRouter()

  const submit = async (e: any) => {
    e.preventDefault()
    setLoading(true)
    const res = await fetch('/api/admin/login', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ username: user, password: pass }) })
    setLoading(false)
    if (res.ok) {
      const j = await res.json()
      localStorage.setItem('admin_token', j.access_token)
      router.push('/admin/dashboard')
    } else {
      alert('Invalid credentials')
    }
  }

  return (
    <main className="min-h-screen p-8">
      <div className="max-w-md mx-auto glass p-6">
        <h2 className="text-2xl neon-glow">Admin Login</h2>
        <form onSubmit={submit} className="mt-4">
          <input value={user} onChange={(e)=> setUser(e.target.value)} placeholder="Username" className="w-full p-2 rounded bg-black/20" />
          <input value={pass} onChange={(e)=> setPass(e.target.value)} placeholder="Password" type="password" className="w-full p-2 rounded bg-black/20 mt-2" />
          <button disabled={loading} className="mt-4 px-4 py-2 neon-glow glass rounded">{loading? 'Signing in...' : 'Login'}</button>
        </form>
      </div>
    </main>
  )
}
