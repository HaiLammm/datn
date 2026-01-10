/**
 * VoiceInput Component
 * 
 * Voice input component with Web Speech API integration for real-time voice-to-text transcription.
 * Displays recording status, live transcription preview, and handles browser compatibility.
 * 
 * Features:
 * - Real-time voice-to-text transcription
 * - Visual feedback (waveform animation) during recording
 * - Microphone permission handling
 * - Browser compatibility checks
 * - Error handling with user-friendly messages
 * - Manual text input fallback
 * 
 * @example
 * ```tsx
 * <VoiceInput
 *   onTranscriptComplete={(transcript) => console.log('User said:', transcript)}
 *   onError={(error) => console.error('Voice error:', error)}
 *   disabled={false}
 * />
 * ```
 */
'use client';

import { useState, useEffect, useCallback } from 'react';
import { Mic, MicOff, Loader2, AlertCircle, Keyboard } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { useVoiceRecognition } from '../hooks/useVoiceRecognition';
import { cn } from '@/lib/utils';

export interface VoiceInputProps {
  /**
   * Callback when final transcript is complete.
   */
  onTranscriptComplete: (transcript: string) => void;

  /**
   * Callback when error occurs.
   */
  onError?: (error: string) => void;

  /**
   * Language for speech recognition.
   * @default 'vi-VN'
   */
  lang?: string;

  /**
   * Placeholder text for manual input fallback.
   */
  placeholder?: string;

  /**
   * Whether the input is disabled.
   */
  disabled?: boolean;

  /**
   * Whether to show manual input option.
   * @default true
   */
  showManualInput?: boolean;
}

