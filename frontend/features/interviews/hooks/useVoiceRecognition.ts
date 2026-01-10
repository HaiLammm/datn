/**
 * useVoiceRecognition Hook
 * 
 * Custom hook for integrating Web Speech API (Speech Recognition) for voice-to-text functionality.
 * Handles browser compatibility, permission management, and real-time transcription.
 * 
 * Browser Support:
 * - Chrome/Edge: Full support
 * - Firefox: No support (as of 2026)
 * - Safari: Limited support (iOS 14.5+)
 * 
 * @example
 * ```tsx
 * const { transcript, isListening, isSupported, error, startListening, stopListening } = useVoiceRecognition({
 *   lang: 'vi-VN',
 *   continuous: true,
 *   interimResults: true,
 *   onResult: (finalTranscript) => console.log('Final:', finalTranscript),
 *   onError: (error) => console.error('Error:', error),
 * });
 * ```
 */
import { useState, useEffect, useRef, useCallback } from 'react';

// Types for Web Speech API (not natively typed in TypeScript)
interface SpeechRecognitionEvent extends Event {
  results: SpeechRecognitionResultList;
  resultIndex: number;
}

interface SpeechRecognitionErrorEvent extends Event {
  error: string;
  message: string;
}

interface SpeechRecognition extends EventTarget {
  continuous: boolean;
  interimResults: boolean;
  lang: string;
  maxAlternatives: number;
  start: () => void;
  stop: () => void;
  abort: () => void;
  onstart: ((this: SpeechRecognition, ev: Event) => any) | null;
  onend: ((this: SpeechRecognition, ev: Event) => any) | null;
  onresult: ((this: SpeechRecognition, ev: SpeechRecognitionEvent) => any) | null;
  onerror: ((this: SpeechRecognition, ev: SpeechRecognitionErrorEvent) => any) | null;
}

// Global SpeechRecognition constructor (browser-specific)
declare global {
  interface Window {
    SpeechRecognition: new () => SpeechRecognition;
    webkitSpeechRecognition: new () => SpeechRecognition;
  }
}

export interface UseVoiceRecognitionOptions {
  /**
   * Language for speech recognition.
   * @default 'vi-VN' (Vietnamese)
   * @example 'en-US', 'vi-VN'
   */
  lang?: string;

  /**
   * Whether to continue listening after each result.
   * If false, stops after first recognition.
   * @default true
   */
  continuous?: boolean;

  /**
   * Whether to return interim results while speaking.
   * Enables real-time transcription preview.
   * @default true
   */
  interimResults?: boolean;

  /**
   * Number of alternative transcriptions to consider.
   * @default 1
   */
  maxAlternatives?: number;

  /**
   * Callback when final transcript is ready.
   */
  onResult?: (transcript: string) => void;

  /**
   * Callback when recognition error occurs.
   */
  onError?: (error: string) => void;

  /**
   * Callback when recognition starts.
   */
  onStart?: () => void;

  /**
   * Callback when recognition stops.
   */
  onEnd?: () => void;
}

export interface UseVoiceRecognitionReturn {
  /**
   * Current transcript (includes interim results if enabled).
   */
  transcript: string;

  /**
   * Final transcript (only complete results).
   */
  finalTranscript: string;

  /**
   * Whether recognition is currently active.
   */
  isListening: boolean;

  /**
   * Whether Web Speech API is supported in current browser.
   */
  isSupported: boolean;

  /**
   * Current error message (null if no error).
   */
  error: string | null;

  /**
   * Start voice recognition.
   */
  startListening: () => void;

  /**
   * Stop voice recognition gracefully.
   */
  stopListening: () => void;

  /**
   * Abort voice recognition immediately.
   */
  abortListening: () => void;

  /**
   * Reset transcript to empty state.
   */
  resetTranscript: () => void;
}

