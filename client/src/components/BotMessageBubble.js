import React, { useState } from 'react';
import { ThumbsUp, ThumbsDown, Copy, Check, Share2, ShieldCheck } from 'lucide-react';
import ResponsePlayer from './ResponsePlayer';

export default function BotMessageBubble({ text, language }) {
  const [feedback, setFeedback] = useState(null);
  const [isCopied, setIsCopied] = useState(false);

  const handleFeedback = (type) => {
    setFeedback(type);
  };

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(text);
      setIsCopied(true);
      setTimeout(() => setIsCopied(false), 2000);
    } catch (err) {
      console.error("Failed to copy text:", err);
    }
  };

  const handleShare = async () => {
    if (navigator.share) {
      try {
        await navigator.share({
          title: 'HealthBridge Africa',
          text: text,
        });
      } catch (err) {
        console.error("Failed to share:", err);
      }
    } else {
      await handleCopy();
      alert("Response copied to clipboard to share!");
    }
  };

  return (
    <div className="max-w-[92%] md:max-w-[85%] rounded-2xl px-4 py-3 md:px-5 md:py-4 bg-slate-50 text-slate-800 self-start rounded-bl-sm border border-slate-200">
      <div className="flex items-center gap-1.5 mb-2 text-teal-700">
        <ShieldCheck size={14} />
        <span className="text-[10px] font-semibold uppercase tracking-wider">HealthBridge</span>
      </div>

      <p className="leading-relaxed text-sm md:text-base whitespace-pre-line">{text}</p>

      <div className="mt-3 flex items-center justify-between border-t border-slate-200/60 pt-3">
        <ResponsePlayer text={text} language={language} />

        <div className="flex items-center gap-1 md:gap-2">
          <button
            onClick={handleCopy}
            title="Copy response"
            className="p-1.5 text-slate-400 hover:text-teal-600 hover:bg-slate-100 rounded-md transition-colors"
          >
            {isCopied ? <Check size={18} className="text-teal-600" /> : <Copy size={18} />}
          </button>

          <button
            onClick={handleShare}
            title="Share response"
            className="p-1.5 text-slate-400 hover:text-teal-600 hover:bg-slate-100 rounded-md transition-colors"
          >
            <Share2 size={18} />
          </button>

          <div className="w-px h-4 bg-slate-200 mx-1"></div>

          <button
            onClick={() => handleFeedback('up')}
            className={`p-1.5 rounded-md transition-colors ${
              feedback === 'up' ? 'text-teal-600 bg-teal-100' : 'text-slate-400 hover:text-teal-600 hover:bg-slate-100'
            }`}
          >
            <ThumbsUp size={18} className={feedback === 'up' ? 'fill-current' : ''} />
          </button>

          <button
            onClick={() => handleFeedback('down')}
            className={`p-1.5 rounded-md transition-colors ${
              feedback === 'down' ? 'text-red-500 bg-red-100' : 'text-slate-400 hover:text-red-500 hover:bg-slate-100'
            }`}
          >
            <ThumbsDown size={18} className={feedback === 'down' ? 'fill-current' : ''} />
          </button>
        </div>
      </div>
    </div>
  );
}