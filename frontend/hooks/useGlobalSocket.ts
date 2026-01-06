"use client";

import { useEffect, useState } from 'react';
import { usePathname, useRouter } from 'next/navigation';
import { io, Socket } from 'socket.io-client';
import { toast } from 'sonner';

export function useGlobalSocket() {
  const [socket, setSocket] = useState<Socket | null>(null);
  const pathname = usePathname();
  const router = useRouter();

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

    // Toast notification on new message (when not on the conversation page)
    newSocket.on('conversation-updated', (data) => {
      // Check if user is on the conversation page
      const isOnConversationPage = pathname === `/messages/${data.conversation_id}`;

      if (!isOnConversationPage) {
        // Show toast notification
        const messagePreview = data.last_message.content.length > 50 
          ? data.last_message.content.substring(0, 50) + '...' 
          : data.last_message.content;
        
        toast(`${data.last_message.sender_name}: ${messagePreview}`, {
          action: {
            label: 'Xem',
            onClick: () => router.push(`/messages/${data.conversation_id}`)
          }
        });
      }
    });

    setSocket(newSocket);

    return () => {
      console.log('Cleaning up global socket');
      newSocket.close();
    };
  }, [pathname, router]);

  return socket;
}