"use server";

import { cookies } from "next/headers";
import { redirect } from "next/navigation";

interface ConversationResponse {
  id: string;
  recruiter_id: number;
  candidate_id: number;
  created_at: string;
  updated_at: string;
}

interface CreateConversationRequest {
  candidate_id: number;
  initial_message: string;
}

/**
 * Server action to create a new conversation
 *
 * @param candidateId - ID of the candidate to start conversation with
 * @param initialMessage - First message content
 * @returns Conversation ID or throws error
 */
export async function createConversation(
  candidateId: number,
  initialMessage: string
): Promise<string> {
  try {
    const cookieStore = await cookies();
    const token = cookieStore.get("access_token")?.value;

    if (!token) {
      throw new Error("Authentication required");
    }

    const response = await fetch(
      `${process.env.NEXT_PUBLIC_API_URL}/api/v1/messages/conversations`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          candidate_id: candidateId,
          initial_message: initialMessage,
        } as CreateConversationRequest),
      }
    );

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || "Failed to create conversation");
    }

    const data: ConversationResponse = await response.json();
    return data.id;
  } catch (error) {
    console.error("Error creating conversation:", error);
    throw error;
  }
}

/**
 * Server action to navigate to a conversation
 *
 * @param conversationId - ID of the conversation to navigate to
 */
export async function navigateToConversation(conversationId: string): Promise<void> {
  redirect(`/messages/${conversationId}`);
}

/**
 * Server action to fetch conversation details
 *
 * @param conversationId - ID of the conversation
 * @returns Conversation details or null
 */
export async function getConversation(
  conversationId: string
): Promise<ConversationResponse | null> {
  try {
    const cookieStore = await cookies();
    const token = cookieStore.get("access_token")?.value;

    if (!token) {
      return null;
    }

    const response = await fetch(
      `${process.env.NEXT_PUBLIC_API_URL}/api/v1/messages/conversations/${conversationId}`,
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );

    if (!response.ok) {
      if (response.status === 404) {
        return null;
      }
      throw new Error("Failed to fetch conversation");
    }

    return await response.json();
  } catch (error) {
    console.error("Error fetching conversation:", error);
    return null;
  }
}
