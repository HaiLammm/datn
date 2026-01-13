"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { interviewService } from "@/services/interview.service";
import { InterviewRoom } from "@/features/interviews/components/InterviewRoom";
import { InterviewSessionComplete } from "@/features/interviews/types";
import { Loader2 } from "lucide-react";

export default function InterviewPage() {
    const params = useParams();
    const router = useRouter();
    const [session, setSession] = useState<InterviewSessionComplete | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchInterview = async () => {
            try {
                setLoading(true);
                setError(null);
                
                // Client-side fetch - axios will automatically send HttpOnly cookies
                const data = await interviewService.getInterview(params.id as string);
                setSession(data);
            } catch (err: any) {
                console.error("Error loading interview:", err);
                setError(err.response?.data?.detail || "Failed to load interview session");
                
                // If 404, redirect to interviews list after 2 seconds
                if (err.response?.status === 404) {
                    setTimeout(() => router.push("/interviews"), 2000);
                }
            } finally {
                setLoading(false);
            }
        };

        if (params.id) {
            fetchInterview();
        }
    }, [params.id, router]);

    if (loading) {
        return (
            <div className="container py-10 flex items-center justify-center min-h-[400px]">
                <div className="flex flex-col items-center gap-4">
                    <Loader2 className="h-8 w-8 animate-spin text-primary" />
                    <p className="text-muted-foreground">Loading interview session...</p>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="container py-10 flex items-center justify-center min-h-[400px]">
                <div className="flex flex-col items-center gap-4 text-center max-w-md">
                    <div className="rounded-full bg-destructive/10 p-3">
                        <svg className="h-6 w-6 text-destructive" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                    </div>
                    <div>
                        <h2 className="text-2xl font-bold mb-2">Interview Not Found</h2>
                        <p className="text-muted-foreground mb-4">{error}</p>
                        <p className="text-sm text-muted-foreground">Redirecting to interviews list...</p>
                    </div>
                </div>
            </div>
        );
    }

    if (!session) {
        return null;
    }

    return (
        <div className="container py-10">
            <InterviewRoom initialSession={session} />
        </div>
    );
}
