"use client";

import Link from "next/link";
import { ShieldX, ArrowLeft, Home } from "lucide-react";

interface UnauthorizedContentProps {
  homeLink: string;
  homeLinkText: string;
  roleDisplayName: string | null;
}

export function UnauthorizedContent({ 
  homeLink, 
  homeLinkText, 
  roleDisplayName 
}: UnauthorizedContentProps) {
  return (
    <main className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg shadow-lg p-8 max-w-md w-full text-center">
        {/* Icon */}
        <div className="flex justify-center mb-6">
          <div className="bg-red-100 rounded-full p-4">
            <ShieldX className="h-12 w-12 text-red-500" />
          </div>
        </div>

        {/* Title */}
        <h1 className="text-2xl font-bold text-gray-900 mb-2">
          Access Denied
        </h1>

        {/* Description */}
        <p className="text-gray-600 mb-6">
          You don&apos;t have permission to access this page. 
          {roleDisplayName && (
            <span className="block mt-2">
              Your current role is <strong>{roleDisplayName}</strong>.
            </span>
          )}
        </p>

        {/* Action Buttons */}
        <div className="flex flex-col gap-3">
          <Link
            href={homeLink}
            className="inline-flex items-center justify-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
          >
            <Home className="h-4 w-4" />
            {homeLinkText}
          </Link>
          
          <button
            type="button"
            onClick={() => window.history.back()}
            className="inline-flex items-center justify-center gap-2 px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 transition-colors"
          >
            <ArrowLeft className="h-4 w-4" />
            Go Back
          </button>
        </div>

        {/* Help Text */}
        <p className="text-sm text-gray-500 mt-6">
          If you believe this is an error, please contact support.
        </p>
      </div>
    </main>
  );
}
