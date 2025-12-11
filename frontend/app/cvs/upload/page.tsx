import { CVUploadForm } from "@/features/cv/components/CVUploadForm";
import { cookies } from "next/headers";
import { redirect } from "next/navigation";

export default async function CVUploadPage() {
  // Authentication Guard: Protect the page from unauthenticated access.
  const cookieStore = await cookies();
  const accessToken = cookieStore.get("access_token")?.value;

  if (!accessToken) {
    redirect("/login");
  }

  return (
    <div className="flex min-h-screen flex-col items-center justify-center p-4">
      <div className="w-full max-w-md">
        <CVUploadForm />
      </div>
    </div>
  );
}
