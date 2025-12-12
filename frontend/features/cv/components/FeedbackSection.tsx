interface FeedbackSectionProps {
  feedback: {
    formatting_feedback?: string[];
    ats_hints?: string[];
    strengths?: string[];
    improvements?: string[];
    criteria?: Record<string, number>;
    experience_breakdown?: {
      total_years?: number;
      key_roles?: string[];
      industries?: string[];
    };
  };
}

export function FeedbackSection({ feedback }: FeedbackSectionProps) {
  const hasContent =
    (feedback.formatting_feedback && feedback.formatting_feedback.length > 0) ||
    (feedback.ats_hints && feedback.ats_hints.length > 0) ||
    (feedback.strengths && feedback.strengths.length > 0) ||
    (feedback.improvements && feedback.improvements.length > 0);

  if (!hasContent) {
    return (
      <p className="text-gray-500 italic">No specific feedback available</p>
    );
  }

  return (
    <div className="space-y-6">
      {/* Strengths */}
      {feedback.strengths && feedback.strengths.length > 0 && (
        <div>
          <h4 className="font-medium text-gray-900 mb-2 flex items-center">
            <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
            Key Strengths
          </h4>
          <ul className="space-y-1">
            {feedback.strengths.map((strength, index) => (
              <li key={index} className="text-gray-700 flex items-start">
                <span className="text-green-500 mr-2">✓</span>
                {strength}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Areas for Improvement */}
      {feedback.improvements && feedback.improvements.length > 0 && (
        <div>
          <h4 className="font-medium text-gray-900 mb-2 flex items-center">
            <span className="w-2 h-2 bg-yellow-500 rounded-full mr-2"></span>
            Areas for Improvement
          </h4>
          <ul className="space-y-1">
            {feedback.improvements.map((improvement, index) => (
              <li key={index} className="text-gray-700 flex items-start">
                <span className="text-yellow-500 mr-2">→</span>
                {improvement}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Formatting Feedback */}
      {feedback.formatting_feedback && feedback.formatting_feedback.length > 0 && (
        <div>
          <h4 className="font-medium text-gray-900 mb-2 flex items-center">
            <span className="w-2 h-2 bg-blue-500 rounded-full mr-2"></span>
            Formatting Suggestions
          </h4>
          <ul className="space-y-1">
            {feedback.formatting_feedback.map((item, index) => (
              <li key={index} className="text-gray-700 flex items-start">
                <span className="text-blue-500 mr-2">•</span>
                {item}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* ATS Hints */}
      {feedback.ats_hints && feedback.ats_hints.length > 0 && (
        <div>
          <h4 className="font-medium text-gray-900 mb-2 flex items-center">
            <span className="w-2 h-2 bg-purple-500 rounded-full mr-2"></span>
            ATS Compatibility Tips
          </h4>
          <ul className="space-y-1">
            {feedback.ats_hints.map((hint, index) => (
              <li key={index} className="text-gray-700 flex items-start">
                <span className="text-purple-500 mr-2">★</span>
                {hint}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}