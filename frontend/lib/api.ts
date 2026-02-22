const API_BASE = process.env.NEXT_PUBLIC_API_URL || ''

export async function postRegister(data: any) {
  const res = await fetch(`${API_BASE}/api/register`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) })
  return res
}

export async function postVerifyOtp(payload: any) {
  const res = await fetch(`${API_BASE}/api/verify-otp`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) })
  return res
}

export async function postTestEmail(email: string) {
  const res = await fetch(`${API_BASE}/api/test-email`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ email }) })
  return res
}
