"use client";

import { Button } from "@/components/ui/button";
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
} from "@/components/ui/dialog";
import { JobDescriptionResponse, CVWithStatus } from "@datn/shared-types";
import { useState, useEffect } from "react";
import { getCVList } from "@/features/cv/actions";
import { applyJobAction } from "@/features/jobs/actions";
import { toast } from "sonner";
import { Textarea } from "@/components/ui/textarea";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Label } from "@/components/ui/label";
import Link from "next/link";

interface ApplyJobDialogProps {
    job: JobDescriptionResponse;
    trigger?: React.ReactNode;
}

export function ApplyJobDialog({ job, trigger }: ApplyJobDialogProps) {
    const [open, setOpen] = useState(false);
    const [cvs, setCvs] = useState<CVWithStatus[]>([]);
    const [loadingCVs, setLoadingCVs] = useState(false);
    const [selectedCV, setSelectedCV] = useState<string>("");
    const [coverLetter, setCoverLetter] = useState("");
    const [applying, setApplying] = useState(false);

    useEffect(() => {
        if (open) {
            fetchCVs();
        }
    }, [open]);

    const fetchCVs = async () => {
        setLoadingCVs(true);
        try {
            const data = await getCVList();
            setCvs(data);
            if (data.length > 0) {
                setSelectedCV(data[0].id);
            }
        } catch (error) {
            console.error(error);
            toast.error("Không thể tải danh sách CV. Vui lòng thử lại.");
        } finally {
            setLoadingCVs(false);
        }
    };

    const handleApply = async () => {
        if (!selectedCV) {
            toast.error("Vui lòng chọn một CV");
            return;
        }
        setApplying(true);
        try {
            const result = await applyJobAction(job.id, selectedCV, coverLetter);
            if (result.success) {
                toast.success("Ứng tuyển thành công!");
                setOpen(false);
            } else {
                toast.error(result.message || "Đã xảy ra lỗi khi ứng tuyển");
            }
        } catch (error: any) {
            console.error("Apply error:", error);
            toast.error("Đã xảy ra lỗi khi ứng tuyển");
        } finally {
            setApplying(false);
        }
    };

    return (
        <Dialog open={open} onOpenChange={setOpen}>
            <DialogTrigger asChild>
                {trigger || <Button size="lg">Ứng tuyển ngay</Button>}
            </DialogTrigger>
            <DialogContent className="sm:max-w-[500px] bg-white">
                <DialogHeader>
                    <DialogTitle>Ứng tuyển: {job.title}</DialogTitle>
                    <DialogDescription>
                        Chọn CV và gửi lời nhắn đến nhà tuyển dụng.
                    </DialogDescription>
                </DialogHeader>

                <div className="grid gap-4 py-4">
                    {/* CV Selection */}
                    <div className="space-y-3">
                        <Label>Chọn CV của bạn</Label>
                        {loadingCVs ? (
                            <p className="text-sm text-muted-foreground">Đang tải danh sách CV...</p>
                        ) : cvs.length === 0 ? (
                            <p className="text-red-500 text-sm">
                                Bạn chưa có CV nào.
                                <Link href="/profile/cvs" className="underline ml-1 font-medium">Tải lên ngay</Link>
                            </p>
                        ) : (
                            <RadioGroup value={selectedCV} onValueChange={setSelectedCV} className="max-h-40 overflow-y-auto">
                                {cvs.map(cv => (
                                    <div key={cv.id} className="flex items-center space-x-2 border p-2 rounded hover:bg-slate-50">
                                        <RadioGroupItem value={cv.id} id={cv.id} />
                                        <Label htmlFor={cv.id} className="cursor-pointer flex-1 text-sm font-normal">
                                            <span className="font-medium">{cv.filename}</span>
                                            <span className="block text-xs text-muted-foreground">
                                                {new Date(cv.uploaded_at).toLocaleDateString('vi-VN')}
                                            </span>
                                        </Label>
                                    </div>
                                ))}
                            </RadioGroup>
                        )}
                    </div>

                    {/* Cover Letter */}
                    <div className="space-y-2">
                        <Label>Thư giới thiệu (Không bắt buộc)</Label>
                        <Textarea
                            placeholder="Viết đôi lời giới thiệu về bản thân..."
                            value={coverLetter}
                            onChange={e => setCoverLetter(e.target.value)}
                            className="min-h-[100px]"
                        />
                    </div>
                </div>

                <DialogFooter>
                    <Button variant="outline" onClick={() => setOpen(false)}>Hủy</Button>
                    <Button onClick={handleApply} disabled={applying || cvs.length === 0 || !selectedCV}>
                        {applying ? "Đang gửi..." : "Gửi hồ sơ"}
                    </Button>
                </DialogFooter>
            </DialogContent>
        </Dialog>
    );
}
