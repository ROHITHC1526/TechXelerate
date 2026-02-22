"use client"
import { useEffect } from 'react'
import { useRouter } from 'next/navigation'

export default function Intro() {
  const router = useRouter()

  useEffect(() => {
    router.push('/startup')
  }, [router])

  return null
}
