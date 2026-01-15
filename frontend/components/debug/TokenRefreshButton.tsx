"use client";

import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { config } from "@/lib/config";

export function TokenRefreshButton() {
  const router = useRouter();

  const refreshToken = async () => {
    try {
      const baseURL = config.apiUrl.endsWith('/api/v1') ? config.apiUrl : config.apiUrl + '/api/v1';
      const response = await fetch(`${baseURL}/auth/refresh-token`, {
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