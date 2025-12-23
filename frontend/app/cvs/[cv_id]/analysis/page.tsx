import { Suspense } from 'react';
import { cookies } from 'next/headers';
import { redirect } from 'next/navigation';
import Link from 'next/link';
import { CVAnalysisResults } from '@/features/cv/components/CVAnalysisResults';
import { DeleteCVButton } from '@/features/cv/components/DeleteCVButton';
import { DownloadCVButton } from '@/features/cv/components/DownloadCVButton';
import { getCVAnalysis, getSkillSuggestions } from '@/features/cv/actions'; // Updated import

interface PageProps {
  params: Promise<{ cv_id: string }>;
}

export default async function CVAnalysisPage({ params }: PageProps) {
  // Authentication Guard
  const cookieStore = await cookies();
  const accessToken = cookieStore.get('access_token')?.value;

  if (!accessToken) {
    redirect('/login');
  }

  const { cv_id } = await params;

  // Fetch initial analysis data with error handling
  let analysis;
  let error = null;

  try {
    analysis = await getCVAnalysis(cv_id);
  } catch (e) {
    error = e;
    console.error('Failed to fetch CV analysis:', e);
  }
  
  // Fetch skill suggestions
  let skillSuggestions;
  let suggestionsError = null;
  try {
    skillSuggestions = await getSkillSuggestions(cv_id);
  } catch (e) {
    suggestionsError = e;
    console.error('Failed to fetch skill suggestions:', e);
  }


  // If analysis doesn't exist, show helpful message
  if (!analysis || error) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <Link
            href="/cvs"
            className="text-blue-600 hover:text-blue-800 text-sm mb-2 inline-block"
          >
            &larr; Back to My CVs
          </Link>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            CV Analysis Results
          </h1>
        </div>

        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
          <h3 className="text-lg font-medium text-yellow-800 mb-2">
            Analysis Not Available
          </h3>
          <p className="text-yellow-700 mb-4">
            The analysis for this CV is not available yet. This could be because:
          </p>
          <ul className="list-disc list-inside text-yellow-700 mb-4">
            <li>The CV was uploaded before the analysis feature was enabled</li>
            <li>The analysis is still being processed</li>
            <li>The CV does not exist or you don&apos;t have access to it</li>
          </ul>
          <Link
            href="/cvs/upload"
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
          >
            Upload a New CV
          </Link>
        </div>
      </div>
    );
  }

  // Extract filename for delete dialog (use cv_filename from response or fallback)
  const filename = analysis.cv_filename || `CV-${cv_id.slice(0, 8)}`;

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <div className="flex items-center justify-between mb-2">
          <Link
            href="/cvs"
            className="text-blue-600 hover:text-blue-800 text-sm"
          >
            &larr; Back to My CVs
          </Link>
          <div className="flex items-center space-x-2">
            <DownloadCVButton cvId={cv_id} filename={filename} variant="button" />
            <DeleteCVButton cvId={cv_id} filename={filename} redirectTo="/cvs" />
          </div>
        </div>
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          CV Analysis Results
        </h1>
        <p className="text-gray-600">
          Detailed analysis of your uploaded CV
        </p>
      </div>

      <Suspense fallback={<AnalysisSkeleton />}>
        <CVAnalysisResults 
          cvId={cv_id} 
          initialAnalysis={analysis} 
          skillSuggestions={skillSuggestions?.suggestions || []} // Pass suggestions
        />
      </Suspense>
    </div>
  );
}

function AnalysisSkeleton() {
  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow p-6">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/3 mb-4"></div>
          <div className="h-4 bg-gray-200 rounded w-1/2 mb-2"></div>
          <div className="h-4 bg-gray-200 rounded w-3/4"></div>
        </div>
      </div>
      <div className="bg-white rounded-lg shadow p-6">
        <div className="animate-pulse">
          <div className="h-6 bg-gray-200 rounded w-1/4 mb-4"></div>
          <div className="space-y-2">
            <div className="h-4 bg-gray-200 rounded"></div>
            <div className="h-4 bg-gray-200 rounded"></div>
            <div className="h-4 bg-gray-200 rounded w-3/4"></div>
          </div>
        </div>
      </div>
    </div>
  );
}