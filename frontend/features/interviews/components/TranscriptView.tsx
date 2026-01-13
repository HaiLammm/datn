/**
 * TranscriptView Component (Story 8.4)
 * 
 * Displays the full conversation transcript for a completed interview session.
 * Shows turn-by-turn Q&A with scores, timestamps, and expandable details.
 * 
 * Story 8.4: Interview History
 * 
 * @example
 * ```tsx
 * <TranscriptView
 *   interviewId="123"
 *   transcript={{
 *     interview_id: "123",
 *     job_title: "Senior Software Engineer",
 *     total_turns: 25,
 *     turns: [...]
 *   }}
 * />
 * ```
 */
'use client';

import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from '@/components/ui/collapsible';
import {
  User,
  Bot,
  ChevronDown,
  ChevronUp,
  Clock,
  BarChart3,
  MessageSquare,
} from 'lucide-react';
import { InterviewTranscriptResponse, TranscriptTurn } from '../types';
import { cn } from '@/lib/utils';

export interface TranscriptViewProps {
  interviewId: string;
  transcript: InterviewTranscriptResponse;
}

/**
 * Format timestamp to readable time
 */
function formatTime(dateString: string): string {
  const date = new Date(dateString);
  return new Intl.DateTimeFormat('vi-VN', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  }).format(date);
}

/**
 * Get score color based on value
 */
function getScoreColor(score: number | undefined): string {
  if (!score) return 'text-gray-500';
  if (score >= 8) return 'text-green-600';
  if (score >= 6) return 'text-blue-600';
  if (score >= 4) return 'text-yellow-600';
  return 'text-red-600';
}

/**
 * Get action type badge variant
 */
function getActionTypeBadge(actionType: string | null | undefined) {
  if (!actionType) return null;
  
  const variants: Record<string, { label: string; variant: 'default' | 'secondary' | 'outline' }> = {
    ask: { label: 'Câu hỏi', variant: 'default' },
    follow_up: { label: 'Theo dõi', variant: 'secondary' },
    clarify: { label: 'Làm rõ', variant: 'outline' },
    probe: { label: 'Thăm dò', variant: 'outline' },
    complete: { label: 'Hoàn thành', variant: 'default' },
  };
  
  const config = variants[actionType] || { label: actionType, variant: 'outline' as const };
  return (
    <Badge variant={config.variant} className="text-xs">
      {config.label}
    </Badge>
  );
}

/**
 * Turn Component - Single conversation turn
 */
