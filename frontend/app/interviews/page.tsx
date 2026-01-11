import { redirect } from "next/navigation";
import Link from "next/link";
import { getSession } from "@/lib/auth";
import { listInterviewsAction } from "@/features/interviews/actions";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { MessageSquare, Plus, Clock, CheckCircle2, XCircle, FileText } from "lucide-react";
import type { InterviewSession } from "@/features/interviews/types";

export default async function InterviewsPage() {
  const session = await getSession();
  
  if (!session) {
    redirect("/login");
  }

  // Use Server Action to fetch interviews
  const result = await listInterviewsAction(20, 0);
  const interviews: InterviewSession[] = result.data?.sessions || [];
  const error: string | null = result.error || null;

  return (
    <main className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4 max-w-6xl">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">My Interviews</h1>
            <p className="text-gray-600 mt-2">
              Practice sessions and performance evaluations
            </p>
          </div>
          <Button asChild>
            <Link href="/interviews/new">
              <Plus className="h-4 w-4 mr-2" />
              New Interview
            </Link>
          </Button>
        </div>

        {/* Error State */}
        {error && (
          <Card className="border-red-200 bg-red-50">
            <CardContent className="py-6">
              <p className="text-red-800">{error}</p>
            </CardContent>
          </Card>
        )}

        {/* Empty State */}
        {!error && interviews.length === 0 && (
          <Card>
            <CardContent className="py-12 text-center">
              <MessageSquare className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                No interviews yet
              </h3>
              <p className="text-gray-600 mb-6">
                Start your first practice interview to get personalized feedback
              </p>
              <Button asChild>
                <Link href="/interviews/new">
                  <Plus className="h-4 w-4 mr-2" />
                  Start Practice Interview
                </Link>
              </Button>
            </CardContent>
          </Card>
        )}

        {/* Interviews List */}
        {!error && interviews.length > 0 && (
          <div className="space-y-4">
            {interviews.map((interview: any) => (
              <Card key={interview.id} className="hover:shadow-md transition-shadow">
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <CardTitle className="text-xl mb-2">
                        {interview.position_level.charAt(0).toUpperCase() + 
                         interview.position_level.slice(1)} Level Interview
                      </CardTitle>
                      <CardDescription>
                        {interview.focus_areas && (
                          <span className="text-sm">
                            Focus: {interview.focus_areas}
                          </span>
                        )}
                      </CardDescription>
                    </div>
                    <InterviewStatusBadge status={interview.status} />
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-6 text-sm text-gray-600">
                      <div className="flex items-center gap-2">
                        <MessageSquare className="h-4 w-4" />
                        <span>{interview.current_question_index || 0} / {interview.total_questions || 0} questions</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <Clock className="h-4 w-4" />
                        <span>{new Date(interview.created_at).toLocaleDateString()}</span>
                      </div>
                    </div>
                    
                    <div className="flex items-center gap-2">
                      {interview.status === "completed" && (
                        <Button asChild variant="outline" size="sm">
                          <Link href={`/interviews/${interview.id}/evaluation`}>
                            <FileText className="h-4 w-4 mr-2" />
                            View Report
                          </Link>
                        </Button>
                      )}
                      <Button asChild variant={interview.status === "completed" ? "outline" : "default"} size="sm">
                        <Link href={`/interviews/${interview.id}`}>
                          {interview.status === "completed" ? "Review" : "Continue"}
                        </Link>
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </main>
  );
}

function InterviewStatusBadge({ status }: { status: string }) {
  const statusConfig = {
    pending: {
      label: "Not Started",
      className: "bg-gray-100 text-gray-800",
      icon: Clock,
    },
    in_progress: {
      label: "In Progress",
      className: "bg-blue-100 text-blue-800",
      icon: MessageSquare,
    },
    completed: {
      label: "Completed",
      className: "bg-green-100 text-green-800",
      icon: CheckCircle2,
    },
    failed: {
      label: "Failed",
      className: "bg-red-100 text-red-800",
      icon: XCircle,
    },
  };

  const config = statusConfig[status as keyof typeof statusConfig] || statusConfig.pending;
  const Icon = config.icon;

  return (
    <Badge className={config.className} variant="secondary">
      <Icon className="h-3 w-3 mr-1" />
      {config.label}
    </Badge>
  );
}
