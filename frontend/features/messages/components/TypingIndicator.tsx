"use client";

import React, { useEffect, useState } from 'react';

interface TypingUser {
  id: string;
  name: string;
}

interface TypingIndicatorProps {
  typingUser: TypingUser | null;
}

export function TypingIndicator({ typingUser }: TypingIndicatorProps) {
  const [dots, setDots] = useState('...');

  // Animate dots
  useEffect(() => {
    if (!typingUser) return;

    const interval = setInterval(() => {
      setDots(prev => {
        if (prev === '...') return '.  ';
        if (prev === '.  ') return ' . ';
        if (prev === ' . ') return '  .';
        return '...';
      });
    }, 500);

    return () => clearInterval(interval);
  }, [typingUser]);

  if (!typingUser) return null;

  return (
    <div className="flex items-center gap-2 px-4 py-2 text-sm text-gray-500 italic transition-opacity duration-200 bg-gray-50">
      <div className="flex space-x-1">
        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
      </div>
      <span>{typingUser.name} đang nhập{dots}</span>
    </div>
  );
}