function TurnItem({ turn, isFirst }: { turn: TranscriptTurn; isFirst: boolean }) {
  const [isScoresOpen, setIsScoresOpen] = useState(false);
  const hasScores = turn.scores && Object.values(turn.scores).some(s => s !== undefined && s !== null);

  return (
    <div className={cn('border-l-4 border-blue-200 pl-6 relative', isFirst && 'pt-0')}>
      {/* Turn Number Badge */}
      <div className="absolute -left-3 top-4 bg-blue-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-xs font-bold">
        {turn.turn_number}
      </div>

      <div className="space-y-4 pb-6">
        {/* Question Section */}
        {turn.question_text && (
          <Card className="bg-gray-50 border-gray-200">
            <CardHeader className="pb-3">
              <div className="flex items-start justify-between gap-2">
                <div className="flex items-center gap-2">
                  <Bot className="h-5 w-5 text-blue-600" />
                  <CardTitle className="text-sm font-medium text-gray-700">
                    Câu hỏi từ AI
                  </CardTitle>
                </div>
                <div className="flex items-center gap-2">
                  {getActionTypeBadge(turn.action_type)}
                  {turn.question_type && (
                    <Badge variant="outline" className="text-xs">
                      {turn.question_type}
                    </Badge>
                  )}
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <p className="text-gray-900">{turn.question_text}</p>
            </CardContent>
          </Card>
        )}

        {/* Candidate Answer Section */}
        <Card className="bg-white border-l-4 border-l-green-500">
          <CardHeader className="pb-3">
            <div className="flex items-center gap-2">
              <User className="h-5 w-5 text-green-600" />
              <CardTitle className="text-sm font-medium text-gray-700">
                Câu trả lời của bạn
              </CardTitle>
            </div>
          </CardHeader>
          <CardContent>
            <p className="text-gray-900 whitespace-pre-wrap">{turn.candidate_message}</p>
          </CardContent>
        </Card>

        {/* AI Response Section */}
        <Card className="bg-blue-50 border-blue-200">
          <CardHeader className="pb-3">
            <div className="flex items-center gap-2">
              <MessageSquare className="h-5 w-5 text-blue-600" />
              <CardTitle className="text-sm font-medium text-gray-700">
                Phản hồi từ AI
              </CardTitle>
            </div>
          </CardHeader>
          <CardContent>
            <p className="text-gray-900">{turn.ai_response}</p>
          </CardContent>
        </Card>

        {/* Scores Section (Collapsible) */}
        {hasScores && (
          <Collapsible open={isScoresOpen} onOpenChange={setIsScoresOpen}>
            <CollapsibleTrigger asChild>
              <Button variant="outline" size="sm" className="w-full">
                <BarChart3 className="h-4 w-4 mr-2" />
                {isScoresOpen ? 'Ẩn điểm số' : 'Xem điểm số'}
                {isScoresOpen ? (
                  <ChevronUp className="h-4 w-4 ml-2" />
                ) : (
                  <ChevronDown className="h-4 w-4 ml-2" />
                )}
              </Button>
            </CollapsibleTrigger>
            <CollapsibleContent className="mt-2">
              <Card className="bg-gray-50">
                <CardContent className="pt-4">
                  <div className="grid grid-cols-2 gap-4">
                    {turn.scores?.technical_score !== undefined && turn.scores.technical_score !== null && (
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-gray-600">Kỹ thuật:</span>
                        <span className={cn('font-bold', getScoreColor(turn.scores.technical_score))}>
                          {turn.scores.technical_score.toFixed(1)}/10
                        </span>
                      </div>
                    )}
                    {turn.scores?.communication_score !== undefined && turn.scores.communication_score !== null && (
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-gray-600">Giao tiếp:</span>
                        <span className={cn('font-bold', getScoreColor(turn.scores.communication_score))}>
                          {turn.scores.communication_score.toFixed(1)}/10
                        </span>
                      </div>
                    )}
                    {turn.scores?.depth_score !== undefined && turn.scores.depth_score !== null && (
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-gray-600">Độ sâu:</span>
                        <span className={cn('font-bold', getScoreColor(turn.scores.depth_score))}>
                          {turn.scores.depth_score.toFixed(1)}/10
                        </span>
                      </div>
                    )}
                    {turn.scores?.overall_score !== undefined && turn.scores.overall_score !== null && (
                      <div className="flex justify-between items-center col-span-2 pt-2 border-t">
                        <span className="text-sm font-medium text-gray-700">Tổng thể:</span>
                        <span className={cn('font-bold text-lg', getScoreColor(turn.scores.overall_score))}>
                          {turn.scores.overall_score.toFixed(1)}/10
                        </span>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            </CollapsibleContent>
          </Collapsible>
        )}

        {/* Timestamp */}
        <div className="flex items-center gap-2 text-xs text-gray-500">
          <Clock className="h-3 w-3" />
          <span>{formatTime(turn.created_at)}</span>
        </div>
      </div>
    </div>
  );
}

/**
 * Main TranscriptView Component
 */
export function TranscriptView({ interviewId, transcript }: TranscriptViewProps) {
  return (
    <div className="space-y-6">
      {/* Header */}
      <Card>
        <CardHeader>
          <CardTitle className="text-2xl">{transcript.job_title}</CardTitle>
          <p className="text-sm text-muted-foreground">
            Tổng số {transcript.total_turns} lượt trao đổi
          </p>
        </CardHeader>
      </Card>

      {/* Transcript Timeline */}
      <div className="space-y-1">
        {transcript.turns.map((turn, index) => (
          <TurnItem key={turn.turn_number} turn={turn} isFirst={index === 0} />
        ))}
      </div>

      {/* Empty State */}
      {transcript.turns.length === 0 && (
        <Card>
          <CardContent className="py-12 text-center">
            <MessageSquare className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600">Không có dữ liệu cuộc trò chuyện</p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
