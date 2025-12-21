/**
 * Skeleton loading component for CV History/List.
 * Displays 6 placeholder cards while CVs are being fetched.
 * Also exported as CVListSkeleton for semantic naming.
 */
export function CVHistorySkeleton() {
  return (
    <div className="grid gap-6 grid-cols-1 md:grid-cols-2 lg:grid-cols-3" data-testid="cv-skeleton">
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
            {/* Quality Score placeholder */}
            <div className="mb-4">
              <div className="flex items-center justify-between">
                <div className="h-4 bg-gray-200 rounded w-20"></div>
                <div className="h-5 bg-gray-200 rounded w-12"></div>
              </div>
            </div>
            {/* Visibility toggle placeholder */}
            <div className="mb-4 py-3 border-t border-b border-gray-100">
              <div className="h-5 bg-gray-200 rounded w-32"></div>
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

// Alias for semantic naming per story requirements
export { CVHistorySkeleton as CVListSkeleton };
