/**
 * Test Page for Voice Components (Story 8.2)
 * 
 * This page allows testing individual components without full interview flow.
 * Access at: http://localhost:3000/test/voice-components
 */
'use client';

import { useState, useEffect } from 'react';
import dynamic from 'next/dynamic';
import { TurnData } from '@/features/interviews/components/InterviewTranscript';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';

// Dynamic imports to avoid SSR hydration mismatch
const VoiceInput = dynamic(
  () => import('@/features/interviews/components/VoiceInput').then(mod => ({ default: mod.VoiceInput })),
  { ssr: false }
);

const AIResponse = dynamic(
  () => import('@/features/interviews/components/AIResponse').then(mod => ({ default: mod.AIResponse })),
  { ssr: false }
);

const InterviewTranscript = dynamic(
  () => import('@/features/interviews/components/InterviewTranscript').then(mod => ({ default: mod.InterviewTranscript })),
  { ssr: false }
);

export default function VoiceComponentsTestPage() {
  // State for VoiceInput test
  const [transcript, setTranscript] = useState<string>('');
  const [voiceError, setVoiceError] = useState<string>('');

  // State for AIResponse test
  const [aiResponseText, setAiResponseText] = useState<string>(
    'Câu trả lời của bạn rất tốt! Bạn đã đề cập đến các khái niệm quan trọng như SOLID principles và design patterns. Tuy nhiên, tôi muốn đào sâu hơn về cách bạn áp dụng Dependency Injection trong dự án thực tế. Bạn có thể cho tôi một ví dụ cụ thể không?'
  );

  // State for browser info (client-only)
  const [browserInfo, setBrowserInfo] = useState<{
    userAgent: string;
    speechRecognitionSupported: boolean;
    speechSynthesisSupported: boolean;
  }>({
    userAgent: 'Loading...',
    speechRecognitionSupported: false,
    speechSynthesisSupported: false,
  });

  // State for Transcript test
  const [mockTurns, setMockTurns] = useState<TurnData[]>([
    {
      id: '1',
      turn_number: 1,
      ai_message: 'Xin chào! Câu hỏi đầu tiên: Hãy giải thích về SOLID principles trong lập trình hướng đối tượng.',
      candidate_message: 'SOLID là 5 nguyên tắc cơ bản: Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, và Dependency Inversion. Chúng giúp code dễ maintain và scale hơn.',
      answer_quality: {
        technical_accuracy: 8.5,
        communication_clarity: 7.5,
        depth_of_knowledge: 7.0,
        overall_score: 7.7,
      },
      action_type: 'follow_up',
      created_at: new Date(Date.now() - 120000).toISOString(),
    },
    {
      id: '2',
      turn_number: 2,
      ai_message: 'Tốt! Bạn có thể cho ví dụ cụ thể về Open/Closed Principle không?',
      candidate_message: 'Ví dụ như khi thiết kế payment system, thay vì modify code gốc khi thêm payment method mới, ta nên dùng interface PaymentMethod rồi implement các class như CreditCardPayment, PayPalPayment...',
      answer_quality: {
        technical_accuracy: 9.0,
        communication_clarity: 8.5,
        depth_of_knowledge: 8.5,
        overall_score: 8.7,
      },
      action_type: 'next_question',
      created_at: new Date(Date.now() - 60000).toISOString(),
    },
  ]);

  // Detect browser capabilities after mount (client-side only)
  useEffect(() => {
    if (typeof window !== 'undefined') {
      setBrowserInfo({
        userAgent: navigator.userAgent.split(' ').pop() || 'Unknown',
        speechRecognitionSupported: 'SpeechRecognition' in window || 'webkitSpeechRecognition' in window,
        speechSynthesisSupported: 'speechSynthesis' in window,
      });
    }
  }, []);

  const handleTranscriptComplete = (text: string) => {
    setTranscript(text);
    console.log('✅ Transcript received:', text);
    
    // Simulate adding to conversation
    const newTurn: TurnData = {
      id: String(mockTurns.length + 1),
      turn_number: mockTurns.length + 1,
      ai_message: 'Đây là phản hồi AI mô phỏng...',
      candidate_message: text,
      answer_quality: {
        technical_accuracy: Math.random() * 10,
        communication_clarity: Math.random() * 10,
        depth_of_knowledge: Math.random() * 10,
        overall_score: Math.random() * 10,
      },
      created_at: new Date().toISOString(),
    };
    setMockTurns([...mockTurns, newTurn]);
  };

  const handleVoiceError = (error: string) => {
    setVoiceError(error);
    console.error('❌ Voice error:', error);
  };

  return (
    <div className="container mx-auto py-8 space-y-8">
      <div className="space-y-2">
        <h1 className="text-3xl font-bold">Voice Components Test Page</h1>
        <p className="text-muted-foreground">
          Test individual components for Story 8.2: Voice Interaction with AI Interviewer
        </p>
        <Badge variant="outline">Story 8.2 - Test Environment</Badge>
      </div>

      <Tabs defaultValue="voice-input" className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="voice-input">Voice Input</TabsTrigger>
          <TabsTrigger value="ai-response">AI Response</TabsTrigger>
          <TabsTrigger value="transcript">Transcript</TabsTrigger>
        </TabsList>

        {/* Tab 1: Voice Input Test */}
        <TabsContent value="voice-input" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>VoiceInput Component Test</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <p className="text-sm text-muted-foreground">
                  🎤 Test voice recording or manual text input. Check browser console for logs.
                </p>
                <ul className="text-xs text-muted-foreground list-disc list-inside space-y-1">
                  <li><strong>Chrome/Edge:</strong> Full voice support</li>
                  <li><strong>Firefox:</strong> Manual input only (no Speech Recognition)</li>
                  <li><strong>Safari:</strong> Limited voice support (iOS 14.5+)</li>
                </ul>
              </div>

              <Separator />

              <VoiceInput
                onTranscriptComplete={handleTranscriptComplete}
                onError={handleVoiceError}
                lang="vi-VN"
                placeholder="Nhập câu trả lời của bạn hoặc dùng microphone..."
                showManualInput={true}
              />

              <Separator />

              <div className="space-y-2">
                <h3 className="font-semibold">Transcript Result:</h3>
                {transcript ? (
                  <div className="p-4 bg-green-50 dark:bg-green-950 rounded border border-green-200 dark:border-green-800">
                    <p className="text-sm">{transcript}</p>
                  </div>
                ) : (
                  <p className="text-sm text-muted-foreground italic">No transcript yet. Try speaking or typing.</p>
                )}
              </div>

              {voiceError && (
                <div className="p-4 bg-red-50 dark:bg-red-950 rounded border border-red-200 dark:border-red-800">
                  <p className="text-sm text-red-600 dark:text-red-400">{voiceError}</p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Tab 2: AI Response Test */}
        <TabsContent value="ai-response" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>AIResponse Component Test</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <p className="text-sm text-muted-foreground">
                  🔊 Test text-to-speech playback. Click "Play Audio" to hear the AI response.
                </p>
              </div>

              <Separator />

              <div className="space-y-2">
                <label className="text-sm font-medium">Edit AI Response Text:</label>
                <textarea
                  value={aiResponseText}
                  onChange={(e) => setAiResponseText(e.target.value)}
                  className="w-full p-3 border rounded-lg min-h-[100px] font-mono text-sm"
                  placeholder="Enter AI response text..."
                />
              </div>

              <AIResponse
                text={aiResponseText}
                autoPlay={false}
                lang="vi-VN"
                rate={1.0}
                showVoiceControls={true}
                onPlaybackStart={() => console.log('🔊 TTS started')}
                onPlaybackEnd={() => console.log('✅ TTS ended')}
              />
            </CardContent>
          </Card>
        </TabsContent>

        {/* Tab 3: Transcript Test */}
        <TabsContent value="transcript" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>InterviewTranscript Component Test</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <p className="text-sm text-muted-foreground">
                  💬 Test conversation history display. Transcript updates as you submit answers in the Voice Input tab.
                </p>
              </div>

              <Separator />

              <div className="h-[500px]">
                <InterviewTranscript
                  turns={mockTurns}
                  isCollapsed={false}
                  showExport={false}
                />
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Debug Info */}
      <Card>
        <CardHeader>
          <CardTitle>Debug Info</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <strong>Browser:</strong> {browserInfo.userAgent}
            </div>
            <div>
              <strong>Speech Recognition:</strong>{' '}
              {browserInfo.speechRecognitionSupported ? (
                <Badge variant="default">Supported ✓</Badge>
              ) : (
                <Badge variant="destructive">Not Supported ✗</Badge>
              )}
            </div>
            <div>
              <strong>Speech Synthesis:</strong>{' '}
              {browserInfo.speechSynthesisSupported ? (
                <Badge variant="default">Supported ✓</Badge>
              ) : (
                <Badge variant="destructive">Not Supported ✗</Badge>
              )}
            </div>
            <div>
              <strong>Total Turns:</strong> {mockTurns.length}
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
