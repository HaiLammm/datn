// app/dashboard/page.tsx

import Link from "next/link";
import { LogoutButton } from "@/components/auth/LogoutButton";

export default function DashboardPage() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-6 bg-white">
      <div className="text-center">
        <h1 className="text-4xl font-bold text-gray-800 mb-4">
          Login Successful!
        </h1>
        <p className="text-lg text-gray-600 mb-8">
          Welcome to your dashboard.
        </p>
        <div className="flex gap-4 justify-center">
          <Link 
            href="/" 
            className="px-6 py-2 font-semibold text-white bg-blue-500 rounded-md hover:bg-blue-600"
          >
            Go to Home
          </Link>
          <LogoutButton />
        </div>
      </div>
    </main>
  );
}
