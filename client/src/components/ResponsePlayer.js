import React, { useState, useEffect, useRef } from 'react';
import { Volume2, Square, Loader2 } from 'lucide-react';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

export default function ResponsePlayer({ text, language }) {
  const [isPlaying, setIsPlaying] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const audioRef = useRef(null);

  // Read auto-play preference from localStorage
  const shouldAutoPlay = () => localStorage.getItem('hb_autoplay') === 'true';

  const fetchAndPlayAudio = async () => {
    if (isPlaying && audioRef.current) {
      audioRef.current.pause();
      audioRef.current = null;
      setIsPlaying(false);
      return;
    }

    setIsLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/voice/speak`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text,
          language: language ? language.toLowerCase() : 'en'
        }),
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
        if (!contentType.includes('application/json')) {
          URL.revokeObjectURL(audioUrl);
        }
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
  };

  // Auto-play when the component mounts if preference is enabled
  useEffect(() => {
    if (shouldAutoPlay() && text) {
      // Small delay to let the UI render first before firing the audio request
      const timer = setTimeout(() => {
        fetchAndPlayAudio();
      }, 600);
      return () => clearTimeout(timer);
    }
  }, []);

  return (
    <button
      onClick={fetchAndPlayAudio}
      disabled={isLoading}
      className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
        isPlaying
          ? 'bg-teal-100 text-teal-800 border border-teal-200'
          : 'bg-white text-slate-600 border border-slate-200 hover:bg-slate-50'
      }`}
    >
      {isLoading ? (
        <Loader2 size={16} className="animate-spin" />
      ) : isPlaying ? (
        <Square size={16} />
      ) : (
        <Volume2 size={16} />
      )}
      {isLoading ? 'Loading...' : isPlaying ? 'Stop' : 'Listen'}
    </button>
  );
}