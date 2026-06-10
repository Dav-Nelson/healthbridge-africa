import React, { useState, useRef } from 'react';
import { Mic, Square, Send } from 'lucide-react';
import Header from './components/Header';
import Footer from './components/Footer';
import ChatDisplay from './components/ChatDisplay';
import OnboardingModal from './OnboardingModal'; // Added Import

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

// ISO Language mapping layer supporting Amharic
const LANGUAGE_ISO_MAP = {
  'english': 'en',
  'pidgin': 'pcm',
  'swahili': 'sw',
  'oromo': 'om',
  'twi': 'tw',
  'amharic': 'am'
};

export default function App() {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [language, setLanguage] = useState('English'); 
  const [showOnboarding, setShowOnboarding] = useState(true); // Added Modal State

  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

  const getCleanLanguageCode = () => {
    const currentLang = language.toLowerCase();
    return LANGUAGE_ISO_MAP[currentLang] || currentLang;
  };

  const handleSendMessage = async (textToProcess) => {
    if (!textToProcess.trim()) return;

    setMessages(prev => [...prev, { sender: 'user', text: textToProcess }]);
    setInputValue('');
    setIsLoading(true);

    try {
      const targetCode = getCleanLanguageCode();

      const response = await fetch(`${API_BASE_URL}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          query: textToProcess, 
          language: targetCode 
        }),
      });

      if (!response.ok) throw new Error('API response failed');
      const data = await response.json();
      
      // Kept consistent with your data fields (adding support for optional clinical images)
      setMessages(prev => [...prev, { 
        sender: 'bot', 
        text: data.response,
        imageUrl: data.imageUrl || null 
      }]);
    } catch (error) {
      console.error("Chat Error:", error);
      setMessages(prev => [...prev, { sender: 'bot', text: "Sorry, I am having trouble connecting to the server right now." }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleTextSubmit = (e) => {
    e.preventDefault();
    handleSendMessage(inputValue);
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) audioChunksRef.current.push(event.data);
      };

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        stream.getTracks().forEach(track => track.stop());
        await processVoiceAudio(audioBlob);
      };

      mediaRecorder.start();
      setIsRecording(true);
    } catch (error) {
      console.error("Microphone Error:", error);
      alert("Unable to access the microphone. Please allow permissions.");
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  const processVoiceAudio = async (audioBlob) => {
    setIsLoading(true);
    const formData = new FormData();
    formData.append('audio', audioBlob, 'recording.webm');

    try {
      const response = await fetch(`${API_BASE_URL}/api/voice/transcribe`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) throw new Error('Transcription failed');
      
      const data = await response.json();
      const transcribedText = data.text || data.transcription;

      if (transcribedText) {
         await handleSendMessage(transcribedText);
      }
    } catch (error) {
      console.error("Transcription Error:", error);
      setMessages(prev => [...prev, { sender: 'bot', text: "Sorry, I couldn't process your voice message." }]);
    } finally {
      setIsLoading(false);
    }
  };

  // --- NEW TRANSLATION LOGIC WITH AMHARIC ---
  const inputTranslations = {
    English: { placeholder: "Type your health question...", recording: "Listening..." },
    Pidgin: { placeholder: "Type your health question...", recording: "I dey listen..." },
    Swahili: { placeholder: "Andika swali lako la afya...", recording: "Inasikiliza..." },
    Oromo: { placeholder: "Gaaffii fayyaa kee barreessi...", recording: "Dhaggeeffachaa jira..." },
    Twi: { placeholder: "Kyerɛw wo apɔwmuden asɛm...", recording: "Mretie..." },
    Amharic: { placeholder: "የጤና ጥያቄዎን እዚህ ይጻፉ...", recording: "እያዳመጥኩ ነው..." }
  };

  const tInput = inputTranslations[language] || inputTranslations.English;

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col font-sans antialiased">
      {/* 1. Onboarding Modal Mount */}
      {showOnboarding && (
        <OnboardingModal onComplete={() => setShowOnboarding(false)} />
      )}

      <Header language={language} setLanguage={setLanguage} />

      <main className="flex-grow flex flex-col max-w-4xl mx-auto w-full p-4 h-[calc(100vh-140px)]">
        
        {/* 2. Chat Display Mount (Maps to your message properties) */}
        <ChatDisplay 
          messages={messages} 
          isLoading={isLoading} 
          language={getCleanLanguageCode()} 
        />

        <div className="bg-white rounded-b-2xl shadow-sm border border-slate-200 p-4">
          <form onSubmit={handleTextSubmit} className="flex items-center gap-3">
            <button
              type="button"
              onClick={isRecording ? stopRecording : startRecording}
              className={`p-4 rounded-full flex-shrink-0 transition-all ${
                isRecording 
                  ? 'bg-red-500 hover:bg-red-600 text-white animate-pulse shadow-lg shadow-red-200' 
                  : 'bg-teal-100 hover:bg-teal-200 text-teal-700'
              }`}
            >
              {isRecording ? <Square size={24} fill="currentColor"/> : <Mic size={24} />}
            </button>

            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder={isRecording ? tInput.recording : tInput.placeholder}
              disabled={isRecording || isLoading}
              className="flex-grow p-4 bg-slate-50 border border-slate-300 rounded-xl focus:ring-2 focus:ring-teal-500 outline-none transition-all disabled:opacity-50"
            />

            <button
              type="submit"
              disabled={!inputValue.trim() || isLoading || isRecording}
              className="p-4 bg-teal-600 hover:bg-teal-700 text-white rounded-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed flex-shrink-0"
            >
              <Send size={24} />
            </button>
          </form>
        </div>
      </main>

      <Footer language={language} />
    </div>
  );
}