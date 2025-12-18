"use client";

import { useState } from "react";
import Link from "next/link";
import { JobDescriptionResponse } from "@datn/shared-types";
import { JDCard } from "./JDCard";
import { Button } from "@/components/ui/button";
import { Plus, FileText } from "lucide-react";

interface JDListProps {
  initialJDs: JobDescriptionResponse[];
}

export function JDList({ initialJDs }: JDListProps) {
  const [jds, setJDs] = useState<JobDescriptionResponse[]>(initialJDs);

  const handleDelete = (deletedId: string) => {
    setJDs((prev) => prev.filter((jd) => jd.id !== deletedId));
  };

  if (jds.length === 0) {
    return (
      <div className="text-center py-12 px-4">
        <FileText className="h-16 w-16 text-gray-300 mx-auto mb-4" aria-hidden="true" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">
          Chưa có Job Description nào
        </h3>
        <p className="text-gray-500 mb-6">
          Hãy tạo JD đầu tiên để bắt đầu tìm kiếm ứng viên phù hợp!
        </p>
        <Link href="/jobs/jd/upload">
          <Button>
            <Plus className="h-4 w-4 mr-2" />
            Tạo JD đầu tiên
          </Button>
        </Link>
      </div>
    );
  }

  return (
    <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
      {jds.map((jd) => (
        <JDCard
          key={jd.id}
          jd={jd}
          onDelete={() => handleDelete(jd.id)}
        />
      ))}
    </div>
  );
}
