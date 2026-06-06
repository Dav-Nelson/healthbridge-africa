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
        body: JSON.stringify({ text, language: language ? language.toLowerCase() : 'en' }),
      });

      if (!response.ok) throw new Error('Failed to fetch audio stream');

      // Check content type to see if backend returned JSON or binary data
      const contentType = response.headers.get('content-type');
      let audioUrl = '';

      if (contentType && contentType.includes('application/json')) {
        const data = await response.json();
        // If data contains a base64 audio payload string
        if (data.audio || data.audioContent) {
          const rawBase64 = data.audio || data.audioContent;
          audioUrl = `data:audio/mp3;base64,${rawBase64}`;
        } else {
          throw new Error('Audio payload missing inside JSON response object');
        }
      } else {
        // Fallback fallback: handle it as a direct raw binary audio blob stream
        const blob = await response.blob();
        audioUrl = URL.createObjectURL(blob);
      }

      const audio = new Audio(audioUrl);
      
      audio.onended = () => setIsPlaying(false);
      audio.onerror = (e) => {
        console.error("HTML Audio element decoding failed:", e);
        setIsPlaying(false);
      };
      
      setAudioElement(audio);
      audio.play();
      setIsPlaying(true);
    } catch (error) {
      console.error("Audio Playback System Error:", error.message);
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