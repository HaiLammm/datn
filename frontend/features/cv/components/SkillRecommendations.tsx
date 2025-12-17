import { cn } from '@/lib/utils';

interface SkillRecommendationsProps {
  recommendations: string[];
}

/**
 * Lightbulb icon SVG component for recommendations.
 */
function LightbulbIcon({ className }: { className?: string }) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={cn('w-5 h-5', className)}
      aria-hidden="true"
    >
      <path d="M15 14c.2-1 .7-1.7 1.5-2.5 1-.9 1.5-2.2 1.5-3.5A6 6 0 0 0 6 8c0 1 .2 2.2 1.5 3.5.7.7 1.3 1.5 1.5 2.5" />
      <path d="M9 18h6" />
      <path d="M10 22h4" />
    </svg>
  );
}

/**
 * Displays AI-generated skill development recommendations.
 * Each recommendation is shown as a card with a lightbulb icon.
 * Shows empty state message when no recommendations are available.
 * 
 * @see docs/prd/5-hybrid-skill-scoring-epic.md
 */
export function SkillRecommendations({ recommendations }: SkillRecommendationsProps) {
  if (!recommendations || recommendations.length === 0) {
    return (
      <div className="flex items-center gap-2 text-gray-500 italic">
        <LightbulbIcon className="text-gray-400" />
        <span>No recommendations at this time</span>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2 text-gray-700">
        <LightbulbIcon className="text-amber-500" />
        <h4 className="font-medium">Skill Development Suggestions</h4>
      </div>
      
      <ul className="space-y-2" role="list" aria-label="Skill recommendations">
        {recommendations.map((recommendation, index) => (
          <li
            key={index}
            className={cn(
              'flex items-start gap-3 p-3 rounded-lg',
              'bg-amber-50 border border-amber-100'
            )}
          >
            <span 
              className="flex-shrink-0 w-6 h-6 flex items-center justify-center rounded-full bg-amber-100 text-amber-700 text-xs font-medium"
              aria-hidden="true"
            >
              {index + 1}
            </span>
            <p className="text-sm text-gray-700 leading-relaxed">
              {recommendation}
            </p>
          </li>
        ))}
      </ul>
    </div>
  );
}
