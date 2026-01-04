import { SkillBreakdown } from '@datn/shared-types';
import { cn } from '@/lib/utils';

interface SkillBreakdownCardProps {
  breakdown: SkillBreakdown;
}

/**
 * Displays skill score breakdown with progress bars for each sub-score.
 * Total score (0-25) is shown prominently with color coding based on level.
 * 
 * @see _bmad-output/planning-artifacts/docs/prd/5-hybrid-skill-scoring-epic.md
 */
export function SkillBreakdownCard({ breakdown }: SkillBreakdownCardProps) {
  const { 
    completeness_score, 
    categorization_score, 
    evidence_score, 
    market_relevance_score, 
    total_score 
  } = breakdown;

  // Color coding for total score (0-25)
  const getTotalScoreColor = (score: number) => {
    if (score >= 20) return 'text-green-600 bg-green-50';
    if (score >= 15) return 'text-blue-600 bg-blue-50';
    if (score >= 10) return 'text-yellow-600 bg-yellow-50';
    return 'text-orange-600 bg-orange-50';
  };

  const getTotalScoreLabel = (score: number) => {
    if (score >= 20) return 'Excellent';
    if (score >= 15) return 'Good';
    if (score >= 10) return 'Fair';
    return 'Needs Improvement';
  };

  const subScores = [
    {
      name: 'Completeness',
      score: completeness_score,
      max: 7,
      color: 'bg-blue-500',
      bgColor: 'bg-blue-100',
      description: 'Quantity and diversity of skills'
    },
    {
      name: 'Categorization',
      score: categorization_score,
      max: 6,
      color: 'bg-green-500',
      bgColor: 'bg-green-100',
      description: 'Coverage across skill categories'
    },
    {
      name: 'Evidence',
      score: evidence_score,
      max: 6,
      color: 'bg-purple-500',
      bgColor: 'bg-purple-100',
      description: 'Skill usage demonstrated in experience'
    },
    {
      name: 'Market Relevance',
      score: market_relevance_score,
      max: 6,
      color: 'bg-orange-500',
      bgColor: 'bg-orange-100',
      description: 'In-demand skills for current market'
    }
  ];

  return (
    <div className="space-y-4">
      {/* Total Score Header */}
      <div className={cn(
        'flex items-center justify-between p-4 rounded-lg',
        getTotalScoreColor(total_score)
      )}>
        <div>
          <h3 className="text-lg font-semibold">Skill Score</h3>
          <p className="text-sm opacity-80">{getTotalScoreLabel(total_score)}</p>
        </div>
        <div className="text-right">
          <span className="text-3xl font-bold">{total_score}</span>
          <span className="text-lg opacity-70">/25</span>
        </div>
      </div>

      {/* Sub-scores with progress bars */}
      <div className="space-y-3">
        {subScores.map((item) => {
          const percentage = (item.score / item.max) * 100;
          return (
            <div key={item.name} className="space-y-1">
              <div className="flex justify-between items-center text-sm">
                <span className="font-medium text-gray-700">{item.name}</span>
                <span className="text-gray-500">
                  {item.score}/{item.max}
                </span>
              </div>
              <div 
                className={cn('h-2 rounded-full', item.bgColor)}
                role="progressbar"
                aria-label={`${item.name} score: ${item.score} out of ${item.max}`}
                aria-valuenow={item.score}
                aria-valuemin={0}
                aria-valuemax={item.max}
              >
                <div
                  className={cn(
                    'h-full rounded-full transition-all duration-500 ease-out',
                    item.color
                  )}
                  style={{ width: `${percentage}%` }}
                />
              </div>
              <p className="text-xs text-gray-500">{item.description}</p>
            </div>
          );
        })}
      </div>
    </div>
  );
}
