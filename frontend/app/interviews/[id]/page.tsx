import { notFound } from "next/navigation";
import { interviewService } from "@/services/interview.service";
import { InterviewRoom } from "@/features/interviews/components/InterviewRoom";
import { headers } from "next/headers";

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

export default async function InterviewPage({ params }: PageProps) {
    const accessToken = await getAccessToken();

    try {
        const session = await interviewService.getInterview(params.id, accessToken);

        if (!session) {
            notFound();
        }

        return (
            <div className="container py-10">
                <InterviewRoom initialSession={session} />
            </div>
        );
    } catch (error) {
        console.error("Error loading interview:", error);
        notFound();
    }
}
