"use client";

import React, { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { ConversationList } from "@/features/messages/components/ConversationList";
import { useGlobalSocket } from "@/hooks/useGlobalSocket";
import { ConversationListItem, ConversationUpdatedEvent } from "@/types/messages";
import { getConversations, markConversationAsRead } from "@/features/messages/actions";

export default function MessagesPage(): React.ReactElement {
  const router = useRouter();
  const socket = useGlobalSocket();
  const [conversations, setConversations] = useState<ConversationListItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchConversations = async () => {
      try {
        // Fetch conversations using server action
        // Layout already verified auth, no need to check session here
        const data = await getConversations();
        setConversations(data);
      } catch (err) {
        console.error("Error fetching conversations:", err);
        setError(err instanceof Error ? err.message : "Failed to load conversations");
      } finally {
        setIsLoading(false);
      }
    };

    fetchConversations();
  }, [router]);

  // Story 7.3: Real-time conversation list updates
  useEffect(() => {
    if (!socket) return;

    const handleConversationUpdated = (data: ConversationUpdatedEvent) => {
      console.log('Conversation updated:', data);
      
      setConversations(prev => {
        // Find and update conversation
        const updated = prev.map(conv =>
          conv.conversation_id === data.conversation_id
            ? {
                ...conv,
                last_message: data.last_message,
                unread_count: data.unread_count,
                updated_at: data.updated_at
              }
            : conv
        );

        // Re-sort by updated_at (newest first)
        return updated.sort((a, b) =>
          new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime()
        );
      });
    };

    socket.on('conversation-updated', handleConversationUpdated);

    return () => {
      socket.off('conversation-updated', handleConversationUpdated);
    };
  }, [socket]);

  // Story 7.3: Mark conversation as read when clicked
  const handleMarkAsRead = async (conversationId: string) => {
    try {
      await markConversationAsRead(conversationId);

      // Update local state to mark as read
      setConversations(prev =>
        prev.map(conv =>
          conv.conversation_id === conversationId
            ? { ...conv, unread_count: 0 }
            : conv
        )
      );
    } catch (error) {
      console.error('Failed to mark conversation as read:', error);
    }
  };

  // Loading state
  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="container mx-auto px-4 py-8">
          <h1 className="text-2xl font-bold text-gray-900 mb-6">Messages</h1>
          <ConversationList conversations={[]} isLoading={true} />
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center max-w-md">
          <svg
            className="w-16 h-16 mx-auto mb-4 text-red-500"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
            />
          </svg>
          <h2 className="text-xl font-semibold text-gray-900 mb-2">
            Unable to load conversations
          </h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={() => window.location.reload()}
            className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  // Empty state with Vietnamese message as per AC #6
  if (conversations.length === 0) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="container mx-auto px-4 py-8">
          <div className="max-w-2xl mx-auto">
            <div className="flex items-center justify-between mb-6">
              <h1 className="text-2xl font-bold text-gray-900">Messages</h1>
            </div>

            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-12 text-center">
              <svg
                className="w-16 h-16 mx-auto mb-4 text-gray-300"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={1.5}
                  d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
                />
              </svg>
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                Bạn chưa có cuộc trò chuyện nào
              </h3>
              <p className="text-gray-500">
                Khi có tin nhắn mới, chúng sẽ xuất hiện ở đây.
              </p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-2xl mx-auto">
          <div className="flex items-center justify-between mb-6">
            <h1 className="text-2xl font-bold text-gray-900">Messages</h1>
          </div>

          <ConversationList 
            conversations={conversations} 
            onConversationClick={handleMarkAsRead}
          />
        </div>
      </div>
    </div>
  );
}
