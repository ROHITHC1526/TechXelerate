"use client"

import { useEffect, useState } from "react"

export default function BrochurePopup() {
  const [isOpen, setIsOpen] = useState(false)

  useEffect(() => {
    const hasSeen = localStorage.getItem("brochureSeen")

    if (!hasSeen) {
      setIsOpen(true)
      localStorage.setItem("brochureSeen", "true")
    }
  }, [])

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="relative bg-white rounded-xl max-w-3xl w-full p-4 shadow-2xl animate-fadeIn">

        <button
          onClick={() => setIsOpen(false)}
          className="absolute top-3 right-4 text-black text-xl font-bold"
        >
          ✕
        </button>

        <img
          src="/brochure.png"
          alt="Hackathon Brochure"
          className="w-full rounded-lg"
        />

      </div>
    </div>
  )
}