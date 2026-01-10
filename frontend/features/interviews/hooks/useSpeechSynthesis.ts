/**
 * useSpeechSynthesis Hook
 * 
 * Custom hook for integrating Web Speech Synthesis API for text-to-speech functionality.
 * Handles browser compatibility, voice selection, and playback controls.
 * 
 * Browser Support:
 * - Chrome/Edge: Full support with multiple voices
 * - Firefox: Full support
 * - Safari: Full support
 * 
 * @example
 * ```tsx
 * const { speak, cancel, pause, resume, isSpeaking, isPaused, voices, selectedVoice, setSelectedVoice } = useSpeechSynthesis({
 *   lang: 'vi-VN',
 *   rate: 1.0,
 *   pitch: 1.0,
 *   volume: 1.0,
 *   onEnd: () => console.log('Speech finished'),
 * });
 * 
 * speak('Xin chào, đây là AI phỏng vấn của bạn.');
 * ```
 */
import { useState, useEffect, useRef, useCallback } from 'react';

export interface UseSpeechSynthesisOptions {
  /**
   * Language for speech synthesis.
   * @default 'vi-VN' (Vietnamese)
   * @example 'en-US', 'vi-VN'
   */
  lang?: string;

  /**
   * Speech rate (speed).
   * Range: 0.1 to 10 (1.0 is normal speed)
   * @default 1.0
   */
  rate?: number;

  /**
   * Speech pitch (tone).
   * Range: 0 to 2 (1.0 is normal pitch)
   * @default 1.0
   */
  pitch?: number;

  /**
   * Speech volume.
   * Range: 0 to 1 (1.0 is max volume)
   * @default 1.0
   */
  volume?: number;

  /**
   * Voice name to use (optional).
   * If not specified, uses default voice for language.
   */
  voiceName?: string;

  /**
   * Callback when speech starts.
   */
  onStart?: () => void;

  /**
   * Callback when speech ends.
   */
  onEnd?: () => void;

  /**
   * Callback when speech pauses.
   */
  onPause?: () => void;

  /**
   * Callback when speech resumes.
   */
  onResume?: () => void;

  /**
   * Callback when speech error occurs.
   */
  onError?: (error: SpeechSynthesisErrorEvent) => void;
}

export interface UseSpeechSynthesisReturn {
  /**
   * Speak the given text.
   * Cancels any currently speaking text.
   */
  speak: (text: string) => void;

  /**
   * Cancel current speech immediately.
   */
  cancel: () => void;

  /**
   * Pause current speech.
   */
  pause: () => void;

  /**
   * Resume paused speech.
   */
  resume: () => void;

  /**
   * Whether speech is currently playing.
   */
  isSpeaking: boolean;

  /**
   * Whether speech is currently paused.
   */
  isPaused: boolean;

  /**
   * Whether Web Speech Synthesis API is supported in current browser.
   */
  isSupported: boolean;

  /**
   * List of available voices in browser.
   */
  voices: SpeechSynthesisVoice[];

  /**
   * Currently selected voice.
   */
  selectedVoice: SpeechSynthesisVoice | null;

  /**
   * Set voice by voice object.
   */
  setSelectedVoice: (voice: SpeechSynthesisVoice | null) => void;

  /**
   * Set voice by voice name.
   */
  setVoiceByName: (voiceName: string) => void;
}

