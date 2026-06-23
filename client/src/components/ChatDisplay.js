import React, { useEffect, useRef } from 'react';
import BotMessageBubble from './BotMessageBubble';

export default function ChatDisplay({ messages, isTyping, isLoading, language, secureText }) {
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isTyping, isLoading]);

  return (
    <div className="flex flex-col space-y-4 max-w-4xl mx-auto pb-2">
      
      {/* The translated Secure Consultation text */}
      <div className="text-health-textSecondary text-center text-[10px] sm:text-xs my-2 uppercase tracking-widest opacity-60">
        {secureText || "Secure Clinical Consultation"}
      </div>

      {messages.map((msg) => (
        <div key={msg.id || Math.random()} className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
          {msg.sender === 'user' ? (
            // User Message Bubble
            <div className="max-w-[85%] p-3 rounded-[18px] text-[15px] leading-relaxed shadow-sm bg-health-userBubble text-health-textPrimary rounded-tr-[4px]">
              {msg.text.split('\n').map((line, i) => (
                <span key={i}>{line}<br/></span>
              ))}
            </div>
          ) : (
            // RESTORED: Bot Message Bubble with all buttons, listen feature, and disease images!
            <BotMessageBubble text={msg.text} language={language} />
          )}
        </div>
      ))}
      
      {/* Typing Indicator */}
      {(isTyping || isLoading) && (
        <div className="flex justify-start">
           <div className="bg-health-aiBubble p-4 rounded-[18px] rounded-tl-[4px] flex gap-1 items-center h-[42px] shadow-sm">
             <div className="w-1.5 h-1.5 bg-health-accent rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
             <div className="w-1.5 h-1.5 bg-health-accent rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
             <div className="w-1.5 h-1.5 bg-health-accent rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
           </div>
        </div>
      )}
      <div ref={messagesEndRef} />
    </div>
  );
}