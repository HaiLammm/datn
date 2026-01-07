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
    console.log("🔐 Getting authentication token...");
    const cookieStore = await cookies();
    const token = cookieStore.get("access_token")?.value;

    if (!token) {
      console.error("❌ No authentication token found");
      throw new Error("Authentication required");
    }

    console.log("📡 Sending POST request to create conversation");
    console.log("   Candidate ID:", candidateId);
    console.log("   API URL:", `${process.env.NEXT_PUBLIC_API_URL}/api/v1/messages/conversations`);

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

    console.log("📥 Response status:", response.status);

    if (!response.ok) {
      const error = await response.json();
      console.error("❌ API error:", error);
      throw new Error(error.detail || "Failed to create conversation");
    }

    const data: ConversationResponse = await response.json();
    console.log("✅ Conversation created successfully:", data.id);
    return data.id;
  } catch (error) {
    console.error("❌ Error creating conversation:", error);
    throw error;
  }
}

/**
 * Server action to navigate to a conversation
 * 
 * ⚠️ DEPRECATED: Don't use this function from client components!
 * Next.js redirect() throws NEXT_REDIRECT error when awaited in client.
 * Use router.push() instead from client components.
 *
 * @param conversationId - ID of the conversation to navigate to
 */
export async function navigateToConversation(conversationId: string): Promise<void> {
  console.log("🔄 Redirecting to:", `/messages/${conversationId}`);
  redirect(`/messages/${conversationId}`);
}

/**
 * Server action to fetch conversation list
 *
 * @returns List of conversations or empty array
 */
export async function getConversations(): Promise<any[]> {
  try {
    const cookieStore = await cookies();
    const token = cookieStore.get("access_token")?.value;

    console.log("🔍 getConversations - Token exists:", !!token);
    console.log("🔍 getConversations - Token length:", token?.length);
    console.log("🔍 getConversations - API URL:", process.env.NEXT_PUBLIC_API_URL);

    if (!token) {
      console.log("❌ No token found, redirecting to login");
      redirect("/login");
    }

    const apiUrl = `${process.env.NEXT_PUBLIC_API_URL}/api/v1/messages/conversations`;
    console.log("🔍 Fetching conversations from:", apiUrl);

    const response = await fetch(apiUrl, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
      cache: 'no-store', // Always fetch fresh data
    });

    console.log("🔍 Response status:", response.status);
    console.log("🔍 Response ok:", response.ok);

    if (!response.ok) {
      const errorText = await response.text();
      console.error("❌ API Error:", response.status, errorText);
      
      if (response.status === 401 || response.status === 403) {
        console.log("❌ Auth failed, redirecting to login");
        redirect("/login");
      }
      throw new Error("Failed to fetch conversations");
    }

    const data = await response.json();
    console.log("✅ Conversations fetched:", data.length, "items");
    return data;
  } catch (error) {
    console.error("❌ Error fetching conversations:", error);
    throw error;
  }
}

/**
 * Server action to find existing conversation with a candidate
 * 
 * @param candidateId - ID of the candidate
 * @returns Conversation ID if exists, null if not found
 */
export async function findExistingConversation(candidateId: number): Promise<string | null> {
  try {
    const conversations = await getConversations();
    
    // Find conversation where other participant is the candidate
    const conversation = conversations.find((conv: any) => {
      return conv.other_participant?.id === candidateId;
    });
    
    return conversation ? conversation.conversation_id : null;
  } catch (error) {
    console.error("Error finding conversation:", error);
    return null;
  }
}

/**
 * Server action to mark conversation as read
 *
 * @param conversationId - ID of the conversation to mark as read
 */
