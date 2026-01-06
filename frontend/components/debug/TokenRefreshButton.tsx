"use client";

import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";

export function TokenRefreshButton() {
  const router = useRouter();

  const refreshToken = async () => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/auth/refresh-token`, {
        method: 'POST',
        credentials: 'include',
      });

      if (response.ok) {
        console.log('✅ Token refreshed successfully');
        router.refresh(); // Refresh the page to get new session
      } else {
        console.error('❌ Failed to refresh token:', response.status);
        router.push('/login');
      }
    } catch (error) {
      console.error('❌ Token refresh error:', error);
      router.push('/login');
    }
  };

  return (
    <Button onClick={refreshToken} variant="outline" size="sm">
      🔄 Refresh Token
    </Button>
  );
}