export function useSpeechSynthesis(
  options: UseSpeechSynthesisOptions = {}
): UseSpeechSynthesisReturn {
  const {
    lang = 'vi-VN',
    rate = 1.0,
    pitch = 1.0,
    volume = 1.0,
    voiceName,
    onStart,
    onEnd,
    onPause,
    onResume,
    onError,
  } = options;

  // State
  const [isSpeaking, setIsSpeaking] = useState<boolean>(false);
  const [isPaused, setIsPaused] = useState<boolean>(false);
  const [voices, setVoices] = useState<SpeechSynthesisVoice[]>([]);
  const [selectedVoice, setSelectedVoice] = useState<SpeechSynthesisVoice | null>(null);

  // Check browser support
  const isSupported =
    typeof window !== 'undefined' && 'speechSynthesis' in window;

  // Ref for current utterance
  const utteranceRef = useRef<SpeechSynthesisUtterance | null>(null);

  // Load available voices
  useEffect(() => {
    if (!isSupported) return;

    const loadVoices = () => {
      const availableVoices = window.speechSynthesis.getVoices();
      setVoices(availableVoices);

      // Auto-select voice
      if (!selectedVoice) {
        // Try to find voice matching language
        const matchingVoice = availableVoices.find(
          (v) => v.lang.startsWith(lang.split('-')[0])
        );

        // Or use voice by name if specified
        const namedVoice = voiceName
          ? availableVoices.find((v) => v.name === voiceName)
          : null;

        setSelectedVoice(namedVoice || matchingVoice || availableVoices[0] || null);
      }
    };

    // Load voices immediately
    loadVoices();

    // Some browsers load voices asynchronously
    if (window.speechSynthesis.onvoiceschanged !== undefined) {
      window.speechSynthesis.onvoiceschanged = loadVoices;
    }

    return () => {
      if (window.speechSynthesis.onvoiceschanged !== undefined) {
        window.speechSynthesis.onvoiceschanged = null;
      }
    };
  }, [isSupported, lang, voiceName, selectedVoice]);

  // Update speaking/paused state
  useEffect(() => {
    if (!isSupported) return;

    const checkStatus = () => {
      setIsSpeaking(window.speechSynthesis.speaking);
      setIsPaused(window.speechSynthesis.paused);
    };

    const intervalId = setInterval(checkStatus, 100);

    return () => clearInterval(intervalId);
  }, [isSupported]);

  // Speak function
  const speak = useCallback(
    (text: string) => {
      if (!isSupported) {
        console.warn('Speech synthesis is not supported in this browser.');
        return;
      }

      // Cancel any ongoing speech
      window.speechSynthesis.cancel();

      // Create new utterance
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = lang;
      utterance.rate = rate;
      utterance.pitch = pitch;
      utterance.volume = volume;

      if (selectedVoice) {
        utterance.voice = selectedVoice;
      }

      // Event handlers
      utterance.onstart = () => {
        setIsSpeaking(true);
        setIsPaused(false);
        onStart?.();
      };

      utterance.onend = () => {
        setIsSpeaking(false);
        setIsPaused(false);
        onEnd?.();
      };

      utterance.onpause = () => {
        setIsPaused(true);
        onPause?.();
      };

      utterance.onresume = () => {
        setIsPaused(false);
        onResume?.();
      };

      utterance.onerror = (event) => {
        setIsSpeaking(false);
        setIsPaused(false);
        console.error('Speech synthesis error:', event);
        onError?.(event);
      };

      // Store reference
      utteranceRef.current = utterance;

      // Start speaking
      window.speechSynthesis.speak(utterance);
    },
    [
      isSupported,
      lang,
      rate,
      pitch,
      volume,
      selectedVoice,
      onStart,
      onEnd,
      onPause,
      onResume,
      onError,
    ]
  );

  // Cancel function
  const cancel = useCallback(() => {
    if (!isSupported) return;
    window.speechSynthesis.cancel();
    setIsSpeaking(false);
    setIsPaused(false);
  }, [isSupported]);

  // Pause function
  const pause = useCallback(() => {
    if (!isSupported) return;
    window.speechSynthesis.pause();
    setIsPaused(true);
  }, [isSupported]);

  // Resume function
  const resume = useCallback(() => {
    if (!isSupported) return;
    window.speechSynthesis.resume();
    setIsPaused(false);
  }, [isSupported]);

  // Set voice by name
  const setVoiceByName = useCallback(
    (name: string) => {
      const voice = voices.find((v) => v.name === name);
      if (voice) {
        setSelectedVoice(voice);
      }
    },
    [voices]
  );

  return {
    speak,
    cancel,
    pause,
    resume,
    isSpeaking,
    isPaused,
    isSupported,
    voices,
    selectedVoice,
    setSelectedVoice,
    setVoiceByName,
  };
}
