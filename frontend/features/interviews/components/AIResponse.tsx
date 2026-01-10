/**
 * AIResponse Component
 * 
 * Component for displaying AI responses with text-to-speech (TTS) playback.
 * Shows AI's text response and provides audio playback controls.
 * 
 * Features:
 * - Text-to-speech using Web Speech Synthesis API
 * - Playback controls (play, pause, resume, stop)
 * - Voice selection (male/female if available)
 * - Visual feedback during playback
 * - Auto-play option
 * 
 * @example
 * ```tsx
 * <AIResponse
 *   text="Câu trả lời của bạn rất tốt! Bạn có thể giải thích thêm về..."
 *   autoPlay={true}
 *   onPlaybackEnd={() => console.log('AI finished speaking')}
 * />
 * ```
 */
'use client';

import { useState, useEffect } from 'react';
import {
  Play,
  Pause,
  Square,
  Volume2,
  VolumeX,
  RotateCcw,
  Settings,
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { useSpeechSynthesis } from '../hooks/useSpeechSynthesis';
import { cn } from '@/lib/utils';

export interface AIResponseProps {
  /**
   * AI's text response to speak.
   */
  text: string;

  /**
   * Auto-play audio when component mounts.
   * @default false
   */
  autoPlay?: boolean;

  /**
   * Language for speech synthesis.
   * @default 'vi-VN'
   */
  lang?: string;

  /**
   * Speech rate (speed). Range: 0.5 to 2.0
   * @default 1.0
   */
  rate?: number;

  /**
   * Whether to show voice selection controls.
   * @default true
   */
  showVoiceControls?: boolean;

  /**
   * Callback when playback starts.
   */
  onPlaybackStart?: () => void;

  /**
   * Callback when playback ends.
   */
  onPlaybackEnd?: () => void;

  /**
   * Custom className for styling.
   */
  className?: string;
}

export function AIResponse({
  text,
  autoPlay = false,
  lang = 'vi-VN',
  rate = 1.0,
  showVoiceControls = true,
  onPlaybackStart,
  onPlaybackEnd,
  className,
}: AIResponseProps) {
  // Speech synthesis hook
  const {
    speak,
    cancel,
    pause,
    resume,
    isSpeaking,
    isPaused,
    isSupported,
    voices,
    selectedVoice,
    setVoiceByName,
  } = useSpeechSynthesis({
    lang,
    rate,
    onStart: onPlaybackStart,
    onEnd: onPlaybackEnd,
  });

  // State
  const [showSettings, setShowSettings] = useState<boolean>(false);
  const [hasAutoPlayed, setHasAutoPlayed] = useState<boolean>(false);

  // Filter voices by language
  const availableVoices = voices.filter((voice) =>
    voice.lang.startsWith(lang.split('-')[0])
  );

  // Auto-play on mount if enabled
  useEffect(() => {
    if (autoPlay && !hasAutoPlayed && text && isSupported) {
      speak(text);
      setHasAutoPlayed(true);
    }
  }, [autoPlay, hasAutoPlayed, text, isSupported, speak]);

  // Handle play button
  const handlePlay = () => {
    if (isPaused) {
      resume();
    } else {
      speak(text);
    }
  };

  // Handle replay button
  const handleReplay = () => {
    cancel();
    setTimeout(() => speak(text), 100); // Small delay to ensure cancel completes
  };

  // Render voice selection
  const renderVoiceSettings = () => {
    if (!showSettings || !showVoiceControls) return null;

    return (
      <div className="space-y-3 pt-4 border-t">
        <div className="flex items-center justify-between">
          <label className="text-sm font-medium">Select Voice:</label>
          <Select
            value={selectedVoice?.name || ''}
            onValueChange={setVoiceByName}
            disabled={isSpeaking}
          >
            <SelectTrigger className="w-[200px]">
              <SelectValue placeholder="Choose voice..." />
            </SelectTrigger>
            <SelectContent>
              {availableVoices.length > 0 ? (
                availableVoices.map((voice) => (
                  <SelectItem key={voice.name} value={voice.name}>
                    {voice.name} ({voice.lang})
                  </SelectItem>
                ))
              ) : (
                <SelectItem value="none" disabled>
                  No voices available
                </SelectItem>
              )}
            </SelectContent>
          </Select>
        </div>

        <p className="text-xs text-muted-foreground">
          {selectedVoice
            ? `Using: ${selectedVoice.name}`
            : 'No voice selected'}
        </p>
      </div>
    );
  };

  // Render browser not supported message
  if (!isSupported) {
    return (
      <Alert className={className}>
        <VolumeX className="h-4 w-4" />
        <AlertDescription>
          Your browser does not support text-to-speech. Please read the text
          response below.
        </AlertDescription>
      </Alert>
    );
  }

  return (
    <Card className={cn('transition-all duration-300', className)}>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <span className="flex items-center gap-2">
            <Volume2 className="h-5 w-5 text-primary" />
            AI Interviewer Response
          </span>

          {/* Status Badge */}
          <Badge
            variant={isSpeaking ? 'default' : 'secondary'}
            className={cn(isSpeaking && 'animate-pulse')}
          >
            {isSpeaking ? (isPaused ? 'Paused' : 'Speaking...') : 'Ready'}
          </Badge>
        </CardTitle>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* AI Response Text */}
        <div className="p-4 bg-muted/50 rounded-lg border-l-4 border-primary">
          <p className="text-base leading-relaxed whitespace-pre-wrap">{text}</p>
        </div>

        {/* Playback Controls */}
        <div className="flex items-center gap-2 flex-wrap">
          {!isSpeaking && !isPaused && (
            <Button onClick={handlePlay} size="sm">
              <Play className="mr-2 h-4 w-4" />
              Play Audio
            </Button>
          )}

          {isSpeaking && !isPaused && (
            <Button onClick={pause} size="sm" variant="secondary">
              <Pause className="mr-2 h-4 w-4" />
              Pause
            </Button>
          )}

          {isPaused && (
            <Button onClick={resume} size="sm">
              <Play className="mr-2 h-4 w-4" />
              Resume
            </Button>
          )}

          {(isSpeaking || isPaused) && (
            <Button onClick={cancel} size="sm" variant="destructive">
              <Square className="mr-2 h-4 w-4" />
              Stop
            </Button>
          )}

          {!isSpeaking && !isPaused && (
            <Button onClick={handleReplay} size="sm" variant="outline">
              <RotateCcw className="mr-2 h-4 w-4" />
              Replay
            </Button>
          )}

          {showVoiceControls && (
            <Button
              onClick={() => setShowSettings(!showSettings)}
              size="sm"
              variant="ghost"
              className="ml-auto"
            >
              <Settings className="mr-2 h-4 w-4" />
              {showSettings ? 'Hide' : 'Voice Settings'}
            </Button>
          )}
        </div>

        {/* Voice Settings */}
        {renderVoiceSettings()}

        {/* Visual Feedback */}
        {isSpeaking && !isPaused && (
          <div className="flex justify-center items-center gap-2 h-8 py-2">
            {[...Array(7)].map((_, i) => (
              <div
                key={i}
                className="w-1 bg-primary rounded-full animate-waveform"
                style={{
                  animationDelay: `${i * 0.15}s`,
                  height: '100%',
                }}
              />
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

// Add custom animation to globals.css or tailwind.config.ts
// @keyframes waveform {
//   0%, 100% { transform: scaleY(0.3); }
//   50% { transform: scaleY(1); }
// }
