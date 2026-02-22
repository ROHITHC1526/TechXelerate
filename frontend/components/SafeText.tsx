import React from 'react'

export default function SafeText({ value }: { value: any }) {
  if (value === null || value === undefined || value === '') return null
  if (typeof value === 'string' || typeof value === 'number' || typeof value === 'boolean') return <>{String(value)}</>
  try {
    return <>{JSON.stringify(value)}</>
  } catch (e) {
    return <>{String(value)}</>
  }
}
