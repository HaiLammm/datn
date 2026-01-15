"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { Loader2 } from "lucide-react";

import { Button } from "@/components/ui/button";
import {
    Form,
    FormControl,
    FormDescription,
    FormField,
    FormItem,
    FormLabel,
    FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select";
import {
    Card,
    CardContent,
    CardDescription,
    CardFooter,
    CardHeader,
    CardTitle,
} from "@/components/ui/card";
import { toast } from "sonner";
import { createInterviewAction } from "../actions";
import { CVWithStatus } from "@datn/shared-types";

const formSchema = z.object({
    job_description: z.string().min(10, {
        message: "Job description must be at least 10 characters.",
    }),
    position_level: z.enum(["junior", "middle", "senior"]),
    num_questions: z.number().int().min(1).max(50),
    focus_areas: z.string().optional(),
    selected_cv_id: z.string().min(1, {
        message: "Please select a CV.",
    }),
});

interface InterviewSetupFormProps {
    cvList: CVWithStatus[];
}

export function InterviewSetupForm({ cvList }: InterviewSetupFormProps) {
    const router = useRouter();
    const [isLoading, setIsLoading] = useState(false);

    const form = useForm<z.infer<typeof formSchema>>({
        resolver: zodResolver(formSchema),
        defaultValues: {
            job_description: "",
            position_level: "middle",
            num_questions: 10,
            focus_areas: "",
            selected_cv_id: "",
        },
    });

    async function onSubmit(values: z.infer<typeof formSchema>) {
        setIsLoading(true);

        try {
            const formData = new FormData();
            formData.append("job_description", values.job_description);
            formData.append("cv_id", values.selected_cv_id);  // Send CV ID, not content
            formData.append("position_level", values.position_level);
            formData.append("num_questions", values.num_questions.toString());
            if (values.focus_areas) {
                formData.append("focus_areas", values.focus_areas);
            }

            const result = await createInterviewAction(null, formData);

            if (result.errors) {
                // Handle validation errors from server
                Object.keys(result.errors).forEach((key) => {
                    form.setError(key as any, {
                        type: "server",
                        message: result.errors![key]
                    });
                });
                toast.error("Please check the form for errors.");
                return;
            }

            if (result.message && !result.data) {
                toast.error(result.message);
                return;
            }

            toast.success("Interview session created! Redirecting...");

            // Redirect to the interview room
            if (result.data) {
                router.push(`/interviews/${result.data.session.id}`);
            }

        } catch (error) {
            toast.error("Something went wrong. Please try again.");
        } finally {
            setIsLoading(false);
        }
    }

    const handleCVChange = (cvId: string) => {
        const selectedCV = cvList.find(cv => cv.id === cvId);
        if (selectedCV) {
            form.setValue("selected_cv_id", cvId);
            // CV content will be fetched server-side when form is submitted
        }
    };

    return (
        <Card className="w-full max-w-2xl mx-auto">
            <CardHeader>
                <CardTitle>Interview Setup</CardTitle>
                <CardDescription>
                    Customize your practice interview session.
                </CardDescription>
            </CardHeader>
            <CardContent>
                <Form {...form}>
                    <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">

                        <FormField
                            control={form.control}
                            name="selected_cv_id"
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel>Select CV</FormLabel>
                                    <Select onValueChange={(val) => {
                                        field.onChange(val);
                                        handleCVChange(val);
                                    }} defaultValue={field.value}>
                                        <FormControl>
                                            <SelectTrigger>
                                                <SelectValue placeholder="Select a CV" />
                                            </SelectTrigger>
                                        </FormControl>
                                        <SelectContent>
                                            {cvList.map((cv) => (
                                                <SelectItem key={cv.id} value={cv.id}>
                                                    {cv.filename}
                                                </SelectItem>
                                            ))}
                                        </SelectContent>
                                    </Select>
                                    <FormMessage />
                                </FormItem>
                            )}
                        />

                        <FormField
                            control={form.control}
                            name="job_description"
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel>Job Description</FormLabel>
                                    <FormControl>
                                        <Textarea
                                            placeholder="Paste the job description here..."
                                            className="min-h-[150px]"
                                            {...field}
                                        />
                                    </FormControl>
                                    <FormMessage />
                                </FormItem>
                            )}
                        />

                        <div className="grid grid-cols-2 gap-4">
                            <FormField
                                control={form.control}
                                name="position_level"
                                render={({ field }) => (
                                    <FormItem>
                                        <FormLabel>Position Level</FormLabel>
                                        <Select onValueChange={field.onChange} defaultValue={field.value}>
                                            <FormControl>
                                                <SelectTrigger>
                                                    <SelectValue placeholder="Select level" />
                                                </SelectTrigger>
                                            </FormControl>
                                            <SelectContent>
                                                <SelectItem value="junior">Junior</SelectItem>
                                                <SelectItem value="middle">Middle</SelectItem>
                                                <SelectItem value="senior">Senior</SelectItem>
                                            </SelectContent>
                                        </Select>
                                        <FormMessage />
                                    </FormItem>
                                )}
                            />

                            <FormField
                                control={form.control}
                                name="num_questions"
                                render={({ field }) => (
                                    <FormItem>
                                        <FormLabel>Number of Questions</FormLabel>
                                        <Select
                                            onValueChange={(val) => field.onChange(parseInt(val))}
                                            defaultValue={field.value?.toString()}
                                        >
                                            <FormControl>
                                                <SelectTrigger>
                                                    <SelectValue placeholder="10" />
                                                </SelectTrigger>
                                            </FormControl>
                                            <SelectContent>
                                                <SelectItem value="5">5 Questions</SelectItem>
                                                <SelectItem value="10">10 Questions</SelectItem>
                                                <SelectItem value="15">15 Questions</SelectItem>
                                            </SelectContent>
                                        </Select>
                                        <FormMessage />
                                    </FormItem>
                                )}
                            />
                        </div>

                        <FormField
                            control={form.control}
                            name="focus_areas"
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel>Focus Areas (Optional)</FormLabel>
                                    <FormControl>
                                        <Input placeholder="e.g. React, System Design, Soft Skills" {...field} />
                                    </FormControl>
                                    <FormDescription>Comma separated list of topics.</FormDescription>
                                    <FormMessage />
                                </FormItem>
                            )}
                        />

                        <Button type="submit" className="w-full" disabled={isLoading}>
                            {isLoading ? (
                                <>
                                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                    Generating Interview...
                                </>
                            ) : (
                                "Start Interview"
                            )}
                        </Button>
                    </form>
                </Form>
            </CardContent>
        </Card>
    );
}
