"use client";

import { useEffect, useState, useCallback, useRef } from 'react';
import { io, Socket } from 'socket.io-client';
import { getClientAuthToken } from '@/lib/auth-client';
import { getSocketUrl, config } from '@/lib/config';

export interface Message {
  id: string;
  conversation_id: string;
  sender_id: number;
  content: string;
  created_at: string;
  is_read: boolean;
  sender?: {
    id: number;
    full_name: string;
    email: string;
    role: string;
  };
}

export interface UseSocketReturn {
  socket: Socket | null;
  messages: Message[];
  isConnected: boolean;
  isConnecting: boolean;
  error: string | null;
  connectionError: string | null; // Alias for error
  sendMessage: (content: string) => void;
  setMessages: (messages: Message[]) => void;
  addMessage: (message: Message) => void;
  clearError: () => void;
  clearMessages: () => void;
  startTyping: (conversationId: string) => void;
  stopTyping: (conversationId: string) => void;
}

/**
 * Custom hook for Socket.io integration with JWT authentication
 * 
 * Features:
 * - Auto-connection with JWT token
 * - Real-time message handling
 * - Connection status tracking
 * - Auto-reconnect on network issues
 * - Error handling with user feedback
 * - Typing indicators support
 */
export function useSocket(conversationId: string): UseSocketReturn {
  const [socket, setSocket] = useState<Socket | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const reconnectAttempts = useRef(0);
  const maxReconnectAttempts = config.websocket.reconnectionAttempts;
  const errorTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const optimisticMessageTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  // Get auth token
  const getAuthToken = useCallback(() => {
    return getClientAuthToken() || '';
  }, []);

  // Clear error function with timeout cleanup
  const clearError = useCallback(() => {
    if (errorTimeoutRef.current) {
      clearTimeout(errorTimeoutRef.current);
      errorTimeoutRef.current = null;
    }
    setError(null);
  }, []);

  // Enhanced error setting with auto-clear for non-critical errors
  const setErrorWithTimeout = useCallback((message: string, isPersistent = false, timeout = 5000) => {
    setError(message);
    
    if (!isPersistent) {
      // Clear previous timeout
      if (errorTimeoutRef.current) {
        clearTimeout(errorTimeoutRef.current);
      }
      
      // Set new timeout to auto-clear error
      errorTimeoutRef.current = setTimeout(() => {
        setError(null);
        errorTimeoutRef.current = null;
      }, timeout);
    }
  }, []);

  // Send message function with enhanced error handling
  const sendMessage = useCallback((content: string) => {
    if (!socket || !isConnected) {
      setErrorWithTimeout('Not connected to server. Please check your connection.', false);
      return;
    }

    if (!content.trim()) {
      setErrorWithTimeout('Message cannot be empty.', false, 3000);
      return;
    }

    // Clear any previous error
    clearError();

    // Add optimistic message first
    const optimisticMessage: Message = {
      id: `temp-${Date.now()}`,
      conversation_id: conversationId,
      sender_id: 0, // Will be set by server
      content: content.trim(),
      created_at: new Date().toISOString(),
      is_read: false,
    };

    setMessages(prev => [...prev, optimisticMessage]);

    // Set timeout for optimistic message (remove if server doesn't respond in 10s)
    if (optimisticMessageTimeoutRef.current) {
      clearTimeout(optimisticMessageTimeoutRef.current);
    }
    
    optimisticMessageTimeoutRef.current = setTimeout(() => {
      setMessages(prev => prev.filter(msg => msg.id !== optimisticMessage.id));
      setErrorWithTimeout('Message failed to send. Please try again.', false);
    }, 10000);

    // Send to server
    socket.emit('send-message', {
      conversationId,
      content: content.trim()
    });

    // Message sent successfully - could add logging here if needed
  }, [socket, isConnected, conversationId, clearError, setErrorWithTimeout]);

  // Add message function with optimistic timeout cleanup
  const addMessage = useCallback((message: Message) => {
    setMessages(prev => {
      // Remove optimistic message if exists
      const filteredPrev = prev.filter(msg => !msg.id.startsWith('temp-'));
      // Add real message
      return [...filteredPrev, message];
    });
    
    // Clear optimistic message timeout since message was successful
    if (optimisticMessageTimeoutRef.current) {
      clearTimeout(optimisticMessageTimeoutRef.current);
      optimisticMessageTimeoutRef.current = null;
    }
    
    // Clear any send-related errors
    setError(null);
  }, []);

  // Clear messages function
  const clearMessages = useCallback(() => {
    setMessages([]);
  }, []);

  // Typing indicator functions
  const startTyping = useCallback((conversationId: string) => {
    if (!socket || !isConnected) return;
    
    socket.emit('start-typing', { conversationId });
    // Started typing indicator
  }, [socket, isConnected]);

  const stopTyping = useCallback((conversationId: string) => {
    if (!socket || !isConnected) return;
    
    socket.emit('stop-typing', { conversationId });
    // Stopped typing indicator
  }, [socket, isConnected]);

  // Socket connection effect
  useEffect(() => {
    if (!conversationId) return;

    const token = getAuthToken();
    if (!token) {
      setErrorWithTimeout('Authentication token not found. Please log in again.', true);
      return;
    }

    // Initializing socket connection
    setIsConnecting(true);
    setError(null);

    // Initialize socket connection with validated URL
    const socketUrl = getSocketUrl();
    const newSocket = io(socketUrl, {
      auth: { token },
      transports: ['websocket', 'polling'],
      forceNew: true,
      reconnection: true,
      reconnectionAttempts: maxReconnectAttempts,
      reconnectionDelay: config.websocket.reconnectionDelay,
      timeout: config.websocket.timeout,
    });

    // Connection event handlers
    newSocket.on('connect', () => {
      // Successfully connected to Socket.io server
      setIsConnected(true);
      setIsConnecting(false);
      setError(null);
      reconnectAttempts.current = 0;

      // Join conversation room
      newSocket.emit('join-conversation', conversationId);
    });

    newSocket.on('disconnect', (reason) => {
      // Disconnected from Socket.io server
      setIsConnected(false);
      setIsConnecting(false);
      
      if (reason === 'io server disconnect') {
        // Server initiated disconnect, try to reconnect
        setErrorWithTimeout('Server disconnected. Attempting to reconnect...', false, 8000);
      } else if (reason === 'transport close') {
        // Network issues
        setErrorWithTimeout('Connection lost. Reconnecting...', false, 8000);
      }
    });

    newSocket.on('connect_error', (error) => {
      // Connection error occurred
      setIsConnected(false);
      setIsConnecting(false);
      reconnectAttempts.current++;
      
      // Calculate exponential backoff delay
      const delay = Math.min(1000 * Math.pow(2, reconnectAttempts.current - 1), 10000);
      
      if (reconnectAttempts.current >= maxReconnectAttempts) {
        setErrorWithTimeout('Failed to connect to chat server. Please refresh the page.', true);
      } else {
        setErrorWithTimeout(
          `Connection failed. Retrying in ${Math.ceil(delay / 1000)}s... (${reconnectAttempts.current}/${maxReconnectAttempts})`,
          false,
          delay + 2000
        );
      }
    });

    newSocket.on('reconnect', () => {
      // Successfully reconnected
      setError(null);
      reconnectAttempts.current = 0;
      // Rejoin conversation room
      newSocket.emit('join-conversation', conversationId);
    });

    // Message event handlers
    newSocket.on('new-message', (message: Message) => {
      addMessage(message);
    });

    newSocket.on('message-sent', (confirmation) => {
      // Message delivery confirmed - remove optimistic messages
      setMessages(prev => prev.filter(msg => !msg.id.startsWith('temp-')));
      
      // Clear optimistic message timeout since message was successful
      if (optimisticMessageTimeoutRef.current) {
        clearTimeout(optimisticMessageTimeoutRef.current);
        optimisticMessageTimeoutRef.current = null;
      }
    });

    newSocket.on('conversation-joined', (data) => {
      // Successfully joined conversation room
    });

    // Error event handlers
    newSocket.on('error', (errorData) => {
      // Determine error type and set appropriate timeout
      const errorMessage = errorData.message || 'An error occurred with the chat connection.';
      const isCriticalError = errorMessage.includes('Authentication') || errorMessage.includes('permission');
      
      setErrorWithTimeout(errorMessage, isCriticalError, isCriticalError ? 0 : 8000);
      
      // Remove failed optimistic messages
      setMessages(prev => prev.filter(msg => !msg.id.startsWith('temp-')));
      
      // Clear optimistic message timeout
      if (optimisticMessageTimeoutRef.current) {
        clearTimeout(optimisticMessageTimeoutRef.current);
        optimisticMessageTimeoutRef.current = null;
      }
    });

    // Typing event handlers (for future use)
    newSocket.on('user-typing', (data) => {
      // TODO: Implement typing indicator UI
    });

    newSocket.on('user-stopped-typing', (data) => {
      // TODO: Remove typing indicator UI
    });

    setSocket(newSocket);

    // Cleanup function
    return () => {
      // Cleaning up socket connection
      
      // Clear all timeouts
      if (errorTimeoutRef.current) {
        clearTimeout(errorTimeoutRef.current);
        errorTimeoutRef.current = null;
      }
      if (optimisticMessageTimeoutRef.current) {
        clearTimeout(optimisticMessageTimeoutRef.current);
        optimisticMessageTimeoutRef.current = null;
      }
      newSocket.off('connect');
      newSocket.off('disconnect');
      newSocket.off('connect_error');
      newSocket.off('reconnect');
      newSocket.off('new-message');
      newSocket.off('message-sent');
      newSocket.off('conversation-joined');
      newSocket.off('error');
      newSocket.off('user-typing');
      newSocket.off('user-stopped-typing');
      
      if (newSocket.connected) {
        newSocket.disconnect();
      }
      
      setSocket(null);
      setIsConnected(false);
      setIsConnecting(false);
    };
  }, [conversationId, getAuthToken, addMessage, setErrorWithTimeout]);

  return {
    socket,
    messages,
    isConnected,
    isConnecting,
    error,
    connectionError: error, // Alias for error to match ChatWindow expectations
    sendMessage,
    setMessages,
    addMessage,
    clearError,
    clearMessages,
    startTyping,
    stopTyping,
  };
}