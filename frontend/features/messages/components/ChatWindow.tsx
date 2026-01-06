"use client";

import React from "react";
import { MessageList } from "./MessageList";
import { MessageInput } from "./MessageInput";
import { useSocket, Message } from "@/lib/hooks/useSocket";

interface ChatWindowProps {
  conversationId: string;
  candidateName: string;
  candidateAvatar?: string;
  initialMessages?: Message[];
  onSendMessage?: (content: string) => void;
}

/**
 * ChatWindow component - Main chat interface for a conversation
 *
 * Features:
 * - Message list with scroll and auto-scroll
 * - Connection status indicator
 * - Message input with send functionality
 * - Real-time message updates via Socket.io
 */
export function ChatWindow({
  conversationId,
  candidateName,
  candidateAvatar,
  initialMessages = [],
  onSendMessage,
}: ChatWindowProps) {
  const {
    isConnected,
    isConnecting,
    connectionError,
    messages,
    sendMessage,
    startTyping,
    stopTyping,
    clearMessages,
  } = useSocket(conversationId);

  // Combine initial messages with real-time messages
  const allMessages = React.useMemo(() => {
    const initialIds = new Set(initialMessages.map((m) => m.id));
    const realTimeMessages = messages.filter((m) => !initialIds.has(m.id));
    return [...initialMessages, ...realTimeMessages];
  }, [initialMessages, messages]);

  const handleSendMessage = (content: string) => {
    sendMessage(content);
    onSendMessage?.(content);
  };

  const handleTypingStart = () => {
    startTyping(conversationId);
  };

  const handleTypingStop = () => {
    stopTyping(conversationId);
  };

  return (
    <div className="flex flex-col h-full bg-white rounded-lg shadow-md">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-gray-200">
        <div className="flex items-center gap-3">
          {/* Avatar */}
          <div className="w-10 h-10 rounded-full bg-blue-500 flex items-center justify-center text-white font-medium">
            {candidateAvatar ? (
              <img
                src={candidateAvatar}
                alt={candidateName}
                className="w-full h-full rounded-full object-cover"
              />
            ) : (
              candidateName.charAt(0).toUpperCase()
            )}
          </div>

          {/* Name and status */}
          <div>
            <h3 className="font-medium text-gray-900">{candidateName}</h3>
            <div className="flex items-center gap-1">
              {isConnected ? (
                <>
                  <span className="w-2 h-2 bg-green-500 rounded-full" />
                  <span className="text-xs text-green-600">Connected</span>
                </>
              ) : isConnecting ? (
                <>
                  <span className="w-2 h-2 bg-yellow-500 rounded-full animate-pulse" />
                  <span className="text-xs text-yellow-600">Connecting...</span>
                </>
              ) : (
                <>
                  <span className="w-2 h-2 bg-red-500 rounded-full" />
                  <span className="text-xs text-red-600">
                    {connectionError || "Disconnected"}
                  </span>
                </>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Message List */}
      <div className="flex-1 overflow-y-auto">
        <MessageList messages={allMessages} currentUserId={null} />
      </div>

      {/* Message Input */}
      <MessageInput
        onSend={handleSendMessage}
        onTyping={handleTypingStart}
        onStopTyping={handleTypingStop}
        disabled={!isConnected}
        placeholder="Nhập tin nhắn..."
      />
    </div>
  );
}
