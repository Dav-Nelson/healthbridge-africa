import React, { useEffect, useRef } from 'react';
import BotMessageBubble from './BotMessageBubble';

export default function ChatDisplay({ messages, isLoading, language }) {
  const messagesEndRef = useRef(null);

  const translations = {
    en: {
      greeting: "How can we help you today?",
      instruction: "Type a health question or use the microphone to speak.",
      thinking: "Generating response..."
    },
    pcm: {
      greeting: "How we fit help you today?",
      instruction: "Type your health question or use mic talk.",
      thinking: "Response dey load..."
    },
    sw: {
      greeting: "Tunawezaje kukusaidia leo?",
      instruction: "Andika swali la afya au tumia maikrofoni kuzungumza.",
      thinking: "Jibu linaandaliwa..."
    },
    om: {
      greeting: "Har'a akkamitti isin gargaaruu dandeenya?",
      instruction: "Gaaffii fayyaa barreessi ykn maayikiroofoonii fayyadami.",
      thinking: "Deebiin qophaa'aa jira..."
    },
    tw: {
      greeting: "Yɛbɛyɛ dɛn aboa wo nnɛ?",
      instruction: "Kyerɛw wo apɔwmuden asɛm anaa fa kasa afiri no kasa.",
      thinking: "Yɛreyɛ mmuae no..."
    },
    am: {
      greeting: "የጤና ጥያቄዎን እዚህ ይጻፉ...",
      instruction: "የጤና ጥያቄዎን እዚህ ይጻፉ ወይም በመጥቀስ",
      thinking: "በማመንጨት ላይ..."
    }
  };

  const t = translations[language] || translations.en;

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
            <div key={index} className="max-w-[88%] md:max-w-[75%] rounded-2xl px-4 py-3 bg-teal-600 text-white self-end rounded-br-none shadow-sm shadow-teal-100">
              <p className="leading-relaxed text-sm md:text-base whitespace-pre-line">{msg.text}</p>
            </div>
          ) : (
            <BotMessageBubble key={index} text={msg.text} language={msg.language || language} />
          )
        ))
      )}

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