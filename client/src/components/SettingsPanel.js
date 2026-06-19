import React, { useState } from 'react';
import { Settings, Volume2, Globe, Trash2, ShieldCheck } from 'lucide-react';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';
const SUPPORTED_LANGUAGES = ['English', 'Pidgin', 'Oromo', 'Twi', 'Swahili', 'Amharic'];

export default function SettingsPanel({ language, setLanguage }) {
  const [autoPlay, setAutoPlay] = useState(() => {
    return localStorage.getItem('hb_autoplay') === 'true';
  });
  const [cleared, setCleared] = useState(false);
  const [isClearing, setIsClearing] = useState(false);

  const handleAutoPlayToggle = () => {
    const next = !autoPlay;
    setAutoPlay(next);
    localStorage.setItem('hb_autoplay', String(next));
  };

  const handleClearHistory = async () => {
    const sessionId = localStorage.getItem('chat_session_id');
    setIsClearing(true);

    if (sessionId) {
      try {
        await fetch(`${API_BASE_URL}/api/voice/history/${sessionId}`, {
          method: 'DELETE'
        });
      } catch (err) {
        console.error('Failed to delete server history:', err);
        // Still clear localStorage even if server delete fails
      }
    }

    localStorage.removeItem('chat_session_id');
    setIsClearing(false);
    setCleared(true);
    setTimeout(() => setCleared(false), 3000);
  };

  return (
    <div className="flex-grow bg-white rounded-2xl shadow-sm border border-slate-200 overflow-y-auto">

      <div className="p-5 border-b border-slate-100">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-slate-100 flex items-center justify-center flex-shrink-0">
            <Settings size={18} className="text-slate-600" />
          </div>
          <div>
            <h2 className="text-base font-bold text-slate-800">System Preferences</h2>
            <p className="text-xs text-slate-400">Personalise your HealthBridge Africa experience</p>
          </div>
        </div>
      </div>

      <div className="p-5 flex flex-col gap-6">

        {/* Language preference */}
        <div className="flex flex-col gap-2">
          <div className="flex items-center gap-2 mb-1">
            <Globe size={15} className="text-teal-600" />
            <span className="text-sm font-semibold text-slate-700">Preferred Language</span>
          </div>
          <p className="text-xs text-slate-400 mb-2">
            Sets the default language for your consultation. You can also change this anytime from the header.
          </p>
          <select
            value={language}
            onChange={(e) => setLanguage(e.target.value)}
            className="w-full p-2.5 rounded-xl border border-slate-200 text-sm text-slate-700 bg-slate-50 focus:ring-2 focus:ring-teal-500 outline-none"
          >
            {SUPPORTED_LANGUAGES.map((lang) => (
              <option key={lang} value={lang}>{lang}</option>
            ))}
          </select>
        </div>

        {/* Audio auto-play */}
        <div className="flex items-center justify-between gap-4 p-4 bg-slate-50 rounded-xl border border-slate-200">
          <div className="flex items-start gap-3 min-w-0">
            <Volume2 size={18} className="text-slate-500 flex-shrink-0 mt-0.5" />
            <div className="min-w-0">
              <p className="text-sm font-semibold text-slate-700">Auto-play Audio</p>
              <p className="text-xs text-slate-400 leading-snug">Automatically play voice responses after each reply</p>
            </div>
          </div>
          <button
            onClick={handleAutoPlayToggle}
            aria-label="Toggle auto-play audio"
            className={`relative w-11 h-6 rounded-full transition-colors flex-shrink-0 ${
              autoPlay ? 'bg-teal-500' : 'bg-slate-300'
            }`}
          >
            <span className={`absolute top-1 left-1 w-4 h-4 bg-white rounded-full shadow transition-transform ${
              autoPlay ? 'translate-x-5' : 'translate-x-0'
            }`} />
          </button>
        </div>

        {/* Clear history */}
        <div className="flex flex-col gap-2">
          <div className="flex items-center gap-2 mb-1">
            <Trash2 size={15} className="text-red-500" />
            <span className="text-sm font-semibold text-slate-700">Clear Consultation History</span>
          </div>
          <p className="text-xs text-slate-400 mb-2">
            Permanently removes your session and all conversation data from both this device and our servers. Your next conversation will start completely fresh.
          </p>
          <button
            onClick={handleClearHistory}
            disabled={isClearing}
            className="w-full p-2.5 rounded-xl border border-red-200 text-sm font-medium text-red-600 bg-red-50 hover:bg-red-100 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isClearing
              ? 'Clearing...'
              : cleared
              ? '✓ Session cleared — refresh to start fresh'
              : 'Clear my session'}
          </button>
        </div>

        {/* Privacy note */}
        <div className="flex items-start gap-3 p-4 bg-teal-50 rounded-xl border border-teal-100">
          <ShieldCheck size={18} className="text-teal-600 flex-shrink-0 mt-0.5" />
          <p className="text-xs text-slate-600 leading-relaxed">
            HealthBridge Africa does not collect your name, email, or any personal identity. Your conversations are stored securely and linked only to your device session. Clearing your session permanently deletes all conversation data from our servers.
          </p>
        </div>

      </div>
    </div>
  );
}