import { NextRequest, NextResponse } from 'next/server';
import { getSession } from '@/lib/auth';

/**
 * GET /api/auth/me - Get current user information
 * 
 * This endpoint returns the current user's session information
 * by reading the HttpOnly JWT cookie and decoding it server-side.
 */
export async function GET(request: NextRequest) {
  try {
    // Get session from HttpOnly cookie
    const session = await getSession();
    
    if (!session) {
      return NextResponse.json(
        { error: 'Not authenticated' },
        { status: 401 }
      );
    }

    // Return user information from session
    return NextResponse.json({
      id: session.user.id,
      email: session.user.email,
      role: session.user.role,
      authenticated: true
    });
    
  } catch (error) {
    console.error('Auth API error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}