import React, { useEffect, useRef } from 'react';
import posthog from 'posthog-js';
import BotMessageBubble from './BotMessageBubble';

export default function ChatDisplay({ messages, isLoading, language }) {
  const messagesEndRef = useRef(null);

  // 1. Dictionary updated to support lowercased ISO language codes passed from App.js
  const translations = {
    en: {
      greeting: "How can we help you today?",
      instruction: "Type a health question or use the microphone to speak.",
      thinking: "Processing audio..."
    },
    pcm: {
      greeting: "How we fit help you today?",
      instruction: "Type your health question or use mic talk.",
      thinking: "Processing audio..."
    },
    sw: {
      greeting: "Tunawezaje kukusaidia leo?",
      instruction: "Andika swali la afya au tumia maikrofoni kuzungumza.",
      thinking: "Processing audio..."
    },
    om: {
      greeting: "Har'a akkamitti isin gargaaruu dandeenya?",
      instruction: "Gaaffii fayyaa barreessi ykn maayikiroofoonii fayyadami.",
      thinking: "Processing audio..."
    },
    tw: {
      greeting: "Yɛbɛyɛ dɛn aboa wo nnɛ?",
      instruction: "Kyerɛw wo apɔwmuden asɛm anaa fa kasa afiri no kasa.",
      thinking: "Processing audio..."
    },
    am: {
      greeting: "የጤና ጥያቄዎን እዚህ ይጻፉ...",
      instruction: "የጤና ጥያቄዎን እዚህ ይጻፉ ወይም ማይክሮፎኑን በመጠቀም ይናገሩ።",
      thinking: "እያደመጥን ነው..."
    }
  };

  const t = translations[language] || translations.en;

  const handleFeedback = (rating, index) => {
    posthog.capture('accent_rated', { rating, message_id: index });
  };

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  return (
    <div className="flex-grow bg-white rounded-t-2xl shadow-sm border border-slate-200 p-4 md:p-6 overflow-y-auto mb-4 flex flex-col gap-4 h-full">
      {messages.length === 0 ? (
        <div className="flex-grow flex flex-col items-center justify-center text-slate-400 text-center">
          <p className="text-lg font-medium text-teal-800 mb-2">{t.greeting}</p>
          <p className="text-sm">{t.instruction}</p>
        </div>
      ) : (
        messages.map((msg, index) => (
          msg.sender === 'user' ? (
            /* User Message Bubble */
            <div key={index} className="max-w-[88%] md:max-w-[75%] rounded-2xl px-4 py-3 md:px-5 md:py-4 bg-teal-600 text-white self-end rounded-br-none shadow-sm shadow-teal-100">
              <p className="leading-relaxed text-sm md:text-base whitespace-pre-line">{msg.text}</p>
            </div>
          ) : (
            /* Healthcare-focused Clinical Bot Card Layout */
            <div key={index} className="max-w-[88%] md:max-w-[75%] rounded-2xl p-5 bg-white border border-slate-200 self-start rounded-bl-none shadow-sm flex flex-col gap-4">
              
              <div className="leading-relaxed text-slate-800 text-sm md:text-base">
                <BotMessageBubble text={msg.text} language={language} />
              </div>

              {/* Clinical Imagery (Renders dynamically if payload includes imageUrl) */}
              {msg.imageUrl && (
                <div className="mt-2 bg-slate-50 rounded-xl p-3 border border-slate-100">
                  <p className="text-[11px] font-bold text-slate-400 uppercase tracking-wider mb-2">
                    Clinical Manifestation Reference (Darker Skin Types)
                  </p>
                  <img 
                    src={msg.imageUrl} 
                    alt="Clinical reference condition manifestation" 
                    className="rounded-lg w-full h-auto object-cover max-h-64 shadow-inner"
                  />
                  <span className="text-[10px] text-slate-400 mt-2 block italic text-right">
                    Source: Mind the Gap / Black Derm Directory
                  </span>
                </div>
              )}

              {/* Accent Evaluation Interaction Layout */}
              <div className="pt-3 border-t border-slate-100 flex items-center justify-between">
                <span className="text-xs text-slate-400 font-medium">Rate accent accuracy:</span>
                <div className="flex space-x-4">
                  <button onClick={() => handleFeedback('good', index)} className="text-slate-400 hover:text-green-500 scale-110 active:scale-95 transition">
                    👍
                  </button>
                  <button onClick={() => handleFeedback('bad', index)} className="text-slate-400 hover:text-red-500 scale-110 active:scale-95 transition">
                    👎
                  </button>
                </div>
              </div>

            </div>
          )
        ))
      )}
      
      {/* Dynamic Animated Waveform Module Replacing Simple Spinner */}
      {isLoading && (
        <div className="bg-white border border-slate-200 shadow-sm rounded-2xl rounded-bl-none px-5 py-4 flex items-center space-x-1.5 h-14 self-start">
          <div className="w-1 bg-teal-500 h-5 rounded-full animate-wave" style={{ animationDelay: '0.0s' }}></div>
          <div className="w-1 bg-teal-500 h-7 rounded-full animate-wave" style={{ animationDelay: '0.15s' }}></div>
          <div className="w-1 bg-teal-500 h-4 rounded-full animate-wave" style={{ animationDelay: '0.3s' }}></div>
          <div className="w-1 bg-teal-500 h-6 rounded-full animate-wave" style={{ animationDelay: '0.45s' }}></div>
          <div className="w-1 bg-teal-500 h-3 rounded-full animate-wave" style={{ animationDelay: '0.6s' }}></div>
          <span className="text-sm text-slate-400 ml-3 font-medium tracking-wide animate-pulse">{t.thinking}</span>
        </div>
      )}
      
      <div ref={messagesEndRef} />
    </div>
  );
}