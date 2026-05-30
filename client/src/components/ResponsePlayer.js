import React, { useState } from 'react';
import { Volume2, Square, Loader2 } from 'lucide-react';

export default function ResponsePlayer({ text, language }) {
  const [isPlaying, setIsPlaying] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [audioElement, setAudioElement] = useState(null);

  const handlePlayAudio = async () => {
    // If already playing, stop it
    if (isPlaying && audioElement) {
      audioElement.pause();
      setIsPlaying(false);
      return;
    }

    setIsLoading(true);
    try {
      const response = await fetch('https://healthbridge-africa.onrender.com/api/voice/speak', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text, language: language.toLowerCase() }),
      });

      if (!response.ok) throw new Error('Failed to fetch audio');

      const blob = await response.blob();
      const audioUrl = URL.createObjectURL(blob);
      const audio = new Audio(audioUrl);
      
      audio.onended = () => setIsPlaying(false);
      
      setAudioElement(audio);
      audio.play();
      setIsPlaying(true);
    } catch (error) {
      console.error("Audio Playback Error:", error);
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