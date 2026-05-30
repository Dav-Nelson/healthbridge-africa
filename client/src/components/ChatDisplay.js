import React, { useEffect, useRef } from 'react';
import { Loader2 } from 'lucide-react';
import ResponsePlayer from './ResponsePlayer';

export default function ChatDisplay({ messages, isLoading, language }) {
  const messagesEndRef = useRef(null);

  // Auto-scroll to the latest message
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  return (
    <div className="flex-grow bg-white rounded-t-2xl shadow-sm border border-slate-200 p-6 overflow-y-auto mb-4 flex flex-col gap-4">
      {messages.length === 0 ? (
        <div className="flex-grow flex flex-col items-center justify-center text-slate-400 text-center">
          <p className="text-lg font-medium text-teal-800 mb-2">How can we help you today?</p>
          <p className="text-sm">Type a health question or use the microphone to speak.</p>
        </div>
      ) : (
        messages.map((msg, index) => (
          <div key={index} className={`max-w-[85%] rounded-2xl px-5 py-4 ${
            msg.sender === 'user' 
              ? 'bg-teal-600 text-white self-end rounded-br-sm' 
              : 'bg-slate-50 text-slate-800 self-start rounded-bl-sm border border-slate-200'
          }`}>
            <p className="leading-relaxed">{msg.text}</p>
            
            {/* Render the Play Button only for AI responses */}
            {msg.sender === 'bot' && (
              <ResponsePlayer text={msg.text} language={language} />
            )}
          </div>
        ))
      )}
      
      {isLoading && (
        <div className="bg-slate-50 text-slate-500 self-start rounded-2xl rounded-bl-sm border border-slate-200 px-5 py-4 flex items-center gap-2">
          <Loader2 size={18} className="animate-spin text-teal-600" />
          <span className="text-sm">Processing...</span>
        </div>
      )}
      <div ref={messagesEndRef} />
    </div>
  );
}