"use client";

import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { MessageSquare } from "lucide-react";
import { useState } from "react";

export function SafeMessagesButton() {
  const router = useRouter();
  const [isChecking, setIsChecking] = useState(false);

  const navigateToMessages = async () => {
    setIsChecking(true);
    
    try {
      console.log('🔍 SafeMessagesButton - Navigating to messages...');
      
      // Just navigate - layout will handle auth check
      // No need to refresh token if user is already logged in
      router.push('/messages');
    } catch (error) {
      console.error('❌ Error navigating:', error);
    } finally {
      setIsChecking(false);
    }
  };

  return (
    <Button 
      onClick={navigateToMessages}
      variant="outline"
      className="flex-1"
      disabled={isChecking}
      data-testid="safe-messages-button"
    >
      <MessageSquare className="h-4 w-4 mr-2" />
      {isChecking ? "Checking..." : "Messages (Safe)"}
    </Button>
  );
}