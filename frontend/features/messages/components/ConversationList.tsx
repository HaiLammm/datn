"use client";

import React from "react";
import Link from "next/link";
import { ConversationListItem } from "@/types/messages";

interface ConversationListProps {
  conversations: ConversationListItem[];
  isLoading?: boolean;
  onConversationClick?: (conversationId: string) => void;
}

function formatTimeAgo(dateString: string): string {
  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);

  if (diffMins < 1) return "Vừa xong";
  if (diffMins < 60) return `${diffMins} phút trước`;
  if (diffHours < 24) return `${diffHours} giờ trước`;
  if (diffDays === 1) return "Hôm qua";
  if (diffDays < 7) return `${diffDays} ngày trước`;
  return date.toLocaleDateString('vi-VN');
}

function ConversationItem({
  conversation,
  onConversationClick,
}: {
  conversation: ConversationListItem;
  onConversationClick?: (conversationId: string) => void;
}): React.ReactElement {
  const otherParticipant = conversation.other_participant;
  const lastMessage = conversation.last_message;
  const hasUnread = conversation.unread_count > 0;

  // Truncate message content to 60 chars as per story requirements
  const truncatedContent = lastMessage?.content 
    ? lastMessage.content.length > 60 
      ? lastMessage.content.substring(0, 60) + "..."
      : lastMessage.content
    : "";

  return (
    <Link
      href={`/messages/${conversation.conversation_id}`}
      onClick={() => onConversationClick?.(conversation.conversation_id)}
      className={`flex items-center gap-4 p-4 border-b border-gray-100 hover:bg-gray-50 transition-colors ${
        hasUnread ? "bg-blue-50" : ""
      }`}
    >
      {/* Avatar */}
      <div className="relative">
        <div className="w-12 h-12 rounded-full bg-blue-500 flex items-center justify-center text-white font-medium text-lg">
          {otherParticipant.avatar ? (
            <img
              src={otherParticipant.avatar}
              alt={otherParticipant.full_name}
              className="w-full h-full rounded-full object-cover"
            />
          ) : (
            otherParticipant.full_name.charAt(0).toUpperCase()
          )}
        </div>
      </div>

      {/* Conversation Info */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center justify-between mb-1">
          <h3 className={`font-medium truncate ${hasUnread ? "font-bold text-gray-900" : "text-gray-700"}`}>
            {otherParticipant.full_name}
          </h3>
          {lastMessage && (
            <span className="text-xs text-gray-400">
              {formatTimeAgo(lastMessage.timestamp)}
            </span>
          )}
        </div>

        {lastMessage && (
          <p className={`text-sm truncate ${hasUnread ? "text-gray-900 font-medium" : "text-gray-500"}`}>
            {truncatedContent}
          </p>
        )}
        
        {!lastMessage && (
          <p className="text-sm text-gray-400 italic">Chưa có tin nhắn</p>
        )}
      </div>

      {/* Unread badge */}
      {hasUnread && (
        <div className="flex flex-col items-end">
          <div className="bg-blue-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
            {conversation.unread_count}
          </div>
        </div>
      )}
    </Link>
  );
}

export function ConversationList({
  conversations,
  isLoading = false,
  onConversationClick,
}: ConversationListProps): React.ReactElement {
  if (isLoading) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="space-y-0">
          {[1, 2, 3].map((i) => (
            <div key={i} className="flex items-center gap-4 p-4 border-b border-gray-100 animate-pulse">
              <div className="w-12 h-12 bg-gray-200 rounded-full" />
              <div className="flex-1 space-y-2">
                <div className="h-4 bg-gray-200 rounded w-1/3" />
                <div className="h-3 bg-gray-200 rounded w-2/3" />
              </div>
              <div className="w-4 h-4 bg-gray-200 rounded-full" />
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (conversations.length === 0) {
    return (
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
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200">
      {conversations.map((conversation) => (
        <ConversationItem 
          key={conversation.conversation_id} 
          conversation={conversation} 
          onConversationClick={onConversationClick}
        />
      ))}
    </div>
  );
}
