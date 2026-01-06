"use client";

import { useConversations } from '@/features/messages/contexts/ConversationContext';
import { ConversationListItem } from '@/types/messages';

export function MessagesBadge() {
  const { conversations } = useConversations();

  const totalUnread = conversations.reduce((sum: number, conv: ConversationListItem) => sum + (conv.unread_count || 0), 0);

  if (totalUnread === 0) return null;

  const displayCount = totalUnread > 99 ? '99+' : totalUnread.toString();

  return (
    <div className="absolute top-[-8px] right-[-8px] bg-red-500 text-white text-xs font-bold rounded-full min-w-[20px] h-5 flex items-center justify-center px-1.5 z-10">
      {displayCount}
    </div>
  );
}