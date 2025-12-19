import { redirect } from "next/navigation";
import Link from "next/link";
import { Home, FileText } from "lucide-react";
import { getSession, canAccessCVs, getDefaultRedirect } from "@/lib/auth";

export default async function CVsLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  // Get session and check role-based access
  const session = await getSession();
  
  if (!session) {
    redirect("/login");
  }
  
  // Check if user can access CV features
  if (!canAccessCVs(session.user.role)) {
    // Redirect to appropriate section based on role
    redirect(getDefaultRedirect(session.user.role));
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation Header */}
      <nav className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="container mx-auto px-4">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-6">
              <Link
                href="/dashboard"
                className="flex items-center gap-2 text-gray-600 hover:text-gray-900 transition-colors"
              >
                <Home className="h-5 w-5" />
                <span className="hidden sm:inline">Dashboard</span>
              </Link>
              <Link
                href="/cvs"
                className="flex items-center gap-2 text-blue-600 font-medium"
              >
                <FileText className="h-5 w-5" />
                <span>My CVs</span>
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main>{children}</main>
    </div>
  );
}
