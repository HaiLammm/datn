/**
 * InterviewSessionCard Component
 * 
 * Displays a summary card for an interview session in the history list.
 * Shows key information like job title, date, duration, score, and status.
 * 
 * Story 8.4: Interview History
 * 
 * @example
 * ```tsx
 * <InterviewSessionCard
 *   session={{
 *     id: "123",
 *     job_title: "Senior Software Engineer",
 *     created_at: "2024-01-12T10:30:00Z",
 *     status: "completed",
 *     overall_score: 8.5,
 *     overall_grade: "A-",
 *     duration_minutes: 45,
 *     question_count: 10,
 *     turn_count: 25
 *   }}
 * />
 * ```
 */
'use client';

import Link from 'next/link';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Clock, Calendar, MessageSquare, FileText } from 'lucide-react';
import { InterviewSessionSummary } from '../types';
import { cn } from '@/lib/utils';

export interface InterviewSessionCardProps {
  session: InterviewSessionSummary;
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
 * Get status badge variant
 */
function getStatusVariant(status: string): "default" | "secondary" | "destructive" | "outline" {
  switch (status.toLowerCase()) {
    case 'completed':
      return 'default';
    case 'in_progress':
      return 'secondary';
    case 'error':
      return 'destructive';
    default:
      return 'outline';
  }
}

/**
 * Format date to readable string
 */
function formatDate(dateString: string): string {
  const date = new Date(dateString);
  return new Intl.DateTimeFormat('vi-VN', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(date);
}

/**
 * Format duration to readable string
 */
function formatDuration(minutes: number | null | undefined): string {
  if (!minutes) return 'N/A';
  if (minutes < 60) return `${minutes} phút`;
  const hours = Math.floor(minutes / 60);
  const remainingMinutes = minutes % 60;
  return `${hours}h ${remainingMinutes}m`;
}

export function InterviewSessionCard({ session }: InterviewSessionCardProps) {
  const {
    id,
    job_title,
    created_at,
    completed_at,
    status,
    overall_score,
    overall_grade,
    duration_minutes,
    question_count,
    turn_count,
  } = session;

  return (
    <Link href={`/interviews/${id}/detail`} className="block">
      <Card
        className={cn(
          'transition-all duration-200 hover:shadow-lg hover:scale-[1.02] cursor-pointer',
          'border-l-4',
          status === 'completed' ? 'border-l-green-500' : 'border-l-blue-500'
        )}
      >
        <CardHeader className="pb-3">
          <div className="flex items-start justify-between gap-2">
            <h3 className="text-lg font-semibold line-clamp-2 flex-1">
              {job_title}
            </h3>
            {overall_grade && (
              <Badge className={cn('text-white font-bold', getGradeColor(overall_grade))}>
                {overall_grade}
              </Badge>
            )}
          </div>
          <div className="flex items-center gap-2 mt-2">
            <Badge variant={getStatusVariant(status)}>
              {status === 'completed' ? 'Hoàn thành' : 
               status === 'in_progress' ? 'Đang thực hiện' : 
               status === 'error' ? 'Lỗi' : status}
            </Badge>
          </div>
        </CardHeader>

        <CardContent className="space-y-3">
          {/* Date and Duration */}
          <div className="flex items-center gap-4 text-sm text-muted-foreground">
            <div className="flex items-center gap-1">
              <Calendar className="h-4 w-4" />
              <span>{formatDate(created_at)}</span>
            </div>
            {duration_minutes !== null && duration_minutes !== undefined && (
              <div className="flex items-center gap-1">
                <Clock className="h-4 w-4" />
                <span>{formatDuration(duration_minutes)}</span>
              </div>
            )}
          </div>

          {/* Score Display */}
          {overall_score !== null && overall_score !== undefined && (
            <div className="flex items-center justify-between p-3 bg-muted/50 rounded-lg">
              <span className="text-sm font-medium">Điểm tổng thể:</span>
              <span className="text-2xl font-bold">{overall_score.toFixed(1)}/10</span>
            </div>
          )}

          {/* Stats */}
          <div className="flex items-center justify-between pt-2 border-t">
            <div className="flex items-center gap-1 text-sm text-muted-foreground">
              <FileText className="h-4 w-4" />
              <span>{question_count} câu hỏi</span>
            </div>
            <div className="flex items-center gap-1 text-sm text-muted-foreground">
              <MessageSquare className="h-4 w-4" />
              <span>{turn_count} lượt trao đổi</span>
            </div>
          </div>

          {/* Completed Date (if applicable) */}
          {completed_at && (
            <div className="text-xs text-muted-foreground text-right">
              Hoàn thành: {formatDate(completed_at)}
            </div>
          )}
        </CardContent>
      </Card>
    </Link>
  );
}
