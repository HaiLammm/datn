import { InterviewSetupForm } from "@/features/interviews/components/InterviewSetupForm";
import { getCVListAction } from "@/features/interviews/actions";
import { Metadata } from "next";

export const metadata: Metadata = {
    title: "Interview Setup - AI Recruitment Platform",
    description: "Setup your virtual interview session",
};

export default async function InterviewSetupPage() {
    const cvList = await getCVListAction();

    return (
        <div className="container py-10">
            <div className="max-w-4xl mx-auto space-y-8">
                <div className="text-center space-y-2">
                    <h1 className="text-3xl font-bold tracking-tight">Virtual Interview Room</h1>
                    <p className="text-muted-foreground">
                        Configure your interview settings. Choose a CV and Job Description to get personalized questions.
                    </p>
                </div>

                <InterviewSetupForm cvList={cvList} />
            </div>
        </div>
    );
}
