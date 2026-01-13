/**
 * EvaluationDetailReport Component (Story 8.4)
 * 
 * Displays comprehensive evaluation report using the new /evaluation/detail endpoint.
 * Shows overall evaluation, dimension breakdown, detailed analysis, and recommendations.
 * 
 * Story 8.4: Interview History
 * 
 * @example
 * ```tsx
 * <EvaluationDetailReport
 *   evaluation={{
 *     interview_id: "123",
 *     job_title: "Senior Software Engineer",
 *     overall_evaluation: {...},
 *     dimension_scores: {...},
 *     detailed_analysis: {...},
 *     recommendations: {...},
 *     created_at: "..."
 *   }}
 * />
 * ```
 */
'use client';

import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription } from '@/components/ui/alert';
import {
  CheckCircle2,
  XCircle,
  AlertTriangle,
  TrendingUp,
  Target,
  Award,
  Lightbulb,
  Flag,
  Star,
  ArrowUp,
} from 'lucide-react';
import { InterviewEvaluationDetail } from '../types';
import { cn } from '@/lib/utils';

export interface EvaluationDetailReportProps {
  evaluation: InterviewEvaluationDetail;
}

/**
 * Get color class based on score
 */
function getScoreColor(score: number): string {
  if (score >= 8) return 'text-green-600';
  if (score >= 6) return 'text-blue-600';
  if (score >= 4) return 'text-yellow-600';
  return 'text-red-600';
}

/**
 * Get grade badge color
 */
function getGradeColor(grade: string): string {
  const gradeUpper = grade.toUpperCase();
  if (gradeUpper.startsWith('A')) return 'bg-green-500';
  if (gradeUpper.startsWith('B')) return 'bg-blue-500';
  if (gradeUpper.startsWith('C')) return 'bg-yellow-500';
  if (gradeUpper.startsWith('D')) return 'bg-orange-500';
  return 'bg-red-500';
}

/**
 * Get hiring recommendation icon and color
 */
function getRecommendationDisplay(recommendation: string) {
  const rec = recommendation.toLowerCase();
  
  if (rec.includes('strongly recommend') || rec.includes('strong hire')) {
    return {
      icon: CheckCircle2,
      color: 'text-green-600',
      bgColor: 'bg-green-50',
      borderColor: 'border-green-200',
    };
  }
  
  if (rec.includes('recommend') || rec.includes('hire')) {
    return {
      icon: CheckCircle2,
      color: 'text-blue-600',
      bgColor: 'bg-blue-50',
      borderColor: 'border-blue-200',
    };
  }
  
  if (rec.includes('consider') || rec.includes('maybe')) {
    return {
      icon: AlertTriangle,
      color: 'text-yellow-600',
      bgColor: 'bg-yellow-50',
      borderColor: 'border-yellow-200',
    };
  }
  
  return {
    icon: XCircle,
    color: 'text-red-600',
    bgColor: 'bg-red-50',
    borderColor: 'border-red-200',
  };
}

