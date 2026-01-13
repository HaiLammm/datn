/**
 * InterviewScoreGauge Component
 * 
 * Displays interview score in a visual gauge format with grade badge.
 * Shows overall score out of 10 with color coding based on performance.
 * 
 * Story 8.4: Interview History
 * 
 * @example
 * ```tsx
 * <InterviewScoreGauge
 *   score={8.5}
 *   grade="A-"
 *   maxScore={10}
 * />
 * ```
 */
'use client';

import { Badge } from '@/components/ui/badge';
import { Card, CardContent } from '@/components/ui/card';
import { cn } from '@/lib/utils';

export interface InterviewScoreGaugeProps {
  score: number;
  grade?: string | null;
  maxScore?: number;
  size?: 'sm' | 'md' | 'lg';
  showLabel?: boolean;
}

/**
 * Get color based on score percentage
 */
function getScoreColor(score: number, maxScore: number): string {
  const percentage = (score / maxScore) * 100;
  
  if (percentage >= 80) return 'text-green-600';
  if (percentage >= 60) return 'text-blue-600';
  if (percentage >= 40) return 'text-yellow-600';
  if (percentage >= 20) return 'text-orange-600';
  return 'text-red-600';
}

/**
 * Get background color for progress bar
 */
function getProgressColor(score: number, maxScore: number): string {
  const percentage = (score / maxScore) * 100;
  
  if (percentage >= 80) return 'bg-green-500';
  if (percentage >= 60) return 'bg-blue-500';
  if (percentage >= 40) return 'bg-yellow-500';
  if (percentage >= 20) return 'bg-orange-500';
  return 'bg-red-500';
}

/**
 * Get badge color based on grade
 */
function getGradeColor(grade: string | null | undefined): string {
  if (!grade) return 'bg-gray-500';
  
  const gradeUpper = grade.toUpperCase();
  if (gradeUpper.startsWith('A')) return 'bg-green-500';
  if (gradeUpper.startsWith('B')) return 'bg-blue-500';
  if (gradeUpper.startsWith('C')) return 'bg-yellow-500';
  if (gradeUpper.startsWith('D')) return 'bg-orange-500';
  return 'bg-red-500';
}

/**
 * Get size classes based on size prop
 */
function getSizeClasses(size: 'sm' | 'md' | 'lg') {
  switch (size) {
    case 'sm':
      return {
        container: 'w-24 h-24',
        score: 'text-2xl',
        maxScore: 'text-sm',
        badge: 'text-sm px-2 py-1',
      };
    case 'lg':
      return {
        container: 'w-48 h-48',
        score: 'text-5xl',
        maxScore: 'text-xl',
        badge: 'text-lg px-4 py-2',
      };
    default: // md
      return {
        container: 'w-32 h-32',
        score: 'text-4xl',
        maxScore: 'text-base',
        badge: 'text-base px-3 py-1',
      };
  }
}

export function InterviewScoreGauge({
  score,
  grade,
  maxScore = 10,
  size = 'md',
  showLabel = true,
}: InterviewScoreGaugeProps) {
  const percentage = (score / maxScore) * 100;
  const sizeClasses = getSizeClasses(size);
  const scoreColor = getScoreColor(score, maxScore);
  const progressColor = getProgressColor(score, maxScore);
  const gradeColor = getGradeColor(grade);

  return (
    <Card className="border-2">
      <CardContent className="p-6">
        <div className="flex flex-col items-center gap-4">
          {/* Circular Gauge */}
          <div className="relative flex items-center justify-center">
            {/* Background Circle */}
            <svg className={cn('transform -rotate-90', sizeClasses.container)} viewBox="0 0 120 120">
              {/* Background track */}
              <circle
                cx="60"
                cy="60"
                r="54"
                stroke="currentColor"
                strokeWidth="8"
                fill="none"
                className="text-gray-200"
              />
              {/* Progress arc */}
              <circle
                cx="60"
                cy="60"
                r="54"
                stroke="currentColor"
                strokeWidth="8"
                fill="none"
                strokeLinecap="round"
                strokeDasharray={`${(percentage / 100) * 339.292} 339.292`}
                className={cn('transition-all duration-1000 ease-out', progressColor)}
              />
            </svg>

            {/* Score Text (Centered) */}
            <div className="absolute inset-0 flex flex-col items-center justify-center">
              <div className={cn('font-bold', scoreColor, sizeClasses.score)}>
                {score.toFixed(1)}
              </div>
              <div className={cn('text-gray-500', sizeClasses.maxScore)}>
                /{maxScore}
              </div>
            </div>
          </div>

          {/* Grade Badge */}
          {grade && (
            <Badge className={cn('text-white font-bold', gradeColor, sizeClasses.badge)}>
              Grade: {grade}
            </Badge>
          )}

          {/* Label */}
          {showLabel && (
            <div className="text-center">
              <p className="text-sm font-medium text-gray-700">Overall Performance</p>
              <p className="text-xs text-gray-500">Based on 3 evaluation dimensions</p>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
