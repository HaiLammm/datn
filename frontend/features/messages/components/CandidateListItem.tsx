"use client";

import React, { useState } from "react";

interface Candidate {
  id: number;
  full_name: string;
  email: string;
  avatar?: string;
  role?: string;
  match_score?: number;
  applied_at?: string;
}

interface CandidateListItemProps {
  candidate: Candidate;
  onStartChat: (candidateId: number) => Promise<void>;
  isLoading?: boolean;
}

/**
 * CandidateListItem component - Displays candidate card with "Start Chat" button
 *
 * Used on the applicants page for recruiters to initiate conversations.
 */
export function CandidateListItem({
  candidate,
  onStartChat,
  isLoading = false,
}: CandidateListItemProps) {
  const [isStartingChat, setIsStartingChat] = useState(false);

  const handleStartChat = async () => {
    setIsStartingChat(true);
    try {
      await onStartChat(candidate.id);
    } finally {
      setIsStartingChat(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-4 hover:shadow-lg transition-shadow">
      <div className="flex items-start gap-4">
        {/* Avatar */}
        <div className="flex-shrink-0">
          <div className="w-12 h-12 rounded-full bg-blue-500 flex items-center justify-center text-white font-medium text-lg">
            {candidate.avatar ? (
              <img
                src={candidate.avatar}
                alt={candidate.full_name}
                className="w-full h-full rounded-full object-cover"
              />
            ) : (
              candidate.full_name.charAt(0).toUpperCase()
            )}
          </div>
        </div>

        {/* Info */}
        <div className="flex-1 min-w-0">
          <h3 className="font-medium text-gray-900 truncate">
            {candidate.full_name}
          </h3>
          <p className="text-sm text-gray-500 truncate">{candidate.email}</p>

          {/* Role and Match Score */}
          <div className="flex items-center gap-2 mt-2">
            {candidate.role && (
              <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-800">
                {candidate.role}
              </span>
            )}

            {candidate.match_score !== undefined && (
              <span
                className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${
                  candidate.match_score >= 80
                    ? "bg-green-100 text-green-800"
                    : candidate.match_score >= 60
                    ? "bg-yellow-100 text-yellow-800"
                    : "bg-red-100 text-red-800"
                }`}
              >
                {candidate.match_score}% match
              </span>
            )}

            {candidate.applied_at && (
              <span className="text-xs text-gray-400">
                Applied {new Date(candidate.applied_at).toLocaleDateString()}
              </span>
            )}
          </div>
        </div>

        {/* Start Chat Button */}
        <div className="flex-shrink-0">
          <button
            onClick={handleStartChat}
            disabled={isLoading || isStartingChat}
            className={`inline-flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              isLoading || isStartingChat
                ? "bg-gray-300 cursor-not-allowed text-gray-500"
                : "bg-blue-500 hover:bg-blue-600 text-white"
            }`}
          >
            {isStartingChat ? (
              <>
                <svg
                  className="animate-spin w-4 h-4"
                  fill="none"
                  viewBox="0 0 24 24"
                >
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                  />
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                  />
                </svg>
                Starting...
              </>
            ) : (
              <>
                <svg
                  className="w-4 h-4"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
                  />
                </svg>
                Start Chat
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
