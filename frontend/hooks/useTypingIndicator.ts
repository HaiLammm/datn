"use client";

import { useEffect, useRef, useCallback, useState } from 'react';
import { Socket } from 'socket.io-client';

interface TypingUser {
  id: string;
  name: string;
}

export function useTypingIndicator(
  socket: Socket | null,
  conversationId: string
) {
  const [isTyping, setIsTyping] = useState(false);
  const [typingUser, setTypingUser] = useState<TypingUser | null>(null);
  
  const typingStopTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const typingStartTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  // Emit typing-start (debounced to avoid spamming)
  const emitTypingStart = useCallback(() => {
    if (socket?.connected) {
      socket.emit('typing-start', { conversationId });
      setIsTyping(true);
    }
  }, [socket, conversationId]);

  // Emit typing-stop
  const emitTypingStop = useCallback(() => {
    if (socket?.connected) {
      socket.emit('typing-stop', { conversationId });
      setIsTyping(false);
    }
  }, [socket, conversationId]);

  // Handle input change with debouncing
  const handleTyping = useCallback(() => {
    // Clear existing timeouts
    if (typingStartTimeoutRef.current) {
      clearTimeout(typingStartTimeoutRef.current);
    }
    if (typingStopTimeoutRef.current) {
      clearTimeout(typingStopTimeoutRef.current);
    }

    // Debounce typing-start by 300ms
    typingStartTimeoutRef.current = setTimeout(() => {
      emitTypingStart();
    }, 300);

    // Set typing-stop timeout for 3 seconds of inactivity
    typingStopTimeoutRef.current = setTimeout(() => {
      emitTypingStop();
    }, 3000);
  }, [emitTypingStart, emitTypingStop]);

  // Listen to typing events from other users
  useEffect(() => {
    if (!socket) return;

    const handleUserTyping = (data: { user_id: string; user_name: string }) => {
      setTypingUser({ id: data.user_id, name: data.user_name });
    };

    const handleUserStoppedTyping = (data: { user_id: string }) => {
      setTypingUser(null);
    };

    socket.on('user-typing', handleUserTyping);
    socket.on('user-stopped-typing', handleUserStoppedTyping);

    return () => {
      socket.off('user-typing', handleUserTyping);
      socket.off('user-stopped-typing', handleUserStoppedTyping);
    };
  }, [socket]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (typingStopTimeoutRef.current) {
        clearTimeout(typingStopTimeoutRef.current);
      }
      if (typingStartTimeoutRef.current) {
        clearTimeout(typingStartTimeoutRef.current);
      }
      emitTypingStop();
    };
  }, [emitTypingStop]);

  return {
    isTyping, // Is current user typing?
    typingUser, // Other user typing info
    handleTyping, // Call on input onChange
    emitTypingStop // Call on message send
  };
}