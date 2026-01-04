"use client";

import React, { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { ConversationList } from "@/features/messages/components/ConversationList";
import { getClientSession } from "@/lib/auth-client";

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

interface User {
  id: string;
  email: string;
  role: string;
  full_name?: string;
}

export default function MessagesPage(): React.ReactElement {
  const router = useRouter();
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchConversations = async () => {
      try {
        // Get current user
        const session = getClientSession();
        if (!session?.user) {
          router.push("/login");
          return;
        }
        setCurrentUser(session.user);

        // Get auth token
        const token = document.cookie
          .split("; ")
          .find((row) => row.startsWith("access_token="))
          ?.split("=")[1];

        if (!token) {
          router.push("/login");
          return;
        }

        // Fetch conversations
        const response = await fetch(
          `${process.env.NEXT_PUBLIC_API_URL}/api/v1/messages/conversations`,
          {
            headers: { Authorization: `Bearer ${token}` },
          }
        );

        if (!response.ok) {
          throw new Error("Failed to fetch conversations");
        }

        const data: Conversation[] = await response.json();

        // For each conversation, we need to get the other user's info
        // This would typically be done via a joined query, but for now
        // we'll fetch user details separately or use the existing data
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

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-2xl mx-auto">
          <div className="flex items-center justify-between mb-6">
            <h1 className="text-2xl font-bold text-gray-900">Messages</h1>
          </div>

          <ConversationList conversations={conversations} />
        </div>
      </div>
    </div>
  );
}
