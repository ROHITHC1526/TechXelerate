'use client'
import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
<img src="/brochure.png" alt="Brochure" />

interface BrochureModalProps {
  isOpen: boolean
  onClose: () => void
}

const BrochureModal: React.FC<BrochureModalProps> = ({ isOpen, onClose }) => {
  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4"
          onClick={onClose}
        >
          <motion.div
            initial={{ scale: 0.8, opacity: 0, y: 20 }}
            animate={{ scale: 1, opacity: 1, y: 0 }}
            exit={{ scale: 0.8, opacity: 0, y: 20 }}
            transition={{ type: 'spring', damping: 25, stiffness: 300 }}
            className="relative bg-black border-2 border-cyan-500/50 rounded-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto shadow-2xl shadow-cyan-500/20"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Close/Back Button */}
            <button
              onClick={onClose}
              className="absolute top-6 left-6 z-10 p-2 rounded-full bg-cyan-500/20 hover:bg-cyan-500/40 transition-all group"
              title="Back"
            >
              <svg
                className="w-6 h-6 text-cyan-400 group-hover:text-cyan-300"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M15 19l-7-7 7-7"
                />
              </svg>
            </button>

            {/* Brochure Content */}
            <div className="p-8 md:p-12">
              {/* Header */}
              <div className="text-center mb-12">
                <div className="inline-block px-6 py-3 rounded-full border border-cyan-500/50 bg-cyan-500/10 mb-8">
                  <span className="text-cyan-400 font-mono text-sm font-bold">📋 EVENT BROCHURE</span>
                </div>
              </div>

              {/* Main Content */}
              <div className="space-y-8 text-white">
                {/* Title */}
                <div className="text-center border-b border-cyan-500/30 pb-8">
                  <h1 className="text-4xl md:text-5xl font-black mb-4 bg-gradient-to-r from-cyan-400 to-purple-400 bg-clip-text text-transparent">
                    TECHXELARATE 2026
                  </h1>
                  <p className="text-lg text-gray-300 font-semibold">National Level Hackathon</p>
                  <p className="text-sm text-gray-400 mt-2">Hosted by Laki Reddy Bali Reddy College of Engineering (LBRCE)</p>
                </div>

                {/* Event Details */}
                <div className="grid md:grid-cols-2 gap-8">
                  <div className="space-y-4">
                    <h3 className="text-xl font-bold text-cyan-300 flex items-center gap-2">
                      <span>📅</span> Event Details
                    </h3>
                    <div className="space-y-3 text-gray-300">
                      <p><span className="font-semibold text-cyan-400">Date:</span> March 13, 2026</p>
                      <p><span className="font-semibold text-cyan-400">Duration:</span> 6 Hours</p>
                      <p><span className="font-semibold text-cyan-400">Venue:</span> SRK HALL, Admin Block, 2nd Floor</p>
                      <p><span className="font-semibold text-cyan-400">Registration Fee:</span> ₹500 per team</p>
                    </div>
                  </div>

                  <div className="space-y-4">
                    <h3 className="text-xl font-bold text-purple-300 flex items-center gap-2">
                      <span>👥</span> Team Details
                    </h3>
                    <div className="space-y-3 text-gray-300">
                      <p><span className="font-semibold text-purple-400">Max Members:</span> 3 per team</p>
                      <p><span className="font-semibold text-purple-400">Eligibility:</span> All students welcome</p>
                      <p><span className="font-semibold text-purple-400">Registration:</span> Online portal</p>
                      <p><span className="font-semibold text-purple-400">Deadline:</span> Before event day</p>
                    </div>
                  </div>
                </div>

                {/* Themes */}
                <div className="space-y-4 border-t border-cyan-500/30 pt-8">
                  <h3 className="text-xl font-bold text-green-300 flex items-center gap-2">
                    <span>🎯</span> 23 Competition Themes
                  </h3>
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                    {[
                      'Agriculture', 'Ocean Technology', 'Women Safety', 'Smart Automation',
                      'Forest/Wildlife', 'Life Science', 'Food Tech', 'Healthcare/Bio',
                      'Social Cause', 'Rural Dev', 'IoT', 'AI', 'ML', 'Data Science',
                      'Waste Management', 'Heritage/Culture', 'Robotics/Drones', 'Toys/Games',
                      'Tourism', 'Green Tech', 'Education', 'Disaster Management', 'Environment/Climate'
                    ].map((theme, idx) => (
                      <div
                        key={idx}
                        className="px-3 py-2 bg-gradient-to-r from-cyan-500/10 to-purple-500/10 border border-cyan-500/30 rounded-lg text-sm text-cyan-300 hover:border-cyan-400 transition"
                      >
                        {theme}
                      </div>
                    ))}
                  </div>
                </div>

                {/* Timeline */}
                <div className="space-y-4 border-t border-cyan-500/30 pt-8">
                  <h3 className="text-xl font-bold text-blue-300 flex items-center gap-2">
                    <span>⏰</span> Event Timeline
                  </h3>
                  <div className="space-y-2 text-gray-300 text-sm">
                    <p><span className="font-semibold text-blue-400">09:00 AM</span> - Registration & Attendance</p>
                    <p><span className="font-semibold text-blue-400">09:30 AM</span> - Opening Ceremony</p>
                    <p><span className="font-semibold text-blue-400">10:00 AM</span> - Hackathon Starts</p>
                    <p><span className="font-semibold text-blue-400">01:00 PM</span> - Lunch Break</p>
                    <p><span className="font-semibold text-blue-400">04:00 PM</span> - Project Submissions</p>
                    <p><span className="font-semibold text-blue-400">04:45 PM</span> - Judging & Presentations</p>
                  </div>
                </div>

                {/* Organizers */}
                <div className="space-y-4 border-t border-cyan-500/30 pt-8">
                  <h3 className="text-xl font-bold text-yellow-300 flex items-center gap-2">
                    <span>🤝</span> Organizing Team
                  </h3>
                  <div className="grid md:grid-cols-2 gap-6 text-sm text-gray-300">
                    <div>
                      <p className="font-semibold text-yellow-400 mb-2">Chief Patrons</p>
                      <p>Dr. K. Appa Rao</p>
                      <p>Dr. M. Srinivasa Rao</p>
                    </div>
                    <div>
                      <p className="font-semibold text-yellow-400 mb-2">Conveners</p>
                      <p>Dr. S Jayaprada – CSE(AI & ML)</p>
                      <p>Dr. K.V. Panduranga Rao</p>
                    </div>
                  </div>
                </div>

                {/* Contact */}
                <div className="space-y-4 border-t border-cyan-500/30 pt-8">
                  <h3 className="text-xl font-bold text-orange-300 flex items-center gap-2">
                    <span>📞</span> Contact Information
                  </h3>
                  <div className="space-y-2 text-sm text-gray-300">
                    <p><span className="font-semibold text-orange-400">Faculty Coordinators:</span></p>
                    <p className="ml-4">Dr. I. Murali Krishna - +91 9032197772</p>
                    <p className="ml-4">Mr. Lalam Narendra - +91 9686079977</p>
                    <p className="font-semibold text-orange-400 mt-3">Student Coordinators:</p>
                    <p className="ml-4">B. Rohith Mani - +91 7036636671</p>
                    <p className="ml-4">V.Keerthan - +91 8309209791 </p>
                    <p className="ml-4">M.Sreeram - +91 8977012479</p>
                    <p className="ml-4">Shaik Sazid Vali - +91 7396279327</p>
                  </div>
                </div>

                {/* Footer Quote */}
                <div className="text-center pt-8 border-t border-cyan-500/30">
                  <p className="text-lg font-bold bg-gradient-to-r from-cyan-400 via-purple-400 to-cyan-400 bg-clip-text text-transparent italic">
                    "Innovate. Integrate. Elevate."
                  </p>
                </div>
              </div>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}

export default BrochureModal
