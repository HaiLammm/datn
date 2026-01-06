"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";

export function ApiConnectionTest() {
  const [testResults, setTestResults] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(false);

  const testApiConnection = async () => {
    setIsLoading(true);
    const results: any = {};

    try {
      // Test các endpoints khác nhau
      const apiUrls = [
        'http://localhost:8000/api/v1',
        'http://localhost:8000', 
        'http://localhost:8000/docs', // FastAPI docs
        process.env.NEXT_PUBLIC_API_URL || 'undefined'
      ];

      for (const url of apiUrls) {
        try {
          if (url === 'undefined') {
            results[url] = 'Environment variable not set';
            continue;
          }

          const response = await fetch(url, { 
            method: 'GET',
            signal: AbortSignal.timeout(5000) // 5s timeout
          });
          results[url] = {
            status: response.status,
            statusText: response.statusText,
            ok: response.ok,
            contentType: response.headers.get('content-type')
          };
        } catch (error: any) {
          results[url] = `Error: ${error.message}`;
        }
      }

      // Test login endpoint cụ thể
      try {
        const loginResponse = await fetch('http://localhost:8000/api/v1/auth/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email: 'test', password: 'test' }),
          credentials: 'include'
        });
        results['LOGIN_ENDPOINT'] = {
          status: loginResponse.status,
          statusText: loginResponse.statusText,
          headers: [...loginResponse.headers.entries()]
        };
      } catch (error: any) {
        results['LOGIN_ENDPOINT'] = `Error: ${error.message}`;
      }

      setTestResults(results);
    } catch (error: any) {
      setTestResults({ error: error.message });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="p-4 bg-blue-50 border border-blue-200 rounded">
      <h3 className="font-bold text-blue-800">🔗 API Connection Test</h3>
      
      <Button 
        onClick={testApiConnection} 
        disabled={isLoading}
        className="mt-2 mb-4"
        size="sm"
      >
        {isLoading ? "Testing..." : "Test API Connections"}
      </Button>

      {testResults && (
        <div className="mt-4 text-xs">
          <h4 className="font-semibold">Test Results:</h4>
          <pre className="bg-gray-100 p-2 rounded mt-2 overflow-auto text-xs">
            {JSON.stringify(testResults, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
}