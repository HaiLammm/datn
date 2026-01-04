"use client";

import { useEffect, useState } from 'react';
import { io, Socket } from 'socket.io-client';

export function useGlobalSocket() {
  const [socket, setSocket] = useState<Socket | null>(null);

  useEffect(() => {
    // Get auth token from cookies
    const getAuthToken = () => {
      return document.cookie
        .split('; ')
        .find(row => row.startsWith('access_token='))
        ?.split('=')[1];
    };

    const token = getAuthToken();
    if (!token) {
      console.warn('No auth token found, cannot connect to socket');
      return;
    }

    // Initialize socket connection
    const socketUrl = process.env.NEXT_PUBLIC_SOCKET_URL || 'http://localhost:3001';
    const newSocket = io(socketUrl, {
      auth: { token },
      transports: ['websocket', 'polling'],
    });

    newSocket.on('connect', () => {
      console.log('Global socket connected');
      // User room join happens automatically on server side
    });

    newSocket.on('connect_error', (error) => {
      console.error('Socket connection error:', error.message);
    });

    newSocket.on('disconnect', (reason) => {
      console.log('Socket disconnected:', reason);
    });

    setSocket(newSocket);

    return () => {
      console.log('Cleaning up global socket');
      newSocket.close();
    };
  }, []);

  return socket;
}