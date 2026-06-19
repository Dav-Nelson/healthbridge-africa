import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Volume2, Square, Loader2 } from 'lucide-react';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';
const SPEED_OPTIONS = [0.75, 1, 1.25, 1.5];

export default function ResponsePlayer({ text, language }) {
  const [isPlaying, setIsPlaying] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [speed, setSpeed] = useState(() => {
    const saved = parseFloat(localStorage.getItem('hb_playback_speed'));
    return SPEED_OPTIONS.includes(saved) ? saved : 1;
  });
  const audioRef = useRef(null);

  const shouldAutoPlay = () => localStorage.getItem('hb_autoplay') === 'true';

  const handleSpeedChange = (e) => {
    const newSpeed = parseFloat(e.target.value);
    setSpeed(newSpeed);
    localStorage.setItem('hb_playback_speed', newSpeed);
    if (audioRef.current) {
      audioRef.current.playbackRate = newSpeed;
    }
  };

  const fetchAndPlayAudio = useCallback(async () => {
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
      audio.playbackRate = speed;
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
  }, [text, language, speed, isPlaying]);

  useEffect(() => {
    if (shouldAutoPlay() && text) {
      const timer = setTimeout(() => {
        fetchAndPlayAudio();
      }, 600);
      return () => clearTimeout(timer);
    }
  }, [fetchAndPlayAudio, text]);

  return (
    <div className="flex items-center gap-2">
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

      <select
        value={speed}
        onChange={handleSpeedChange}
        className="text-xs px-2 py-1.5 rounded-lg border border-slate-200 bg-white text-slate-600 cursor-pointer hover:bg-slate-50 focus:outline-none"
        title="Playback speed"
      >
        {SPEED_OPTIONS.map((s) => (
          <option key={s} value={s}>
            {s === 1 ? '1x' : `${s}x`}
          </option>
        ))}
      </select>
    </div>
  );
}