import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Volume2, Square, Loader2 } from 'lucide-react';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

export default function ResponsePlayer({ text, language }) {
  const [isPlaying, setIsPlaying] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [speed, setSpeed] = useState(1);
  const audioRef = useRef(null);

  const handleSpeedChange = () => {
    const nextSpeed = speed === 1 ? 1.5 : speed === 1.5 ? 2 : 1;
    setSpeed(nextSpeed);
    if (audioRef.current) {
      audioRef.current.playbackRate = nextSpeed;
    }
  };

  const fetchAndPlayAudio = useCallback(async () => {
    if (isPlaying && audioRef.current) {
      audioRef.current.pause();
      audioRef.current = null;
      setIsPlaying(false);
      return;
    }

    if (window.hbCurrentAudio) {
      window.hbCurrentAudio.pause();
      window.dispatchEvent(new Event('hb-stop-audio'));
    }

    setIsLoading(true);
    try {
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
      audio.playbackRate = speed;
      audioRef.current = audio;
      window.hbCurrentAudio = audio;

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
        playPromise.catch(() => {
          setIsPlaying(false);
          audioRef.current = null;
        });
      }
    } catch (error) {
      console.error("Audio Processing Error:", error.message);
    } finally {
      setIsLoading(false);
    }
  }, [text, language, isPlaying, speed]);

  useEffect(() => {
    const stopListener = () => {
      if (audioRef.current && window.hbCurrentAudio !== audioRef.current) {
        setIsPlaying(false);
        audioRef.current = null;
      }
    };
    window.addEventListener('hb-stop-audio', stopListener);
    return () => window.removeEventListener('hb-stop-audio', stopListener);
  }, []);

  return (
    <div className="flex items-center gap-2">
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

      <button
        onClick={handleSpeedChange}
        className="flex items-center justify-center px-2 py-1.5 rounded-lg text-xs font-bold bg-health-surface text-health-textSecondary border border-health-border hover:bg-health-chat hover:text-health-textPrimary transition-colors"
        title="Change playback speed"
      >
        {speed}x
      </button>
    </div>
  );
}