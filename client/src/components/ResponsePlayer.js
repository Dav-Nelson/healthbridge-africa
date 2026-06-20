import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Volume2, Square, Loader2 } from 'lucide-react';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

export default function ResponsePlayer({ text, language }) {
  const [isPlaying, setIsPlaying] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const audioRef = useRef(null);
  const hasAutoPlayedRef = useRef(false);

  const fetchAndPlayAudio = useCallback(async () => {
    if (isPlaying && audioRef.current) {
      audioRef.current.pause();
      audioRef.current = null;
      setIsPlaying(false);
      return;
    }

    setIsLoading(true);
    try {
      // RESTORED: Sending the full language name exactly as your original code did
      const targetLang = language ? language.toLowerCase() : 'english';

      const response = await fetch(`${API_BASE_URL}/api/voice/speak`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text, language: targetLang }),
      });

      if (!response.ok) throw new Error('Failed to fetch audio from server');

      const contentType = response.headers.get('content-type') || '';
      let audioUrl = '';

      if (contentType.includes('application/json')) {
        const data = await response.json();
        const rawBase64 = data.audio || data.audioContent || data.data;
        if (!rawBase64) throw new Error('JSON structure did not contain audio data');
        audioUrl = `data:audio/mp3;base64,${rawBase64}`;
      } else {
        const audioBlob = await response.blob();
        if (audioBlob.size === 0) throw new Error('Received an empty audio blob file');
        audioUrl = URL.createObjectURL(audioBlob);
      }

      const audio = new Audio(audioUrl);
      audioRef.current = audio;

      audio.onended = () => {
        setIsPlaying(false);
        audioRef.current = null;
        if (!contentType.includes('application/json')) URL.revokeObjectURL(audioUrl);
      };

      audio.onerror = () => {
        setIsPlaying(false);
        audioRef.current = null;
      };

      setIsPlaying(true);
      const playPromise = audio.play();
      if (playPromise !== undefined) {
        playPromise.catch(() => { setIsPlaying(false); audioRef.current = null; });
      }
    } catch (error) {
      console.error("Audio Processing Error:", error.message);
    } finally {
      setIsLoading(false);
    }
  }, [text, language, isPlaying]);

  useEffect(() => {
    if (localStorage.getItem('hb_autoplay') === 'true' && text && !hasAutoPlayedRef.current) {
      hasAutoPlayedRef.current = true;
      const timer = setTimeout(() => fetchAndPlayAudio(), 600);
      return () => clearTimeout(timer);
    }
  }, [text, fetchAndPlayAudio]);

  return (
    <button
      onClick={fetchAndPlayAudio}
      disabled={isLoading}
      className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold transition-colors ${
        isPlaying
          ? 'bg-health-accent/20 text-health-accentLight border border-health-accent'
          : 'bg-health-surface text-health-textSecondary border border-health-border hover:bg-health-chat hover:text-health-textPrimary'
      }`}
    >
      {isLoading ? <Loader2 size={14} className="animate-spin" /> : isPlaying ? <Square size={14} /> : <Volume2 size={14} />}
      {isLoading ? 'Loading...' : isPlaying ? 'Stop' : 'Listen'}
    </button>
  );
}