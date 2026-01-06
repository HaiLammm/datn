"use client";

import React, { useEffect, useState, use } from "react";
import { useRouter } from "next/navigation";
import { ChatWindow } from "@/features/messages/components/ChatWindow";
import { useSocket, Message } from "@/lib/hooks/useSocket";
import { getConversationWithContext, getConversationMessages } from "@/features/messages/actions";

interface MessageUser {
  id: string; // Changed from number to match SessionUser
  email: string;
  role: string;
  full_name?: string;
}

interface ConversationDetails {
  id: string;
  recruiter_id: string; // Changed from number to match user ID type
  candidate_id: string; // Changed from number to match user ID type
  created_at: string;
  updated_at: string;
  other_user?: {
    id: string; // Changed from number
    full_name: string;
    avatar?: string;
  };
}

interface PageProps {
  params: Promise<{ conversationId: string }>;
}

interface MessageListResponse {
  messages: Message[];
  total: number;
}

/**
 * Chat page - Displays a conversation between recruiter and candidate
 *
 * Features:
 * - Real-time messaging via Socket.io
 * - Initial message load via REST API
 * - Connection status indicator
 * - Auto-reconnect on network issues
 */
export default function ChatPage({ params }: PageProps) {
  const { conversationId } = use(params);
  const router = useRouter();

  const [currentUser, setCurrentUser] = useState<MessageUser | null>(null);
  const [conversation, setConversation] = useState<ConversationDetails | null>(null);
  const [initialMessages, setInitialMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch session and conversation data
  useEffect(() => {
    const fetchData = async () => {
      try {
        // Fetch conversation details with context using server action
        // Layout already verified auth, no need to check session here
        const convData = await getConversationWithContext(conversationId);
        if (!convData) {
          throw new Error("Conversation not found");
        }
        
        // Fetch initial messages using server action
        const msgData = await getConversationMessages(conversationId);
        if (msgData?.messages) {
          setInitialMessages(msgData.messages);
        }

        // Set conversation with other user info
        setConversation({
          ...convData,
          other_user: {
            id: convData.otherUserId,
            full_name: "User", // Would be fetched from API
          },
        });
        
        // Set current user from server data
        setCurrentUser({
          id: convData.currentUserId,
          email: '', // Not needed for chat
          role: '', // Not needed for chat
        });
      } catch (err) {
        console.error("Error fetching data:", err);
        setError(err instanceof Error ? err.message : "Failed to load conversation");
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, [conversationId, router]);

  // Handle send message
  const handleSendMessage = (content: string) => {
    console.log("Sending message:", content);
    // Message is sent via Socket.io through the ChatWindow component
  };

  // Loading state
  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <svg
            className="animate-spin w-10 h-10 mx-auto mb-4 text-blue-500"
            fill="none"
            viewBox="0 0 24 24"
          >
            <circle
              className="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="4"
            />
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            />
          </svg>
          <p className="text-gray-600">Loading conversation...</p>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="flex items-center justify-center h-screen">
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
            Unable to load conversation
          </h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={() => router.back()}
            className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
          >
            Go Back
          </button>
        </div>
      </div>
    );
  }

  // Main chat interface
  return (
    <div className="h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-4xl mx-auto px-4 py-3">
          <button
            onClick={() => router.back()}
            className="flex items-center gap-2 text-gray-600 hover:text-gray-900 transition-colors"
          >
            <svg
              className="w-5 h-5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M10 19l-7-7m0 0l7-7m-7 7h18"
              />
            </svg>
            <span>Back</span>
          </button>
        </div>
      </header>

      {/* Chat Window */}
      <main className="h-[calc(100vh-64px)]">
        <div className="h-full max-w-4xl mx-auto p-4">
          <ChatWindow
            conversationId={conversationId}
            candidateName={conversation?.other_user?.full_name || "Chat"}
            candidateAvatar={conversation?.other_user?.avatar}
            initialMessages={initialMessages}
            onSendMessage={handleSendMessage}
          />
        </div>
      </main>
    </div>
  );
}
