import React, { useEffect, useRef } from 'react';
import { Loader2 } from 'lucide-react';
import BotMessageBubble from './BotMessageBubble';

export default function ChatDisplay({ messages, isLoading, language }) {
  const messagesEndRef = useRef(null);

  // 1. Dictionary for dynamic chat area translations
  const translations = {
    English: {
      greeting: "How can we help you today?",
      instruction: "Type a health question or use the microphone to speak.",
      thinking: "HealthBridge is thinking..."
    },
    Pidgin: {
      greeting: "How we fit help you today?",
      instruction: "Type your health question or use mic talk.",
      thinking: "HealthBridge dey think..."
    },
    Swahili: {
      greeting: "Tunawezaje kukusaidia leo?",
      instruction: "Andika swali la afya au tumia maikrofoni kuzungumza.",
      thinking: "HealthBridge inafikiri..."
    },
    Oromo: {
      greeting: "Har'a akkamitti isin gargaaruu dandeenya?",
      instruction: "Gaaffii fayyaa barreessi ykn maayikiroofoonii fayyadami.",
      thinking: "HealthBridge yaadaa jira..."
    },
    Twi: {
      greeting: "Yɛbɛyɛ dɛn aboa wo nnɛ?",
      instruction: "Kyerɛw wo apɔwmuden asɛm anaa fa kasa afiri no kasa.",
      thinking: "HealthBridge redwene..."
    }
  };

  // Select the current language texts (defaults to English)
  const t = translations[language] || translations.English;

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  return (
    <div className="flex-grow bg-white rounded-t-2xl shadow-sm border border-slate-200 p-4 md:p-6 overflow-y-auto mb-4 flex flex-col gap-4">
      {messages.length === 0 ? (
        <div className="flex-grow flex flex-col items-center justify-center text-slate-400 text-center">
          {/* Inject dynamic greeting and instruction */}
          <p className="text-lg font-medium text-teal-800 mb-2">{t.greeting}</p>
          <p className="text-sm">{t.instruction}</p>
        </div>
      ) : (
        messages.map((msg, index) => (
          msg.sender === 'user' ? (
            <div key={index} className="max-w-[92%] md:max-w-[85%] rounded-2xl px-4 py-3 md:px-5 md:py-4 bg-teal-600 text-white self-end rounded-br-sm">
              <p className="leading-relaxed text-sm md:text-base">{msg.text}</p>
            </div>
          ) : (
            <BotMessageBubble key={index} text={msg.text} language={language} />
          )
        ))
      )}
      
      {isLoading && (
        <div className="bg-slate-50 text-slate-500 self-start rounded-2xl rounded-bl-sm border border-slate-200 px-5 py-4 flex items-center gap-3">
          <Loader2 size={18} className="animate-spin text-teal-600" />
          {/* Inject dynamic loading text */}
          <span className="text-sm font-medium">{t.thinking}</span>
        </div>
      )}
      <div ref={messagesEndRef} />
    </div>
  );
}