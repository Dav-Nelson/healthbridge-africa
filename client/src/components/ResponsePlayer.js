import React, { useState } from 'react';
import { Volume2, Square, Loader2 } from 'lucide-react';

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
      const response = await fetch('https://healthbridge-africa.onrender.com/api/voice/speak', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text, language: language ? language.toLowerCase() : 'en' }),
      });

      if (!response.ok) throw new Error('Failed to fetch audio from server');

      const contentType = response.headers.get('content-type') || '';
      let audioUrl = '';

      // Universal Parsing Layer
      if (contentType.includes('application/json')) {
        // Option A: Backend responded with JSON wrapped Base64
        const data = await response.json();
        const rawBase64 = data.audio || data.audioContent || data.data;
        if (!rawBase64) throw new Error('JSON structure did not contain audio data');
        audioUrl = `data:audio/mp3;base64,${rawBase64}`;
      } else {
        // Option B: Backend responded with a raw direct binary stream/blob
        const audioBlob = await response.blob();
        if (audioBlob.size === 0) throw new Error('Received an empty audio blob file');
        audioUrl = URL.createObjectURL(audioBlob);
      }

      // Initialize HTML5 Audio playback context securely
      const audio = new Audio();
      audio.src = audioUrl;
      
      audio.onended = () => {
        setIsPlaying(false);
        if (!contentType.includes('application/json')) {
          URL.revokeObjectURL(audioUrl); // Clean up memory if blob was used
        }
      };

      audio.onerror = (e) => {
        console.error("Browser media playback engine failed to decode audio source:", e);
        setIsPlaying(false);
        alert("Audio formatting issue. Please try again or check server codecs.");
      };

      setAudioElement(audio);
      setIsPlaying(true);
      
      const playPromise = audio.play();
      if (playPromise !== undefined) {
        playPromise.catch(err => {
          console.error("Playback interrupted or blocked by browser autoplay policy:", err);
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