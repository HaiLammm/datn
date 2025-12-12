import { Suspense } from 'react';
import Link from 'next/link';
import { cookies } from 'next/headers';
import { redirect } from 'next/navigation';
import { getCVList } from '@/features/cv/actions';
import { CVWithStatus } from '@datn/shared-types';

export default async function CVsPage() {
  // Authentication Guard
  const cookieStore = await cookies();
  const accessToken = cookieStore.get('access_token')?.value;

  if (!accessToken) {
    redirect('/login');
  }

  const cvs = await getCVList();

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          My CVs
        </h1>
        <p className="text-gray-600">
          View and manage your uploaded CVs and their analysis results.
        </p>
      </div>

      <div className="mb-6">
        <Link
          href="/cvs/upload"
          className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
        >
          Upload New CV
        </Link>
      </div>

      <Suspense fallback={<CVsSkeleton />}>
        <CVsList cvs={cvs} />
      </Suspense>
    </div>
  );
}

function CVsList({ cvs }: { cvs: CVWithStatus[] }) {
  if (cvs.length === 0) {
    return (
      <div className="text-center py-12">
        <div className="text-gray-400 mb-4">
          <svg className="mx-auto h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        </div>
        <h3 className="text-lg font-medium text-gray-900 mb-2">
          No CVs uploaded yet
        </h3>
        <p className="text-gray-600 mb-6">
          Get started by uploading your first CV for analysis.
        </p>
        <Link
          href="/cvs/upload"
          className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
        >
          Upload Your First CV
        </Link>
      </div>
    );
  }

  return (
    <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
      {cvs.map((cv) => (
        <CVCard key={cv.id} cv={cv} />
      ))}
    </div>
  );
}

function CVCard({ cv }: { cv: CVWithStatus }) {
  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'COMPLETED':
        return (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
            Completed
          </span>
        );
      case 'PROCESSING':
        return (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
            Processing
          </span>
        );
      case 'FAILED':
        return (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
            Failed
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
            Pending
          </span>
        );
    }
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-start justify-between mb-4">
        <div>
          <h3 className="text-lg font-medium text-gray-900 truncate">
            {cv.filename}
          </h3>
          <p className="text-sm text-gray-600">
            Uploaded {new Date(cv.uploaded_at).toLocaleDateString()}
          </p>
        </div>
        {getStatusBadge(cv.analysis_status)}
      </div>

      <div className="flex space-x-3">
        <Link
          href={`/cvs/${cv.id}/analysis`}
          className="flex-1 inline-flex justify-center items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
        >
          View Analysis
        </Link>
        <button
          className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-400 bg-gray-100 cursor-not-allowed"
          disabled
          title="Delete feature coming soon"
        >
          Delete
        </button>
      </div>
    </div>
  );
}

function CVsSkeleton() {
  return (
    <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
      {[...Array(6)].map((_, i) => (
        <div key={i} className="bg-white rounded-lg shadow p-6">
          <div className="animate-pulse">
            <div className="flex items-start justify-between mb-4">
              <div className="flex-1">
                <div className="h-5 bg-gray-200 rounded w-3/4 mb-2"></div>
                <div className="h-4 bg-gray-200 rounded w-1/2"></div>
              </div>
              <div className="h-6 bg-gray-200 rounded-full w-16"></div>
            </div>
            <div className="flex space-x-3">
              <div className="flex-1 h-9 bg-gray-200 rounded"></div>
              <div className="h-9 bg-gray-200 rounded w-16"></div>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}