export function VoiceInput({
  onTranscriptComplete,
  onError,
  lang = 'vi-VN',
  placeholder = 'Nhập câu trả lời của bạn...',
  disabled = false,
  showManualInput = true,
}: VoiceInputProps) {
  // State
  const [inputMode, setInputMode] = useState<'voice' | 'manual'>('voice');
  const [manualText, setManualText] = useState<string>('');

  // Memoize callbacks to prevent useEffect re-runs in useVoiceRecognition hook
  const handleVoiceResult = useCallback(
    (text: string) => {
      onTranscriptComplete(text);
    },
    [onTranscriptComplete]
  );

  const handleVoiceError = useCallback(
    (err: string) => {
      onError?.(err);
    },
    [onError]
  );

  // Voice recognition hook
  const {
    transcript,
    finalTranscript,
    isListening,
    isSupported,
    error: voiceError,
    startListening,
    stopListening,
    resetTranscript,
  } = useVoiceRecognition({
    lang,
    continuous: false, // Stop after user finishes speaking
    interimResults: true, // Show real-time preview
    onResult: handleVoiceResult,
    onError: handleVoiceError,
  });

  // Handle browser incompatibility
  useEffect(() => {
    if (!isSupported && inputMode === 'voice') {
      // Auto-switch to manual input if voice not supported
      setInputMode('manual');
      onError?.('Voice input not supported. Switched to manual input mode.');
    }
  }, [isSupported, inputMode, onError]);

  // Handle manual input submission
  const handleManualSubmit = () => {
    if (manualText.trim()) {
      onTranscriptComplete(manualText.trim());
      setManualText('');
    }
  };

  // Toggle input mode
  const toggleInputMode = () => {
    if (isListening) {
      stopListening();
    }
    setInputMode((prev) => (prev === 'voice' ? 'manual' : 'voice'));
  };

  // Render error alert
  const renderError = () => {
    if (!voiceError) return null;

    return (
      <Alert variant="destructive" className="mb-4">
        <AlertCircle className="h-4 w-4" />
        <AlertDescription>{voiceError}</AlertDescription>
      </Alert>
    );
  };

  // Render browser compatibility warning
  const renderCompatibilityWarning = () => {
    if (isSupported || inputMode === 'manual') return null;

    return (
      <Alert className="mb-4">
        <AlertCircle className="h-4 w-4" />
        <AlertDescription>
          Your browser does not support voice input. Please use{' '}
          <strong>Chrome</strong> or <strong>Edge</strong> for the best experience, or
          switch to manual input mode.
        </AlertDescription>
      </Alert>
    );
  };

  // Render voice input UI
  const renderVoiceInput = () => {
    return (
      <div className="space-y-4">
        <Card
          className={cn(
            'transition-all duration-300',
            isListening && 'border-primary shadow-lg shadow-primary/20'
          )}
        >
          <CardContent className="p-6 space-y-4">
            {/* Status Badge */}
            <div className="flex justify-between items-center">
              <Badge
                variant={isListening ? 'default' : 'secondary'}
                className="text-sm"
              >
                {isListening ? 'Listening...' : 'Ready'}
              </Badge>

              {showManualInput && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={toggleInputMode}
                  disabled={disabled || isListening}
                >
                  <Keyboard className="mr-2 h-4 w-4" />
                  Switch to Manual Input
                </Button>
              )}
            </div>

            {/* Microphone Button */}
            <div className="flex flex-col items-center gap-4">
              <Button
                size="lg"
                variant={isListening ? 'destructive' : 'default'}
                className={cn(
                  'w-20 h-20 rounded-full transition-all duration-300',
                  isListening && 'animate-pulse'
                )}
                onClick={isListening ? stopListening : startListening}
                disabled={disabled || !isSupported}
              >
                {isListening ? (
                  <MicOff className="h-8 w-8" />
                ) : (
                  <Mic className="h-8 w-8" />
                )}
              </Button>

              <p className="text-sm text-muted-foreground text-center">
                {isListening
                  ? 'Speak now... Click to stop recording'
                  : 'Click microphone to start recording'}
              </p>
            </div>

            {/* Waveform Animation (Visual Feedback) */}
            {isListening && (
              <div className="flex justify-center items-center gap-1 h-12">
                {[...Array(5)].map((_, i) => (
                  <div
                    key={i}
                    className="w-1 bg-primary rounded-full animate-waveform"
                    style={{
                      animationDelay: `${i * 0.1}s`,
                      height: '100%',
                    }}
                  />
                ))}
              </div>
            )}

            {/* Transcript Preview */}
            {transcript && (
              <div className="mt-4 p-4 bg-muted rounded-lg">
                <p className="text-sm font-medium mb-2">Transcript Preview:</p>
                <p className="text-base">{transcript}</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    );
  };

  // Render manual input UI
  const renderManualInput = () => {
    return (
      <div className="space-y-4">
        <Card>
          <CardContent className="p-6 space-y-4">
            {/* Status Badge */}
            <div className="flex justify-between items-center">
              <Badge variant="secondary" className="text-sm">
                Manual Input Mode
              </Badge>

              {showManualInput && isSupported && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={toggleInputMode}
                  disabled={disabled}
                >
                  <Mic className="mr-2 h-4 w-4" />
                  Switch to Voice Input
                </Button>
              )}
            </div>

            {/* Textarea */}
            <Textarea
              value={manualText}
              onChange={(e) => setManualText(e.target.value)}
              placeholder={placeholder}
              disabled={disabled}
              rows={6}
              className="resize-none"
              onKeyDown={(e) => {
                if (e.key === 'Enter' && e.ctrlKey) {
                  e.preventDefault();
                  handleManualSubmit();
                }
              }}
            />

            {/* Submit Button */}
            <Button
              onClick={handleManualSubmit}
              disabled={disabled || !manualText.trim()}
              className="w-full"
            >
              Submit Answer
            </Button>

            <p className="text-xs text-muted-foreground text-center">
              Press <kbd className="px-1 py-0.5 bg-muted rounded">Ctrl</kbd> +{' '}
              <kbd className="px-1 py-0.5 bg-muted rounded">Enter</kbd> to submit
            </p>
          </CardContent>
        </Card>
      </div>
    );
  };

  return (
    <div className="w-full">
      {renderError()}
      {renderCompatibilityWarning()}

      {inputMode === 'voice' ? renderVoiceInput() : renderManualInput()}
    </div>
  );
}

// Add custom animation to globals.css or tailwind.config.ts
// @keyframes waveform {
//   0%, 100% { transform: scaleY(0.3); }
//   50% { transform: scaleY(1); }
// }
