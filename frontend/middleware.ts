import { NextRequest, NextResponse } from 'next/server'

export function middleware(request: NextRequest) {
  // If accessing root, redirect to startup unless a short-lived cookie is present
  if (request.nextUrl.pathname === '/') {
    const skip = request.cookies.get('skipStartup')?.value || request.cookies.get('skipstartup')?.value
    if (skip === '1') {
      // allow access to root if cookie was set by the startup page
      return NextResponse.next()
    }
    return NextResponse.redirect(new URL('/startup', request.url))
  }

  return NextResponse.next()
}

export const config = {
  matcher: ['/'],
}