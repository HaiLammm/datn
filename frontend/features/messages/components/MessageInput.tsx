"use client";

import React, { useState, useRef, useCallback } from "react";

interface MessageInputProps {
  onSend: (content: string) => void;
  onTyping?: () => void; // Updated to use with useTypingIndicator
  onStopTyping?: () => void; // Renamed for clarity
  disabled?: boolean;
  placeholder?: string;
  maxLength?: number;
}

/**
 * MessageInput component - Text input with send functionality
 *
 * Features:
 * - Auto-resizing textarea
 * - Send on Enter (Shift+Enter for newline)
 * - Typing indicators
 * - Character count
 * - Disabled state when disconnected
 */
export function MessageInput({
  onSend,
  onTyping,
  onStopTyping,
  disabled = false,
  placeholder = "Nhập tin nhắn...",
  maxLength = 5000,
}: MessageInputProps) {
  const [message, setMessage] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const typingTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  // Auto-resize textarea height
  const adjustHeight = useCallback(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = "auto";
      textarea.style.height = `${Math.min(textarea.scrollHeight, 150)}px`;
    }
  }, []);

  // Handle typing indicator
  const handleTyping = useCallback(() => {
    if (!isTyping) {
      setIsTyping(true);
      onTyping?.();
    }

    // Clear existing timeout
    if (typingTimeoutRef.current) {
      clearTimeout(typingTimeoutRef.current);
    }

    // Set timeout to stop typing indicator (3 seconds for consistency)
    typingTimeoutRef.current = setTimeout(() => {
      setIsTyping(false);
      onStopTyping?.();
    }, 3000);
  }, [isTyping, onTyping, onStopTyping]);

  // Handle input change
  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const value = e.target.value;
    if (value.length <= maxLength) {
      setMessage(value);
      adjustHeight();
      handleTyping();
    }
  };

  // Handle send
  const handleSend = () => {
    const trimmedMessage = message.trim();
    if (trimmedMessage && !disabled) {
      onSend(trimmedMessage);
      setMessage("");
      adjustHeight();

      // Stop typing indicator immediately
      setIsTyping(false);
      if (typingTimeoutRef.current) {
        clearTimeout(typingTimeoutRef.current);
      }
      onStopTyping?.();

      // Refocus textarea
      textareaRef.current?.focus();
    }
  };

  // Handle keyboard shortcuts
  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    // Send on Enter without Shift
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  // Handle paste to check size
  const handlePaste = (e: React.ClipboardEvent<HTMLTextAreaElement>) => {
    const pastedText = e.clipboardData.getData("text");
    const currentLength = message.length;

    if (currentLength + pastedText.length > maxLength) {
      e.preventDefault();
      const remaining = maxLength - currentLength;
      setMessage(message + pastedText.slice(0, remaining));
    }
  };

  // Cleanup typing timeout on unmount
  React.useEffect(() => {
    return () => {
      if (typingTimeoutRef.current) {
        clearTimeout(typingTimeoutRef.current);
      }
    };
  }, []);

  const remainingChars = maxLength - message.length;
  const isOverLimit = remainingChars < 0;

  return (
    <div className="border-t border-gray-200 p-3">
      {/* Typing indicator */}
      {isTyping && (
        <div className="text-xs text-gray-500 mb-1 animate-pulse">
          Typing...
        </div>
      )}

      <div className="flex items-end gap-2">
        {/* Textarea */}
        <div className="flex-1 relative">
          <textarea
            ref={textareaRef}
            value={message}
            onChange={handleChange}
            onKeyDown={handleKeyDown}
            onPaste={handlePaste}
            placeholder={placeholder}
            disabled={disabled}
            rows={1}
            className={`w-full px-4 py-2 border border-gray-300 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed ${
              isOverLimit ? "border-red-500" : ""
            }`}
            style={{
              minHeight: "44px",
              maxHeight: "150px",
            }}
          />

          {/* Character count */}
          {message.length > 0 && (
            <div
              className={`absolute bottom-1 right-2 text-xs ${
                remainingChars < 50 ? "text-orange-500" : "text-gray-400"
              } ${isOverLimit ? "text-red-500" : ""}`}
            >
              {remainingChars}
            </div>
          )}
        </div>

        {/* Send button */}
        <button
          onClick={handleSend}
          disabled={disabled || !message.trim()}
          className={`p-2 rounded-lg transition-colors ${
            disabled || !message.trim()
              ? "bg-gray-300 cursor-not-allowed"
              : "bg-blue-500 hover:bg-blue-600 text-white"
          }`}
          aria-label="Send message"
        >
          <svg
            className="w-5 h-5"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"
            />
          </svg>
        </button>
      </div>
    </div>
  );
}
