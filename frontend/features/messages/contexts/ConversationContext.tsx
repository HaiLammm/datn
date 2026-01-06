"use client";

import React, { createContext, useContext, useEffect, useState } from 'react';
import { ConversationListItem } from '@/types/messages';
import { useGlobalSocket } from '@/hooks/useGlobalSocket';

interface ConversationContextType {
  conversations: ConversationListItem[];
  setConversations: React.Dispatch<React.SetStateAction<ConversationListItem[]>>;
  isLoading: boolean;
  error: string | null;
  refreshConversations: () => Promise<void>;
}

const ConversationContext = createContext<ConversationContextType | undefined>(undefined);

export function ConversationProvider({ children }: { children: React.ReactNode }) {
  const [conversations, setConversations] = useState<ConversationListItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const socket = useGlobalSocket();

  const refreshConversations = async () => {
    try {
      setIsLoading(true);
      setError(null);
      
      const token = document.cookie
        .split('; ')
        .find(row => row.startsWith('access_token='))
        ?.split('=')[1];
        
      if (!token) {
        setError('No authentication token');
        return;
      }

      const response = await fetch('/api/v1/messages/conversations', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to fetch conversations');
      }

      const data = await response.json();
      setConversations(data.conversations || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setIsLoading(false);
    }
  };

  // Load conversations on mount
  useEffect(() => {
    refreshConversations();
  }, []);

  // Real-time updates via socket
  useEffect(() => {
    if (!socket) return;

    const handleConversationUpdated = (data: any) => {
      setConversations(prev => {
        // Find existing conversation
        const existingIndex = prev.findIndex(
          conv => conv.conversation_id === data.conversation_id
        );

        if (existingIndex === -1) {
          // New conversation - refresh all to get proper format
          refreshConversations();
          return prev;
        }

        // Update existing conversation
        const updated = [...prev];
        updated[existingIndex] = {
          ...updated[existingIndex],
          last_message: data.last_message,
          unread_count: data.unread_count,
          updated_at: data.updated_at
        };

        // Sort by updated_at (most recent first)
        updated.sort((a, b) => 
          new Date(b.updated_at || 0).getTime() - new Date(a.updated_at || 0).getTime()
        );

        return updated;
      });
    };

    socket.on('conversation-updated', handleConversationUpdated);

    return () => {
      socket.off('conversation-updated', handleConversationUpdated);
    };
  }, [socket]);

  return (
    <ConversationContext.Provider value={{
      conversations,
      setConversations,
      isLoading,
      error,
      refreshConversations
    }}>
      {children}
    </ConversationContext.Provider>
  );
}

export function useConversations() {
  const context = useContext(ConversationContext);
  if (context === undefined) {
    throw new Error('useConversations must be used within a ConversationProvider');
  }
  return context;
}