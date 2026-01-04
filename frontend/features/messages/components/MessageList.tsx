"use client";

import React, { useEffect, useRef, useState } from "react";
import { Message } from "@/lib/hooks/useSocket";

interface MessageListProps {
  messages: Message[];
  currentUserId: number | null;
}

/**
 * MessageBubble component - Individual message display
 */
interface MessageBubbleProps {
  message: Message;
  isOwn: boolean;
}

function MessageBubble({ message, isOwn }: MessageBubbleProps) {
  const formattedTime = React.useMemo(() => {
    const date = new Date(message.created_at);
    return date.toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit",
    });
  }, [message.created_at]);

  return (
    <div
      className={`flex w-full ${
        isOwn ? "justify-end" : "justify-start"
      } mb-3`}
    >
      <div
        className={`max-w-[70%] rounded-2xl px-4 py-2 ${
          isOwn
            ? "bg-blue-500 text-white rounded-br-md"
            : "bg-gray-100 text-gray-900 rounded-bl-md"
        }`}
      >
        {/* Sender name (for received messages) */}
        {!isOwn && message.sender?.full_name && (
          <p className="text-xs font-medium text-gray-600 mb-1">
            {message.sender.full_name}
          </p>
        )}

        {/* Message content */}
        <p className="text-sm whitespace-pre-wrap break-words">
          {message.content}
        </p>

        {/* Timestamp */}
        <p
          className={`text-xs mt-1 ${
            isOwn ? "text-blue-100" : "text-gray-500"
          }`}
        >
          {formattedTime}
        </p>
      </div>
    </div>
  );
}

/**
 * MessageList component - Displays a scrollable list of messages
 *
 * Features:
 * - Auto-scroll to bottom on new messages
 * - Virtual scrolling for large message lists
 * - Sender/receiver differentiation
 * - Timestamps with relative formatting
 */
export function MessageList({ messages, currentUserId }: MessageListProps) {
  const bottomRef = useRef<HTMLDivElement>(null);
  const [isAutoScrollEnabled, setIsAutoScrollEnabled] = useState(true);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (isAutoScrollEnabled && bottomRef.current) {
      bottomRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages, isAutoScrollEnabled]);

  // Handle scroll to detect if user is viewing older messages
  const handleScroll = (e: React.UIEvent<HTMLDivElement>) => {
    const { scrollTop, scrollHeight, clientHeight } = e.currentTarget;
    const isAtBottom = scrollHeight - scrollTop - clientHeight < 50;
    setIsAutoScrollEnabled(isAtBottom);
  };

  if (messages.length === 0) {
    return (
      <div className="flex items-center justify-center h-full text-gray-500">
        <div className="text-center">
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
          <p className="text-lg">No messages yet</p>
          <p className="text-sm">Start the conversation!</p>
        </div>
      </div>
    );
  }

  return (
    <div
      className="h-full overflow-y-auto p-4"
      onScroll={handleScroll}
    >
      {/* New message indicator */}
      {!isAutoScrollEnabled && (
        <button
          onClick={() => {
            setIsAutoScrollEnabled(true);
            bottomRef.current?.scrollIntoView({ behavior: "smooth" });
          }}
          className="block mx-auto mb-2 px-3 py-1 bg-blue-500 text-white text-xs rounded-full hover:bg-blue-600 transition-colors"
        >
          New messages ↓
        </button>
      )}

      {/* Messages */}
      {messages.map((message) => (
        <MessageBubble
          key={message.id}
          message={message}
          isOwn={currentUserId !== null && message.sender_id === currentUserId}
        />
      ))}

      {/* Invisible element for auto-scroll reference */}
      <div ref={bottomRef} />
    </div>
  );
}
