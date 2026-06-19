import React, { useEffect, useState } from 'react';
import { History, Loader2 } from 'lucide-react';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

const getOrCreateSessionId = () => {
  let sessionId = localStorage.getItem('chat_session_id');
  if (!sessionId) {
    sessionId = crypto.randomUUID();
    localStorage.setItem('chat_session_id', sessionId);
  }
  return sessionId;
};

export default function HistoryPanel() {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const sessionId = getOrCreateSessionId();
        const response = await fetch(`${API_BASE_URL}/api/voice/history/${sessionId}`);
        if (!response.ok) throw new Error('Failed to load history');
        const data = await response.json();
        setMessages(data.messages || []);
      } catch (err) {
        console.error('History load error:', err);
        setError('Could not load your consultation history right now.');
      } finally {
        setIsLoading(false);
      }
    };

    fetchHistory();
  }, []);

  if (isLoading) {
    return (
      <div className="flex-grow bg-white rounded-2xl shadow-sm border border-slate-200 p-6 flex flex-col items-center justify-center text-slate-400">
        <Loader2 size={32} className="animate-spin text-teal-500 mb-3" />
        <p className="text-sm">Loading your history...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex-grow bg-white rounded-2xl shadow-sm border border-slate-200 p-6 flex flex-col items-center justify-center text-slate-400">
        <p className="text-sm text-red-500">{error}</p>
      </div>
    );
  }

  if (messages.length === 0) {
    return (
      <div className="flex-grow bg-white rounded-2xl shadow-sm border border-slate-200 p-6 flex flex-col items-center justify-center text-slate-400">
        <History size={48} className="text-slate-300 mb-3" />
        <p className="text-base font-medium text-slate-700">No Consultation History Yet</p>
        <p className="text-xs text-center mt-1">Your localized medical discussions will appear recorded here securely.</p>
      </div>
    );
  }

  return (
    <div className="flex-grow bg-white rounded-2xl shadow-sm border border-slate-200 p-4 md:p-6 overflow-y-auto flex flex-col gap-3">
      {messages.map((msg, index) => (
        <div
          key={index}
          className={`max-w-[88%] rounded-xl px-4 py-2.5 text-sm ${
            msg.role === 'user'
              ? 'bg-teal-50 text-teal-900 self-end'
              : 'bg-slate-50 text-slate-800 self-start border border-slate-200'
          }`}
        >
          <p className="whitespace-pre-line">{msg.content}</p>
          <p className="text-[10px] text-slate-400 mt-1">
            {new Date(msg.created_at).toLocaleString()}
          </p>
        </div>
      ))}
    </div>
  );
}