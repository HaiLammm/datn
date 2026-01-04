"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { toast } from "sonner";

interface UnreadCountResponse {
  unread_count: number;
}

export function MessageNotification() {
  const router = useRouter();
  const [hasChecked, setHasChecked] = useState(false);

  useEffect(() => {
    const checkUnreadMessages = async () => {
      // Only check once per session
      if (hasChecked) return;
      setHasChecked(true);

      try {
        const token = document.cookie
          .split("; ")
          .find((row) => row.startsWith("access_token="))
          ?.split("=")[1];

        if (!token) return;

        const response = await fetch(
          `${process.env.NEXT_PUBLIC_API_URL}/api/v1/messages/conversations/unread-count`,
          {
            headers: { Authorization: `Bearer ${token}` },
          }
        );

        if (response.ok) {
          const data: UnreadCountResponse = await response.json();

          if (data.unread_count > 0) {
            const message =
              data.unread_count === 1
                ? "You have 1 new message"
                : `You have ${data.unread_count} new messages`;

            toast(message, {
              action: {
                label: "View Messages",
                onClick: () => router.push("/messages"),
              },
              duration: 8000,
            });
          }
        }
      } catch (error) {
        console.error("Failed to check unread messages:", error);
      }
    };

    // Small delay to ensure app is loaded
    const timer = setTimeout(checkUnreadMessages, 1000);

    return () => clearTimeout(timer);
  }, [router, hasChecked]);

  return null;
}