export function useVoiceRecognition(
  options: UseVoiceRecognitionOptions = {}
): UseVoiceRecognitionReturn {
  const {
    lang = 'vi-VN',
    continuous = true,
    interimResults = true,
    maxAlternatives = 1,
    onResult,
    onError,
    onStart,
    onEnd,
  } = options;

  // State
  const [transcript, setTranscript] = useState<string>('');
  const [finalTranscript, setFinalTranscript] = useState<string>('');
  const [isListening, setIsListening] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Check browser support
  const isSupported =
    typeof window !== 'undefined' &&
    ('SpeechRecognition' in window || 'webkitSpeechRecognition' in window);

  // Ref for SpeechRecognition instance
  const recognitionRef = useRef<SpeechRecognition | null>(null);

  // Refs for callbacks to avoid re-creating recognition instance
  const onResultRef = useRef(onResult);
  const onErrorRef = useRef(onError);
  const onStartRef = useRef(onStart);
  const onEndRef = useRef(onEnd);

  // Update refs when callbacks change
  useEffect(() => {
    onResultRef.current = onResult;
    onErrorRef.current = onError;
    onStartRef.current = onStart;
    onEndRef.current = onEnd;
  }, [onResult, onError, onStart, onEnd]);

  // Initialize SpeechRecognition
  useEffect(() => {
    if (!isSupported) {
      setError('Your browser does not support speech recognition.');
      return;
    }

    const SpeechRecognitionAPI =
      window.SpeechRecognition || window.webkitSpeechRecognition;

    const recognitionInstance = new SpeechRecognitionAPI();
    recognitionInstance.continuous = continuous;
    recognitionInstance.interimResults = interimResults;
    recognitionInstance.lang = lang;
    recognitionInstance.maxAlternatives = maxAlternatives;

    // Event: Recognition starts
    recognitionInstance.onstart = () => {
      setIsListening(true);
      setError(null);
      onStartRef.current?.();
    };

    // Event: Recognition ends
    recognitionInstance.onend = () => {
      setIsListening(false);
      onEndRef.current?.();
    };

    // Event: Recognition result
    recognitionInstance.onresult = (event: SpeechRecognitionEvent) => {
      let interimTranscript = '';
      let finalText = '';

      for (let i = event.resultIndex; i < event.results.length; i++) {
        const result = event.results[i];
        const transcriptPart = result[0].transcript;

        if (result.isFinal) {
          finalText += transcriptPart + ' ';
        } else {
          interimTranscript += transcriptPart;
        }
      }

      // Update interim transcript (real-time preview)
      if (interimTranscript) {
        setTranscript(finalTranscript + interimTranscript);
      }

      // Update final transcript
      if (finalText) {
        const newFinalTranscript = finalTranscript + finalText;
        setFinalTranscript(newFinalTranscript);
        setTranscript(newFinalTranscript);
        onResultRef.current?.(newFinalTranscript.trim());
      }
    };

    // Event: Recognition error
    recognitionInstance.onerror = (event: SpeechRecognitionErrorEvent) => {
      let errorMessage = '';

      switch (event.error) {
        case 'no-speech':
          errorMessage = 'No speech detected. Please try again.';
          break;
        case 'audio-capture':
          errorMessage = 'Microphone not found. Please check your device.';
          break;
        case 'not-allowed':
          errorMessage =
            'Microphone permission denied. Please enable microphone access in your browser settings.';
          break;
        case 'network':
          errorMessage = 'Network error. Please check your internet connection.';
          break;
        case 'aborted':
          errorMessage = 'Speech recognition aborted.';
          break;
        default:
          errorMessage = `Speech recognition error: ${event.error}`;
      }

      setError(errorMessage);
      setIsListening(false);
      onErrorRef.current?.(errorMessage);
    };

    recognitionRef.current = recognitionInstance;

    // Cleanup: only abort if component unmounts
    return () => {
      if (recognitionRef.current) {
        try {
          recognitionRef.current.abort();
        } catch (err) {
          // Ignore errors during cleanup
          console.debug('Cleanup abort error (safe to ignore):', err);
        }
        recognitionRef.current = null;
      }
    };
  }, [
    isSupported,
    lang,
    continuous,
    interimResults,
    maxAlternatives,
    finalTranscript,
  ]);

  // Start listening
  const startListening = useCallback(() => {
    if (!isSupported) {
      setError('Speech recognition is not supported in your browser.');
      return;
    }

    if (recognitionRef.current && !isListening) {
      try {
        recognitionRef.current.start();
      } catch (err) {
        // Handle "recognition already started" error
        console.warn('Speech recognition already started:', err);
      }
    }
  }, [isSupported, isListening]);

  // Stop listening
  const stopListening = useCallback(() => {
    if (recognitionRef.current && isListening) {
      recognitionRef.current.stop();
    }
  }, [isListening]);

  // Abort listening
  const abortListening = useCallback(() => {
    if (recognitionRef.current) {
      recognitionRef.current.abort();
      setIsListening(false);
    }
  }, []);

  // Reset transcript
  const resetTranscript = useCallback(() => {
    setTranscript('');
    setFinalTranscript('');
    setError(null);
  }, []);

  return {
    transcript,
    finalTranscript,
    isListening,
    isSupported,
    error,
    startListening,
    stopListening,
    abortListening,
    resetTranscript,
  };
}
