'use server';

/**
 * Auth Server Actions
 * 
 * This module contains server actions for authentication that can be safely
 * imported by client components. The 'use server' directive at the top of
 * the file marks all exports as Server Actions.
 */

import { cookies } from 'next/headers';

/**
 * Get auth token from server-side HttpOnly cookie
 * 
 * This is a server action that can be called from client components
 * to safely retrieve the authentication token without exposing it
 * to client-side JavaScript.
 * 
 * @returns JWT token string or null
 */
export async function getAccessToken(): Promise<string | null> {
  try {
    const cookieStore = await cookies();
    const token = cookieStore.get('access_token')?.value;
    return token || null;
  } catch (error) {
    console.error('Error getting access token:', error);
    return null;
  }
}
