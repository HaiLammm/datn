/**
 * InterviewTranscript Component
 * 
 * Displays conversation history between candidate and AI interviewer.
 * Shows all Q&A exchanges with timestamps and scores.
 * 
 * Features:
 * - Chronological display of turns
 * - Per-turn scores visualization
 * - Collapsible sidebar for space efficiency
 * - Auto-scroll to latest message
 * - Export transcript option (optional)
 * 
 * @example
 * ```tsx
 * <InterviewTranscript
 *   turns={interviewTurns}
 *   isCollapsed={false}
 *   onToggleCollapse={() => setCollapsed(!collapsed)}
 * />
 * ```
 */
'use client';

import { useEffect, useRef } from 'react';
import { MessageSquare, ChevronLeft, ChevronRight, Download } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';
import { cn } from '@/lib/utils';

export interface TurnData {
  id: string;
  turn_number: number;
  ai_message: string;
  candidate_message: string;
  answer_quality?: {
    technical_accuracy: number;
    communication_clarity: number;
    depth_of_knowledge: number;
    overall_score: number;
  };
  action_type?: string;
  created_at: string;
}

export interface InterviewTranscriptProps {
  /**
   * Array of conversation turns.
   */
  turns: TurnData[];

  /**
   * Whether the transcript is collapsed (sidebar mode).
   * @default false
   */
  isCollapsed?: boolean;

  /**
   * Callback when collapse toggle is clicked.
   */
  onToggleCollapse?: () => void;

  /**
   * Whether to show export button.
   * @default false
   */
  showExport?: boolean;

  /**
   * Callback when export button is clicked.
   */
  onExport?: () => void;

  /**
   * Custom className.
   */
  className?: string;
}

export function InterviewTranscript({
  turns,
  isCollapsed = false,
  onToggleCollapse,
  showExport = false,
  onExport,
  className,
}: InterviewTranscriptProps) {
  // Ref for auto-scrolling
  const scrollRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to latest message
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollIntoView({ behavior: 'smooth', block: 'end' });
    }
  }, [turns.length]);

  // Render score badge
  const renderScoreBadge = (score: number) => {
    let variant: 'default' | 'secondary' | 'destructive' | 'outline' = 'secondary';
    let label = 'Average';

    if (score >= 8) {
      variant = 'default';
      label = 'Excellent';
    } else if (score >= 6) {
      variant = 'secondary';
      label = 'Good';
    } else if (score < 5) {
      variant = 'destructive';
      label = 'Needs Improvement';
    }

    return (
      <Badge variant={variant} className="text-xs">
        {score.toFixed(1)} - {label}
      </Badge>
    );
  };

  // Render single turn
  const renderTurn = (turn: TurnData) => {
    return (
      <div key={turn.id} className="space-y-3 pb-4">
        {/* Turn Number */}
        <div className="flex items-center gap-2">
          <MessageSquare className="h-4 w-4 text-muted-foreground" />
          <span className="text-xs font-medium text-muted-foreground">
            Turn {turn.turn_number}
          </span>
          <span className="text-xs text-muted-foreground">
            {new Date(turn.created_at).toLocaleTimeString()}
          </span>
        </div>

        {/* AI Message */}
        <div className="space-y-1">
          <span className="text-xs font-semibold text-primary">AI Interviewer:</span>
          <p className="text-sm text-muted-foreground bg-primary/5 p-2 rounded">
            {turn.ai_message}
          </p>
        </div>

        {/* Candidate Message */}
        <div className="space-y-1">
          <span className="text-xs font-semibold text-foreground">You:</span>
          <p className="text-sm bg-muted p-2 rounded">{turn.candidate_message}</p>
        </div>

        {/* Scores */}
        {turn.answer_quality && (
          <div className="space-y-2 pt-2">
            <span className="text-xs font-medium">Scores:</span>
            <div className="grid grid-cols-2 gap-2 text-xs">
              <div className="flex justify-between">
                <span className="text-muted-foreground">Technical:</span>
                {renderScoreBadge(turn.answer_quality.technical_accuracy)}
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Communication:</span>
                {renderScoreBadge(turn.answer_quality.communication_clarity)}
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Depth:</span>
                {renderScoreBadge(turn.answer_quality.depth_of_knowledge)}
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Overall:</span>
                {renderScoreBadge(turn.answer_quality.overall_score)}
              </div>
            </div>
          </div>
        )}

        <Separator />
      </div>
    );
  };

  // Collapsed view (sidebar icon only)
  if (isCollapsed) {
    return (
      <Button
        onClick={onToggleCollapse}
        variant="outline"
        size="icon"
        className={cn('fixed right-4 top-1/2 -translate-y-1/2 z-50', className)}
      >
        <ChevronLeft className="h-4 w-4" />
      </Button>
    );
  }

  // Full view
  return (
    <Card className={cn('h-full flex flex-col', className)}>
      <CardHeader className="flex-shrink-0">
        <CardTitle className="flex items-center justify-between">
          <span className="flex items-center gap-2">
            <MessageSquare className="h-5 w-5" />
            Interview Transcript
          </span>

          <div className="flex items-center gap-2">
            {showExport && (
              <Button onClick={onExport} variant="ghost" size="sm">
                <Download className="h-4 w-4" />
              </Button>
            )}

            {onToggleCollapse && (
              <Button onClick={onToggleCollapse} variant="ghost" size="icon">
                <ChevronRight className="h-4 w-4" />
              </Button>
            )}
          </div>
        </CardTitle>
      </CardHeader>

      <CardContent className="flex-1 overflow-hidden p-0">
        <ScrollArea className="h-full px-6">
          {turns.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-center text-muted-foreground py-8">
              <MessageSquare className="h-12 w-12 mb-4 opacity-50" />
              <p>No conversation yet.</p>
              <p className="text-sm">Start by answering the first question.</p>
            </div>
          ) : (
            <div className="space-y-4 py-4">
              {turns.map(renderTurn)}
              <div ref={scrollRef} /> {/* Auto-scroll target */}
            </div>
          )}
        </ScrollArea>
      </CardContent>
    </Card>
  );
}
