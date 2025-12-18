import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import Link from "next/link";
import type { Metadata } from "next";
import { SemanticSearchPage } from "@/features/jobs/components/SemanticSearchPage";
import { Button } from "@/components/ui/button";
import { ArrowLeft, Search } from "lucide-react";

export const metadata: Metadata = {
  title: "Tim kiem ung vien - Jobs",
  description: "Tim kiem ung vien bang ngon ngu tu nhien",
};

export default async function SearchPage() {
  // Authentication Guard
  const cookieStore = await cookies();
  const accessToken = cookieStore.get("access_token")?.value;

  if (!accessToken) {
    redirect("/login");
  }

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="flex items-center gap-4 mb-8">
        <Link href="/jobs">
          <Button variant="ghost" size="icon" aria-label="Quay lai">
            <ArrowLeft className="h-5 w-5" />
          </Button>
        </Link>
        <div className="flex items-center gap-2">
          <Search className="h-6 w-6 text-primary" aria-hidden="true" />
          <h1 className="text-2xl font-bold text-gray-900">
            Tim kiem ung vien
          </h1>
        </div>
      </div>

      {/* Description */}
      <p className="text-muted-foreground mb-6 max-w-2xl">
        Nhap mo ta ung vien ban can tim bang ngon ngu tu nhien. Vi du: 
        &quot;Python developer voi 3 nam kinh nghiem AWS&quot; hoac 
        &quot;Frontend developer React, TypeScript&quot;
      </p>

      {/* Search Content */}
      <SemanticSearchPage />
    </div>
  );
}
