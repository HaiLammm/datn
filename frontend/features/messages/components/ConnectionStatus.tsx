"use client";

import React, { useEffect, useState } from 'react';

interface ConnectionStatusProps {
  isConnected: boolean;
}

export function ConnectionStatus({ isConnected }: ConnectionStatusProps) {
  const [showConnected, setShowConnected] = useState(false);
  const [wasDisconnected, setWasDisconnected] = useState(false);

  useEffect(() => {
    if (isConnected) {
      // Show "Connected" badge only if we were previously disconnected
      if (wasDisconnected) {
        setShowConnected(true);

        // Auto-hide after 2 seconds
        const timeout = setTimeout(() => {
          setShowConnected(false);
          setWasDisconnected(false);
        }, 2000);

        return () => clearTimeout(timeout);
      }
    } else {
      // Disconnected
      setWasDisconnected(true);
    }
  }, [isConnected, wasDisconnected]);

  if (isConnected && !showConnected) return null;

  return (
    <div
      className={`
        fixed top-4 right-4 px-3 py-2 rounded-lg text-sm font-medium
        flex items-center gap-2 shadow-lg z-50
        ${isConnected ? 'bg-green-500 text-white' : 'bg-red-500 text-white'}
      `}
    >
      <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-white' : 'bg-white animate-pulse'}`} />
      {isConnected ? 'Đã kết nối' : 'Mất kết nối'}
    </div>
  );
}