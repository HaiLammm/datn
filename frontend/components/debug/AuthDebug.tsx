"use client";

import { useEffect, useState } from "react";

interface AuthStatus {
  hasToken: boolean;
  tokenValid: boolean;
  userRole: string | null;
  error: string | null;
}

export function AuthDebug() {
  const [authStatus, setAuthStatus] = useState<AuthStatus | null>(null);

  useEffect(() => {
    const checkAuth = async () => {
      try {
        // Check if we have token in cookies
        const hasToken = document.cookie.includes('access_token');
        
        // Try to make a request to check token validity
        const response = await fetch('/api/auth/me', {
          credentials: 'include'
        });
        
        if (response.ok) {
          const userData = await response.json();
          setAuthStatus({
            hasToken,
            tokenValid: true,
            userRole: userData.role || 'unknown',
            error: null
          });
        } else {
          setAuthStatus({
            hasToken,
            tokenValid: false,
            userRole: null,
            error: `API returned ${response.status}: ${response.statusText}`
          });
        }
      } catch (error) {
        setAuthStatus({
          hasToken: document.cookie.includes('access_token'),
          tokenValid: false,
          userRole: null,
          error: error instanceof Error ? error.message : 'Unknown error'
        });
      }
    };

    checkAuth();
  }, []);

  if (!authStatus) {
    return <div>Checking auth status...</div>;
  }

  return (
    <div className="p-4 bg-yellow-50 border border-yellow-200 rounded">
      <h3 className="font-bold text-yellow-800">🔍 Auth Debug Info</h3>
      <div className="mt-2 text-sm">
        <p><strong>Has Token:</strong> {authStatus.hasToken ? "✅ Yes" : "❌ No"}</p>
        <p><strong>Token Valid:</strong> {authStatus.tokenValid ? "✅ Valid" : "❌ Invalid"}</p>
        <p><strong>User Role:</strong> {authStatus.userRole || "Not available"}</p>
        {authStatus.error && (
          <p><strong>Error:</strong> <span className="text-red-600">{authStatus.error}</span></p>
        )}
        <p><strong>Cookies:</strong> {document.cookie || "None"}</p>
      </div>
    </div>
  );
}