export async function markConversationAsRead(conversationId: string): Promise<void> {
  try {
    const cookieStore = await cookies();
    const token = cookieStore.get("access_token")?.value;

    if (!token) {
      return;
    }

    const response = await fetch(
      `${process.env.NEXT_PUBLIC_API_URL}/api/v1/messages/conversations/${conversationId}/mark-read`,
      {
        method: 'PATCH',
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );

    if (!response.ok && response.status !== 404) {
      console.error("Failed to mark conversation as read");
    }
  } catch (error) {
    console.error("Error marking conversation as read:", error);
  }
}

/**
 * Server action to fetch conversation messages
 *
 * @param conversationId - ID of the conversation
 * @param limit - Number of messages to fetch
 * @param before - Fetch messages before this timestamp (for pagination)
 * @returns List of messages or empty array
 */
export async function getConversationMessages(
  conversationId: string,
  limit: number = 50,
  before?: string
): Promise<any> {
  try {
    const cookieStore = await cookies();
    const token = cookieStore.get("access_token")?.value;

    if (!token) {
      redirect("/login");
    }

    const url = new URL(
      `${process.env.NEXT_PUBLIC_API_URL}/api/v1/messages/conversations/${conversationId}/messages`
    );
    url.searchParams.set("limit", limit.toString());
    if (before) {
      url.searchParams.set("before", before);
    }

    const response = await fetch(url.toString(), {
      headers: {
        Authorization: `Bearer ${token}`,
      },
      cache: 'no-store',
    });

    if (!response.ok) {
      if (response.status === 401 || response.status === 403) {
        redirect("/login");
      }
      throw new Error("Failed to fetch messages");
    }

    return await response.json();
  } catch (error) {
    console.error("Error fetching messages:", error);
    throw error;
  }
}

/**
 * Server action to get conversation details with current user context
 *
 * @param conversationId - ID of the conversation
 * @returns Conversation details with other user info and current user ID
 */
export async function getConversationWithContext(conversationId: string): Promise<any> {
  try {
    const cookieStore = await cookies();
    const token = cookieStore.get("access_token")?.value;

    if (!token) {
      redirect("/login");
    }

    // Decode token to get current user ID
    const { jwtDecode } = await import('jwt-decode');
    const decoded: any = jwtDecode(token);
    const currentUserId = Number(decoded.user_id || decoded.sub);

    const response = await fetch(
      `${process.env.NEXT_PUBLIC_API_URL}/api/v1/messages/conversations/${conversationId}`,
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
        cache: 'no-store',
      }
    );

    if (!response.ok) {
      const errorBody = await response.text();
      console.error(`[getConversationWithContext] HTTP ${response.status}:`, errorBody);
      
      if (response.status === 401 || response.status === 403) {
        redirect("/login");
      }
      if (response.status === 404) {
        return null;
      }
      throw new Error(`Failed to fetch conversation: ${response.status} - ${errorBody}`);
    }

    const convData = await response.json();
    
    // Add current user ID and determine other user
    return {
      ...convData,
      currentUserId,
      otherUserId: currentUserId === convData.recruiter_id 
        ? convData.candidate_id 
        : convData.recruiter_id
    };
  } catch (error) {
    console.error("Error fetching conversation:", error);
    throw error;
  }
}

/**
 * Server action to get conversation details
 *
 * @param conversationId - ID of the conversation
 * @returns Conversation details with other user info
 */
export async function getConversationDetails(conversationId: string): Promise<any> {
  try {
    const cookieStore = await cookies();
    const token = cookieStore.get("access_token")?.value;

    if (!token) {
      redirect("/login");
    }

    const response = await fetch(
      `${process.env.NEXT_PUBLIC_API_URL}/api/v1/messages/conversations/${conversationId}`,
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
        cache: 'no-store',
      }
    );

    if (!response.ok) {
      if (response.status === 401 || response.status === 403) {
        redirect("/login");
      }
      if (response.status === 404) {
        return null;
      }
      throw new Error("Failed to fetch conversation");
    }

    return await response.json();
  } catch (error) {
    console.error("Error fetching conversation:", error);
    throw error;
  }
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
