"use client";

import React, { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useParams } from "next/navigation";
import { CandidateListItem } from "@/features/messages/components/CandidateListItem";
import { createConversation, navigateToConversation } from "@/features/messages/actions";
import { getClientSession } from "@/lib/auth-client";

interface Applicant {
  id: number;
  full_name: string;
  email: string;
  avatar?: string;
  role?: string;
  match_score?: number;
  applied_at: string;
}

interface JobDetails {
  id: string;
  title: string;
  company?: string;
}

interface PageProps {
  // Params are handled by useParams in client components
}

/**
 * Applicants page - Displays list of candidates who applied to a job
 *
 * Features:
 * - List of applicants with match scores
 * - "Start Chat" button for each candidate
 * - Navigation to chat after starting conversation
 */
export default function ApplicantsPage() {
  const params = useParams();
  const jdId = params.jdId as string;
  const router = useRouter();

  const [applicants, setApplicants] = useState<Applicant[]>([]);
  const [jobDetails, setJobDetails] = useState<JobDetails | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isRecruiter, setIsRecruiter] = useState(false);

  // Fetch job details and applicants
  useEffect(() => {
    const fetchData = async () => {
      try {
        // Check user role
        const session = getClientSession();
        if (!session?.user) {
          router.push("/login");
          return;
        }

        const userRole = session.user.role;
        if (userRole !== "recruiter" && userRole !== "admin") {
          router.push("/");
          return;
        }
        setIsRecruiter(true);

        // Fetch job details
        const token = document.cookie
          .split("; ")
          .find((row) => row.startsWith("access_token="))
          ?.split("=")[1];

        if (!token) {
          router.push("/login");
          return;
        }

        const jobResponse = await fetch(
          `${process.env.NEXT_PUBLIC_API_URL}/api/v1/jobs/jd/${jdId}`,
          {
            headers: { Authorization: `Bearer ${token}` },
          }
        );

        if (!jobResponse.ok) {
          throw new Error("Failed to fetch job details");
        }

        const jobData: JobDetails = await jobResponse.json();
        setJobDetails(jobData);

        // Fetch applicants
        const applicantsResponse = await fetch(
          `${process.env.NEXT_PUBLIC_API_URL}/api/v1/jobs/jd/${jdId}/applicants`,
          {
            headers: { Authorization: `Bearer ${token}` },
          }
        );

        if (applicantsResponse.ok) {
          const data = await applicantsResponse.json();
          setApplicants(data.applicants || []);
        } else {
          // If endpoint doesn't exist yet, show empty state
          setApplicants([]);
        }
      } catch (err) {
        console.error("Error fetching data:", err);
        setError(err instanceof Error ? err.message : "Failed to load data");
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, [jdId, router]);

  // Handle start chat
  const handleStartChat = async (candidateId: number) => {
    try {
      // Show a dialog to enter initial message
      const initialMessage = prompt(
        "Enter your first message to this candidate:"
      );

      if (!initialMessage || !initialMessage.trim()) {
        return;
      }

      // Create conversation
      const conversationId = await createConversation(
        candidateId,
        initialMessage.trim()
      );

      // Navigate to chat
      await navigateToConversation(conversationId);
    } catch (err) {
      console.error("Error starting chat:", err);
      alert(
        err instanceof Error ? err.message : "Failed to start conversation"
      );
    }
  };

  // Loading state
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <svg
            className="animate-spin w-10 h-10 mx-auto mb-4 text-blue-500"
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
          <p className="text-gray-600">Loading applicants...</p>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen">
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
            Unable to load applicants
          </h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={() => router.back()}
            className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
          >
            Go Back
          </button>
        </div>
      </div>
    );
  }

  // Main content
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-4xl mx-auto px-4 py-4">
          <button
            onClick={() => router.back()}
            className="flex items-center gap-2 text-gray-600 hover:text-gray-900 transition-colors mb-4"
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
                d="M10 19l-7-7m0 0l7-7m-7 7h18"
              />
            </svg>
            <span>Back to Job</span>
          </button>

          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              {jobDetails?.title || "Job Applicants"}
            </h1>
            <p className="text-gray-600 mt-1">
              {applicants.length} {applicants.length === 1 ? "applicant" : "applicants"}
            </p>
          </div>
        </div>
      </header>

      {/* Applicants List */}
      <main className="max-w-4xl mx-auto px-4 py-8">
        {applicants.length === 0 ? (
          <div className="text-center py-12">
            <svg
              className="w-16 h-16 mx-auto mb-4 text-gray-300"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={1.5}
                d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"
              />
            </svg>
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              No applicants yet
            </h3>
            <p className="text-gray-600">
              Candidates who apply to this job will appear here.
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {applicants.map((applicant) => (
              <CandidateListItem
                key={applicant.id}
                candidate={applicant}
                onStartChat={handleStartChat}
              />
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
