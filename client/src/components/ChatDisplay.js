import React, { useEffect, useRef } from 'react';
import BotMessageBubble from './BotMessageBubble';
import { ThumbsUp, ThumbsDown } from 'lucide-react';

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
      instruction: "የጤና ጥያቄዎን እዚህ ይጻፉ ወይም ማይክሮፎኑን በመጠቀም ይናገሩ።",
      thinking: "ምላሽ በመዘጋጀት ላይ ነው..."
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
            <div key={index} className="max-w-[92%] md:max-w-[80%] rounded-2xl bg-slate-50 border border-slate-200/80 self-start rounded-bl-none shadow-md overflow-hidden flex flex-col h-auto">
              
              {/* Medical Card Header Accent */}
              <div className="bg-gradient-to-r from-teal-700 to-teal-600 px-4 py-2 flex items-center justify-between border-b border-teal-800/10">
                <span className="text-[11px] font-bold uppercase tracking-wider text-teal-50/90 flex items-center gap-1.5">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
                  Clinical AI Insights
                </span>
                <span className="text-[10px] text-teal-100/75 italic">HealthBridge Verified</span>
              </div>

              {/* Main Card Body */}
              <div className="p-4 md:p-5 flex flex-col gap-4 bg-white">
                <div className="leading-relaxed text-slate-800 text-sm md:text-base font-normal">
                  <BotMessageBubble text={msg.text} language={language} />
                </div>

                {/* Inline Disease Image Manifestation Box */}
                {msg.imageUrl && (
                  <div className="bg-slate-50 rounded-xl p-3 border border-slate-100 shadow-sm">
                    <p className="text-[11px] font-bold text-slate-500 uppercase tracking-wider mb-2 flex items-center gap-1">
                      📸 Clinical Manifestation Reference (Darker Skin Types)
                    </p>
                    <img 
                      src={msg.imageUrl} 
                      alt="Clinical reference condition manifestation" 
                      className="rounded-lg w-full h-auto object-cover max-h-64 shadow-inner border border-slate-200/60"
                    />
                    <span className="text-[10px] text-slate-400 mt-2 block italic text-right">
                      Source: Mind the Gap / Black Derm Directory
                    </span>
                  </div>
                )}

                {/* Accent & Accuracy Feedback Footer */}
                <div className="flex items-center justify-between border-t border-slate-100 pt-3 mt-1">
                  <span className="text-[11px] text-slate-400 font-medium">Rate translation & accent accuracy:</span>
                  <div className="flex items-center gap-3">
                    <button className="text-slate-400 hover:text-teal-600 hover:bg-slate-50 p-1.5 rounded-lg transition-all border border-transparent hover:border-slate-200" aria-label="Helpful / Accurate">
                      <ThumbsUp size={15} />
                    </button>
                    <button className="text-slate-400 hover:text-red-500 hover:bg-slate-50 p-1.5 rounded-lg transition-all border border-transparent hover:border-slate-200" aria-label="Not helpful / Inaccurate">
                      <ThumbsDown size={15} />
                    </button>
                  </div>
                </div>
              </div>
            </div>
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