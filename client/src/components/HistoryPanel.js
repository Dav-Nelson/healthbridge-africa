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
      <div className="flex-grow bg-health-surface rounded-2xl shadow-sm border border-health-border p-6 flex flex-col items-center justify-center text-health-textSecondary">
        <Loader2 size={32} className="animate-spin text-health-accent mb-3" />
        <p className="text-sm">Loading your history...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex-grow bg-health-surface rounded-2xl shadow-sm border border-health-border p-6 flex flex-col items-center justify-center text-health-textSecondary">
        <p className="text-sm text-red-500">{error}</p>
      </div>
    );
  }

  if (messages.length === 0) {
    return (
      <div className="flex-grow bg-health-surface rounded-2xl shadow-sm border border-health-border p-6 flex flex-col items-center justify-center text-health-textSecondary">
        <History size={48} className="text-health-border mb-4 opacity-50" />
        <p className="text-lg font-brand font-bold text-health-textPrimary">No Consultation History</p>
        <p className="text-xs text-center mt-2 max-w-xs">Your localized medical discussions will appear recorded here securely.</p>
      </div>
    );
  }

  return (
    <div className="flex-grow bg-health-surface rounded-2xl shadow-sm border border-health-border p-4 md:p-6 overflow-y-auto flex flex-col gap-4">
      <div className="text-health-textSecondary text-center text-[10px] uppercase tracking-widest opacity-60 mb-2">
        Previous Consultations
      </div>
      {messages.map((msg, index) => (
        <div
          key={index}
          className={`max-w-[88%] rounded-[18px] px-4 py-3 text-[15px] shadow-sm ${
            msg.role === 'user'
              ? 'bg-health-userBubble text-health-textPrimary self-end rounded-tr-[4px]'
              : 'bg-health-aiBubble text-health-textPrimary self-start rounded-tl-[4px]'
          }`}
        >
          <p className="whitespace-pre-line leading-relaxed">{msg.content}</p>
          <p className="text-[10px] text-health-textSecondary opacity-70 mt-2 text-right">
            {new Date(msg.created_at).toLocaleString()}
          </p>
        </div>
      ))}
    </div>
  );
}