export function EvaluationDetailReport({ evaluation }: EvaluationDetailReportProps) {
  const { overall_evaluation, dimension_scores, detailed_analysis, recommendations } = evaluation;
  const recDisplay = getRecommendationDisplay(overall_evaluation.hiring_recommendation);
  const RecommendationIcon = recDisplay.icon;

  return (
    <div className="space-y-6">
      {/* Overall Evaluation Summary */}
      <Card className="border-2">
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="text-2xl">Đánh giá Tổng thể</CardTitle>
            <Badge className={cn('text-white text-lg px-4 py-2', getGradeColor(overall_evaluation.grade))}>
              {overall_evaluation.grade}
            </Badge>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Score Display */}
          <div className="flex items-center justify-center p-6 bg-gray-50 rounded-lg">
            <div className="text-center">
              <div className={cn('text-6xl font-bold', getScoreColor(overall_evaluation.score))}>
                {overall_evaluation.score.toFixed(1)}
              </div>
              <div className="text-gray-500 text-lg mt-1">/10</div>
            </div>
          </div>

          {/* Hiring Recommendation */}
          <Alert className={cn(recDisplay.bgColor, recDisplay.borderColor)}>
            <RecommendationIcon className={cn('h-5 w-5', recDisplay.color)} />
            <AlertDescription className="ml-2">
              <span className="font-semibold">Khuyến nghị tuyển dụng:</span>{' '}
              {overall_evaluation.hiring_recommendation}
            </AlertDescription>
          </Alert>
        </CardContent>
      </Card>

      {/* Dimension Scores Breakdown */}
      <Card>
        <CardHeader>
          <CardTitle className="text-xl">Phân tích theo Chiều đo</CardTitle>
          <CardDescription>
            Điểm số chi tiết cho 3 chiều đo chính: Kỹ thuật (50%), Giao tiếp (25%), Hành vi (25%)
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Technical Dimension */}
          <DimensionCard
            title="Kỹ thuật (Technical)"
            icon={Target}
            dimension={dimension_scores.technical}
            color="blue"
          />

          {/* Communication Dimension */}
          <DimensionCard
            title="Giao tiếp (Communication)"
            icon={TrendingUp}
            dimension={dimension_scores.communication}
            color="green"
          />

          {/* Behavioral Dimension */}
          <DimensionCard
            title="Hành vi (Behavioral)"
            icon={Award}
            dimension={dimension_scores.behavioral}
            color="purple"
          />
        </CardContent>
      </Card>

      {/* Detailed Analysis */}
      <Card>
        <CardHeader>
          <CardTitle className="text-xl">Phân tích Chi tiết</CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Key Strengths */}
          {detailed_analysis.key_strengths.length > 0 && (
            <div>
              <div className="flex items-center gap-2 mb-3">
                <Star className="h-5 w-5 text-green-600" />
                <h3 className="font-semibold text-green-600">Điểm mạnh chính</h3>
              </div>
              <ul className="space-y-2">
                {detailed_analysis.key_strengths.map((strength, idx) => (
                  <li key={idx} className="flex items-start gap-2">
                    <CheckCircle2 className="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
                    <span className="text-gray-700">{strength}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Areas for Improvement */}
          {detailed_analysis.areas_for_improvement.length > 0 && (
            <div>
              <div className="flex items-center gap-2 mb-3">
                <ArrowUp className="h-5 w-5 text-blue-600" />
                <h3 className="font-semibold text-blue-600">Điểm cần cải thiện</h3>
              </div>
              <ul className="space-y-2">
                {detailed_analysis.areas_for_improvement.map((area, idx) => (
                  <li key={idx} className="flex items-start gap-2">
                    <Lightbulb className="h-4 w-4 text-blue-500 mt-0.5 flex-shrink-0" />
                    <span className="text-gray-700">{area}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Notable Moments */}
          {detailed_analysis.notable_moments.length > 0 && (
            <div>
              <div className="flex items-center gap-2 mb-3">
                <AlertTriangle className="h-5 w-5 text-yellow-600" />
                <h3 className="font-semibold text-yellow-600">Điểm đáng chú ý</h3>
              </div>
              <ul className="space-y-2">
                {detailed_analysis.notable_moments.map((moment, idx) => (
                  <li key={idx} className="flex items-start gap-2">
                    <span className="text-yellow-600 font-bold mt-0.5 flex-shrink-0">•</span>
                    <span className="text-gray-700">{moment}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Red Flags */}
          {detailed_analysis.red_flags && detailed_analysis.red_flags.length > 0 && (
            <div>
              <div className="flex items-center gap-2 mb-3">
                <Flag className="h-5 w-5 text-red-600" />
                <h3 className="font-semibold text-red-600">Cảnh báo</h3>
              </div>
              <ul className="space-y-2">
                {detailed_analysis.red_flags.map((flag, idx) => (
                  <li key={idx} className="flex items-start gap-2">
                    <XCircle className="h-4 w-4 text-red-500 mt-0.5 flex-shrink-0" />
                    <span className="text-gray-700">{flag}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Recommendations */}
      <Card>
        <CardHeader>
          <CardTitle className="text-xl">Khuyến nghị & Phát triển</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Hiring Decision */}
          <div>
            <h3 className="font-semibold mb-2">Quyết định tuyển dụng</h3>
            <p className="text-gray-700">{recommendations.hiring_decision}</p>
          </div>

          {/* Reasoning */}
          <div>
            <h3 className="font-semibold mb-2">Lý do</h3>
            <p className="text-gray-700">{recommendations.reasoning}</p>
          </div>

          {/* Role Fit */}
          <div>
            <h3 className="font-semibold mb-2">Phù hợp với vị trí</h3>
            <p className="text-gray-700">{recommendations.role_fit}</p>
          </div>

          {/* Development Areas */}
          {recommendations.development_areas.length > 0 && (
            <div>
              <h3 className="font-semibold mb-2">Lĩnh vực cần phát triển</h3>
              <ul className="list-disc list-inside space-y-1">
                {recommendations.development_areas.map((area, idx) => (
                  <li key={idx} className="text-gray-700">{area}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Onboarding Suggestions */}
          {recommendations.onboarding_suggestions && recommendations.onboarding_suggestions.length > 0 && (
            <div>
              <h3 className="font-semibold mb-2">Gợi ý Onboarding</h3>
              <ul className="list-disc list-inside space-y-1">
                {recommendations.onboarding_suggestions.map((suggestion, idx) => (
                  <li key={idx} className="text-gray-700">{suggestion}</li>
                ))}
              </ul>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

/**
 * Dimension Card Component
 */
function DimensionCard({
  title,
  icon: Icon,
  dimension,
  color,
}: {
  title: string;
  icon: React.ElementType;
  dimension: { score: number; weight: number; sub_scores: Record<string, number>; evidence: string[] };
  color: 'blue' | 'green' | 'purple';
}) {
  const colorClasses = {
    blue: { text: 'text-blue-600', bg: 'bg-blue-500', light: 'bg-blue-50' },
    green: { text: 'text-green-600', bg: 'bg-green-500', light: 'bg-green-50' },
    purple: { text: 'text-purple-600', bg: 'bg-purple-500', light: 'bg-purple-50' },
  };

  const colors = colorClasses[color];

  return (
    <div className={cn('border-2 rounded-lg p-4', colors.light)}>
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <Icon className={cn('h-5 w-5', colors.text)} />
          <h3 className="font-semibold">{title}</h3>
          <Badge variant="outline">{(dimension.weight * 100).toFixed(0)}%</Badge>
        </div>
        <div className={cn('text-2xl font-bold', getScoreColor(dimension.score))}>
          {dimension.score.toFixed(1)}/10
        </div>
      </div>

      {/* Progress Bar */}
      <Progress value={dimension.score * 10} className="h-3 mb-4" />

      {/* Sub-scores */}
      {Object.keys(dimension.sub_scores).length > 0 && (
        <div className="space-y-2 mb-3">
          <h4 className="text-sm font-medium text-gray-700">Điểm chi tiết:</h4>
          <div className="grid grid-cols-2 gap-2">
            {Object.entries(dimension.sub_scores).map(([key, value]) => (
              <div key={key} className="flex justify-between text-sm">
                <span className="text-gray-600 capitalize">{key.replace(/_/g, ' ')}:</span>
                <span className={cn('font-semibold', getScoreColor(value))}>{value.toFixed(1)}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Evidence */}
      {dimension.evidence.length > 0 && (
        <div>
          <h4 className="text-sm font-medium text-gray-700 mb-2">Bằng chứng:</h4>
          <ul className="space-y-1">
            {dimension.evidence.map((item, idx) => (
              <li key={idx} className="text-sm text-gray-600 flex items-start gap-1">
                <span className="mt-1">•</span>
                <span>{item}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
