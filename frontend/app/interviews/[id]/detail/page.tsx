/**
 * Interview Detail Page (Story 8.4)
 * 
 * Displays comprehensive view of a completed interview session with tabs:
 * - Overview: Session metadata and score summary
 * - Transcript: Full conversation history
 * - Evaluation: Comprehensive performance report
 * 
 * Uses new Story 8.4 endpoints for enhanced data structure.
 * 
 * Route: /interviews/[id]/detail
 */

import { redirect, notFound } from 'next/navigation';
import Link from 'next/link';
import { getSession } from '@/lib/auth';
import {
  getInterviewDetailAction,
  getInterviewTranscriptAction,
  getEvaluationDetailAction,
} from '@/features/interviews/actions';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { InterviewScoreGauge } from '@/features/interviews/components/InterviewScoreGauge';
import { TranscriptView } from '@/features/interviews/components/TranscriptView';
import { EvaluationDetailReport } from '@/features/interviews/components/EvaluationDetailReport';
import {
  ArrowLeft,
  Calendar,
  Clock,
  FileText,
  MessageSquare,
  Briefcase,
  BarChart3,
} from 'lucide-react';

interface PageProps {
  params: {
    id: string;
  };
}

/**
 * Format date to readable string
 */
function formatDate(dateString: string): string {
  const date = new Date(dateString);
  return new Intl.DateTimeFormat('vi-VN', {
    year: 'numeric',
    month: 'long',
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
  return `${hours} giờ ${remainingMinutes} phút`;
}

/**
 * Get status badge variant
 */
function getStatusBadge(status: string) {
  switch (status.toLowerCase()) {
    case 'completed':
      return (
        <Badge variant="default" className="bg-green-500">
          Hoàn thành
        </Badge>
      );
    case 'in_progress':
      return (
        <Badge variant="secondary" className="bg-blue-500 text-white">
          Đang thực hiện
        </Badge>
      );
    case 'error':
      return (
        <Badge variant="destructive">
          Lỗi
        </Badge>
      );
    default:
      return <Badge variant="outline">{status}</Badge>;
  }
}

export default async function InterviewDetailPage({ params }: PageProps) {
  // Auth check
  const session = await getSession();
  if (!session) {
    redirect('/login');
  }

  // Fetch data using Story 8.4 endpoints
  const [detailResult, transcriptResult, evaluationResult] = await Promise.all([
    getInterviewDetailAction(params.id),
    getInterviewTranscriptAction(params.id),
    getEvaluationDetailAction(params.id),
  ]);

  // Handle errors
  if (detailResult.error || !detailResult.data) {
    if (detailResult.error?.includes('404') || detailResult.error?.includes('not found')) {
      notFound();
    }
    return (
      <div className="container py-10">
        <Card className="border-red-200 bg-red-50">
          <CardContent className="py-6">
            <p className="text-red-800">Lỗi: {detailResult.error}</p>
          </CardContent>
        </Card>
      </div>
    );
  }

  const detail = detailResult.data;
  const transcript = transcriptResult.data;
  const evaluation = evaluationResult.data;

  return (
    <div className="container py-10 max-w-7xl">
      {/* Header with Navigation */}
      <div className="mb-6 flex items-center justify-between">
        <Button asChild variant="outline">
          <Link href="/interviews/history">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Quay lại Lịch sử
          </Link>
        </Button>
        <Button asChild>
          <Link href="/interviews/new">
            Phỏng vấn mới
          </Link>
        </Button>
      </div>

      {/* Session Header Card */}
      <Card className="mb-6">
        <CardHeader>
          <div className="flex items-start justify-between gap-4">
            <div className="flex-1">
              <CardTitle className="text-3xl mb-2">{detail.job_title}</CardTitle>
              <div className="flex items-center gap-2 mt-2">
                {getStatusBadge(detail.status)}
                {detail.position_level && (
                  <Badge variant="outline" className="capitalize">
                    {detail.position_level}
                  </Badge>
                )}
              </div>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Created At */}
            <div className="flex items-start gap-3">
              <Calendar className="h-5 w-5 text-gray-500 mt-0.5" />
              <div>
                <p className="text-sm text-gray-500">Ngày tạo</p>
                <p className="font-medium">{formatDate(detail.created_at)}</p>
              </div>
            </div>

            {/* Duration */}
            {detail.duration_minutes !== null && detail.duration_minutes !== undefined && (
              <div className="flex items-start gap-3">
                <Clock className="h-5 w-5 text-gray-500 mt-0.5" />
                <div>
                  <p className="text-sm text-gray-500">Thời lượng</p>
                  <p className="font-medium">{formatDuration(detail.duration_minutes)}</p>
                </div>
              </div>
            )}

            {/* Questions */}
            <div className="flex items-start gap-3">
              <FileText className="h-5 w-5 text-gray-500 mt-0.5" />
              <div>
                <p className="text-sm text-gray-500">Số câu hỏi</p>
                <p className="font-medium">{detail.question_count}</p>
              </div>
            </div>

            {/* Turns */}
            <div className="flex items-start gap-3">
              <MessageSquare className="h-5 w-5 text-gray-500 mt-0.5" />
              <div>
                <p className="text-sm text-gray-500">Lượt trao đổi</p>
                <p className="font-medium">{detail.turn_count}</p>
              </div>
            </div>
          </div>

          {/* Job Description (if available) */}
          {detail.job_description && (
            <div className="mt-6 pt-6 border-t">
              <div className="flex items-center gap-2 mb-3">
                <Briefcase className="h-5 w-5 text-gray-500" />
                <h3 className="font-semibold text-gray-700">Mô tả công việc</h3>
              </div>
              <p className="text-sm text-gray-600 whitespace-pre-wrap line-clamp-3">
                {detail.job_description}
              </p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Tabs with Content */}
      <Tabs defaultValue="overview" className="w-full">
        <TabsList className="grid w-full grid-cols-3 max-w-2xl mx-auto">
          <TabsTrigger value="overview">
            <BarChart3 className="h-4 w-4 mr-2" />
            Tổng quan
          </TabsTrigger>
          <TabsTrigger value="transcript">
            <MessageSquare className="h-4 w-4 mr-2" />
            Transcript
          </TabsTrigger>
          <TabsTrigger value="evaluation">
            <FileText className="h-4 w-4 mr-2" />
            Đánh giá
          </TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="mt-6">
          <div className="space-y-6">
            {/* Score Display */}
            {detail.overall_score !== null && detail.overall_score !== undefined && (
              <div className="flex justify-center">
                <InterviewScoreGauge
                  score={detail.overall_score}
                  grade={detail.overall_grade}
                  maxScore={10}
                  size="lg"
                  showLabel={true}
                />
              </div>
            )}

            {/* Hiring Recommendation */}
            {detail.hiring_recommendation && (
              <Card>
                <CardHeader>
                  <CardTitle>Khuyến nghị Tuyển dụng</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-lg">{detail.hiring_recommendation}</p>
                </CardContent>
              </Card>
            )}

            {/* Quick Stats */}
            <Card>
              <CardHeader>
                <CardTitle>Thống kê Nhanh</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="text-center">
                    <div className="text-3xl font-bold text-blue-600">{detail.question_count}</div>
                    <div className="text-sm text-gray-600">Câu hỏi</div>
                  </div>
                  <div className="text-center">
                    <div className="text-3xl font-bold text-green-600">{detail.turn_count}</div>
                    <div className="text-sm text-gray-600">Lượt trao đổi</div>
                  </div>
                  {detail.duration_minutes && (
                    <div className="text-center">
                      <div className="text-3xl font-bold text-purple-600">
                        {detail.duration_minutes}
                      </div>
                      <div className="text-sm text-gray-600">Phút</div>
                    </div>
                  )}
                  {detail.overall_score && (
                    <div className="text-center">
                      <div className="text-3xl font-bold text-yellow-600">
                        {detail.overall_score.toFixed(1)}
                      </div>
                      <div className="text-sm text-gray-600">Điểm</div>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Transcript Tab */}
        <TabsContent value="transcript" className="mt-6">
          {transcript ? (
            <TranscriptView interviewId={params.id} transcript={transcript} />
          ) : (
            <Card>
              <CardContent className="py-12 text-center">
                <MessageSquare className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-600">
                  {transcriptResult.error || 'Không có dữ liệu transcript'}
                </p>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* Evaluation Tab */}
        <TabsContent value="evaluation" className="mt-6">
          {evaluation ? (
            <EvaluationDetailReport evaluation={evaluation} />
          ) : (
            <Card>
              <CardContent className="py-12 text-center">
                <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-xl font-semibold mb-2">Đánh giá chưa sẵn sàng</h3>
                <p className="text-gray-600 mb-4">
                  {evaluationResult.error || 'Buổi phỏng vấn cần được hoàn thành trước khi xem đánh giá'}
                </p>
                {detail.status !== 'completed' && (
                  <Button asChild>
                    <Link href={`/interviews/${params.id}`}>
                      Tiếp tục Phỏng vấn
                    </Link>
                  </Button>
                )}
              </CardContent>
            </Card>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
}
