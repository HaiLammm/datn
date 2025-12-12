interface AnalysisSummaryProps {
  summary: string;
}

export function AnalysisSummary({ summary }: AnalysisSummaryProps) {
  return (
    <div className="prose prose-gray max-w-none">
      <p className="text-gray-700 leading-relaxed">{summary}</p>
    </div>
  );
}