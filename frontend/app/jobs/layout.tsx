import Link from "next/link";
import { Home, Briefcase } from "lucide-react";

export default function JobsLayout({
  children,
}: {
  children: React.ReactNode;
}) {
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
                href="/jobs"
                className="flex items-center gap-2 text-blue-600 font-medium"
              >
                <Briefcase className="h-5 w-5" />
                <span>Job Descriptions</span>
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
