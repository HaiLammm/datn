import { redirect } from "next/navigation";
import Link from "next/link";
import { Home, MessageSquare } from "lucide-react";
import { getSession, canAccessMessages, getDefaultRedirect } from "@/lib/auth";

export default async function MessagesLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  console.log("🔍 Messages Layout - Checking session...");
  const session = await getSession();
  console.log("🔍 Messages Layout - Session:", session ? `✅ ${session.user.email} (${session.user.role})` : "❌ null");

  if (!session) {
    console.log("❌ No session found, redirecting to /login");
    redirect("/login");
  }

  console.log("🔍 Messages Layout - Can access messages:", canAccessMessages(session.user.role));
  if (!canAccessMessages(session.user.role)) {
    console.log("❌ User cannot access messages, redirecting to:", getDefaultRedirect(session.user.role));
    redirect(getDefaultRedirect(session.user.role));
  }

  console.log("✅ Messages Layout - Access granted!");

  const unreadCount = 0; // Would be fetched from API in real implementation

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
                href="/messages"
                className="flex items-center gap-2 text-blue-600 font-medium"
              >
                <MessageSquare className="h-5 w-5" />
                <span>Messages</span>
                {unreadCount > 0 && (
                  <span className="ml-1 px-2 py-0.5 text-xs bg-red-500 text-white rounded-full">
                    {unreadCount}
                  </span>
                )}
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
