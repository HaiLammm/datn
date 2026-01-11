import { notFound } from "next/navigation";
import { headers } from "next/headers";
import Link from "next/link";
import { interviewService } from "@/services/interview.service";
import { EvaluationReport } from "@/features/interviews/components/EvaluationReport";
import { TranscriptReview } from "@/features/interviews/components/TranscriptReview";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

async function getAccessToken(): Promise<string> {
    const headersList = await headers();
    const cookieHeader = headersList.get("cookie") || "";
    const cookies = cookieHeader.split(";").map((c) => c.trim());
    const accessTokenCookie = cookies.find((c) => c.startsWith("access_token="));
    return accessTokenCookie ? accessTokenCookie.split("=")[1] : "";
}

interface PageProps {
    params: {
        id: string;
    };
}

export default async function EvaluationPage({ params }: PageProps) {
    const accessToken = await getAccessToken();

    try {
        // Fetch session and evaluation data
        const [session, evaluation] = await Promise.all([
            interviewService.getInterview(params.id, accessToken),
            interviewService.getEvaluation(params.id, accessToken),
        ]);

        if (!session || !evaluation) {
            notFound();
        }

        return (
            <div className="container py-10">
                <div className="mb-6">
                    <Link href={`/interviews/${params.id}`}>
                        <Button variant="outline">← Back to Interview</Button>
                    </Link>
                </div>

                <Tabs defaultValue="evaluation" className="w-full">
                    <TabsList className="grid w-full grid-cols-2 max-w-md">
                        <TabsTrigger value="evaluation">Evaluation Report</TabsTrigger>
                        <TabsTrigger value="transcript">Transcript Review</TabsTrigger>
                    </TabsList>
                    
                    <TabsContent value="evaluation" className="mt-6">
                        <EvaluationReport
                            session={session}
                            evaluation={evaluation}
                        />
                    </TabsContent>
                    
                    <TabsContent value="transcript" className="mt-6">
                        <TranscriptReview
                            turns={session.turns}
                            questions={session.questions}
                        />
                    </TabsContent>
                </Tabs>
            </div>
        );
    } catch (error: any) {
        console.error("Error loading evaluation:", error);
        
        // Check if evaluation doesn't exist yet
        if (error.response?.status === 404 || error.message?.includes("not found")) {
            return (
                <div className="container py-10">
                    <Card>
                        <CardContent className="py-10">
                            <div className="text-center space-y-4">
                                <h1 className="text-2xl font-bold">Evaluation Not Available</h1>
                                <p className="text-muted-foreground">
                                    This interview hasn't been completed yet. Please complete the interview first to generate an evaluation report.
                                </p>
                                <Link href={`/interviews/${params.id}`}>
                                    <Button>Go to Interview</Button>
                                </Link>
                            </div>
                        </CardContent>
                    </Card>
                </div>
            );
        }
        
        notFound();
    }
}
