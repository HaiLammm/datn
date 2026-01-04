"use client";

// Test useSocket hook directly
import React from 'react';
import { useSocket } from '@/lib/hooks/useSocket';

export default function TestSocketPage() {
  const { 
    isConnected, 
    isConnecting, 
    connectionError, 
    messages, 
    sendMessage 
  } = useSocket('test-conversation');

  const handleSend = () => {
    sendMessage('Test message from browser!');
  };

  return (
    <div className="p-8 max-w-2xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">Socket.io Connection Test</h1>
      
      {/* Connection Status */}
      <div className="mb-4 p-4 border rounded">
        <h2 className="font-semibold mb-2">Connection Status:</h2>
        {isConnecting && <p className="text-yellow-600">🟡 Connecting...</p>}
        {isConnected && <p className="text-green-600">🟢 Connected!</p>}
        {connectionError && <p className="text-red-600">🔴 Error: {connectionError}</p>}
      </div>

      {/* Send Test Message */}
      <div className="mb-4">
        <button
          onClick={handleSend}
          disabled={!isConnected}
          className="px-4 py-2 bg-blue-500 text-white rounded disabled:bg-gray-300"
        >
          Send Test Message
        </button>
      </div>

      {/* Messages */}
      <div className="border rounded p-4">
        <h3 className="font-semibold mb-2">Messages:</h3>
        {messages.length === 0 ? (
          <p className="text-gray-500">No messages yet</p>
        ) : (
          messages.map((msg, idx) => (
            <div key={idx} className="mb-2 p-2 bg-gray-100 rounded">
              <p>{msg.content}</p>
              <small className="text-gray-500">{msg.created_at}</small>
            </div>
          ))
        )}
      </div>
    </div>
  );
}