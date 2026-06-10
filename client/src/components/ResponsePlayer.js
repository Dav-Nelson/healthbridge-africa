import React, { useState } from 'react';
import { Volume2, Square, Loader2 } from 'lucide-react';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

export default function ResponsePlayer({ text, language }) {
  const [isPlaying, setIsPlaying] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [audioElement, setAudioElement] = useState(null);

  const handlePlayAudio = async () => {
    if (isPlaying && audioElement) {
      audioElement.pause();
      setIsPlaying(false);
      return;
    }

    setIsLoading(true);
    try {
      // FIX: Route through API_BASE_URL to prevent CORS/direct stream blocks
      const response = await fetch(`${API_BASE_URL}/api/voice/speak`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text, language: language ? language.toLowerCase() : 'en' }),
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

      const audio = new Audio();
      audio.src = audioUrl;
      
      audio.onended = () => {
        setIsPlaying(false);
        if (!contentType.includes('application/json')) {
          URL.revokeObjectURL(audioUrl);
        }
      };

      audio.onerror = (e) => {
        console.error("Browser media playback engine failed to decode audio source:", e);
        setIsPlaying(false);
        alert("Audio rendering issue. Please check device output codec.");
      };

      setAudioElement(audio);
      setIsPlaying(true);
      
      const playPromise = audio.play();
      if (playPromise !== undefined) {
        playPromise.catch(err => {
          console.error("Playback blocked by browser autoplay rules:", err);
          setIsPlaying(false);
        });
      }

    } catch (error) {
      console.error("Audio Processing Pipeline Exception:", error.message);
      alert("Could not play the audio response.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <button
      onClick={handlePlayAudio}
      disabled={isLoading}
      className={`mt-2 flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
        isPlaying 
          ? 'bg-teal-100 text-teal-800 border border-teal-200' 
          : 'bg-white text-slate-600 border border-slate-200 hover:bg-slate-50'
      }`}
    >
      {isLoading ? <Loader2 size={16} className="animate-spin" /> : 
       isPlaying ? <Square size={16} /> : <Volume2 size={16} />}
      {isPlaying ? 'Stop' : 'Listen'}
    </button>
  );
}