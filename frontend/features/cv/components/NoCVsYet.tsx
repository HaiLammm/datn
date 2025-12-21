import Link from "next/link";

interface NoCVsYetProps {
  /** Title text to display */
  title?: string;
  /** Description text below title */
  description?: string;
  /** Whether to show the upload link */
  showUploadLink?: boolean;
  /** Custom action element instead of upload link */
  customAction?: React.ReactNode;
}

/**
 * Empty state component shown when user has no CVs uploaded.
 * Used in the CV list page and dashboard.
 *
 * @example
 * // Default usage
 * <NoCVsYet />
 *
 * @example
 * // Custom message
 * <NoCVsYet
 *   title="No matching CVs"
 *   description="Try adjusting your filters."
 *   showUploadLink={false}
 * />
 */
export function NoCVsYet({
  title = "No CVs uploaded yet",
  description = "Get started by uploading your first CV for analysis.",
  showUploadLink = true,
  customAction,
}: NoCVsYetProps) {
  return (
    <div className="text-center py-12" data-testid="no-cvs-empty-state">
      <div className="text-gray-400 mb-4">
        <svg
          className="mx-auto h-12 w-12"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          aria-hidden="true"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
          />
        </svg>
      </div>
      <h3 className="text-lg font-medium text-gray-900 mb-2">{title}</h3>
      <p className="text-gray-600 mb-6">{description}</p>
      {customAction ? (
        customAction
      ) : showUploadLink ? (
        <Link
          href="/cvs/upload"
          className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          data-testid="upload-first-cv-link"
        >
          Upload Your First CV
        </Link>
      ) : null}
    </div>
  );
}
