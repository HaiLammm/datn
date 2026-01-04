// Story 7.3: Types for conversation list with enhanced data
export interface UserBasicInfo {
  id: number;
  name: string;
  avatar?: string;
  role: string;
}

export interface MessagePreview {
  content: string;
  timestamp: string;
  sender_id: number;
}

export interface ConversationListItem {
  conversation_id: string;
  other_participant: UserBasicInfo;
  last_message?: MessagePreview;
  unread_count: number;
  updated_at: string;
}

export interface ConversationUpdatedEvent {
  conversation_id: string;
  last_message: MessagePreview;
  unread_count: number;
  updated_at: string;
}