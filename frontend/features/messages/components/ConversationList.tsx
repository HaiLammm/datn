"use client";

import React from "react";
import Link from "next/link";

interface Conversation {
  id: string;
  recruiter_id: string;
  candidate_id: string;
  created_at: string;
  updated_at: string;
  unread_count?: number;
  last_message?: {
    id: string;
    content: string;
    created_at: string;
    sender_id: number;
  };
  other_user?: {
    id: string;
    full_name: string;
    avatar?: string;
  };
}

interface ConversationListProps {
  conversations: Conversation[];
  isLoading?: boolean;
}

function formatTimeAgo(dateString: string): string {
  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);

  if (diffMins < 1) return "Just now";
  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  if (diffDays < 7) return `${diffDays}d ago`;
  return date.toLocaleDateString();
}

function ConversationItem({
  conversation,
}: {
  conversation: Conversation;
}): React.ReactElement {
  const otherUser = conversation.other_user;
  const lastMessage = conversation.last_message;
  const hasUnread = (conversation.unread_count || 0) > 0;

  return (
    <Link
      href={`/messages/${conversation.id}`}
      className={`flex items-center gap-4 p-4 border-b border-gray-100 hover:bg-gray-50 transition-colors ${
        hasUnread ? "bg-blue-50/50" : ""
      }`}
    >
      {/* Avatar */}
      <div className="relative">
        <div className="w-12 h-12 rounded-full bg-blue-500 flex items-center justify-center text-white font-medium text-lg">
          {otherUser?.avatar ? (
            <img
              src={otherUser.avatar}
              alt={otherUser.full_name || "User"}
              className="w-full h-full rounded-full object-cover"
            />
          ) : (
            (otherUser?.full_name || "U").charAt(0).toUpperCase()
          )}
        </div>
        {hasUnread && (
          <span className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 text-white text-xs font-bold rounded-full flex items-center justify-center">
            {conversation.unread_count}
          </span>
        )}
      </div>

      {/* Conversation Info */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center justify-between mb-1">
          <h3 className={`font-medium truncate ${hasUnread ? "text-gray-900" : "text-gray-700"}`}>
            {otherUser?.full_name || "Unknown User"}
          </h3>
          {lastMessage && (
            <span className="text-xs text-gray-500">
              {formatTimeAgo(lastMessage.created_at)}
            </span>
          )}
        </div>

        {lastMessage && (
          <p className={`text-sm truncate ${hasUnread ? "text-gray-700 font-medium" : "text-gray-500"}`}>
            {lastMessage.content}
          </p>
        )}
      </div>
    </Link>
  );
}

export function ConversationList({
  conversations,
  isLoading = false,
}: ConversationListProps): React.ReactElement {
  if (isLoading) {
    return (
      <div className="space-y-4">
        {[1, 2, 3].map((i) => (
          <div key={i} className="flex items-center gap-4 p-4 animate-pulse">
            <div className="w-12 h-12 bg-gray-200 rounded-full" />
            <div className="flex-1 space-y-2">
              <div className="h-4 bg-gray-200 rounded w-1/3" />
              <div className="h-3 bg-gray-200 rounded w-2/3" />
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (conversations.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-12 text-center">
        <svg
          className="w-16 h-16 text-gray-300 mb-4"
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
        <h3 className="text-lg font-medium text-gray-900 mb-1">No conversations yet</h3>
        <p className="text-gray-500">
          When recruiters contact you, your conversations will appear here.
        </p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200">
      {conversations.map((conversation) => (
        <ConversationItem key={conversation.id} conversation={conversation} />
      ))}
    </div>
  );
}
