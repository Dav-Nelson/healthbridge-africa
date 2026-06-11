import React, { useState } from 'react';
import { ThumbsUp, ThumbsDown, Copy, Check, Share2 } from 'lucide-react';
import ResponsePlayer from './ResponsePlayer';

export default function BotMessageBubble({ text, language }) {
  const [feedback, setFeedback] = useState(null);
  const [isCopied, setIsCopied] = useState(false);

  const handleFeedback = (type) => {
    setFeedback(type);
    // In the future, trigger an API call here to send the feedback to your backend
  };

  // 1. Copy to Clipboard Logic
  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(text);
      setIsCopied(true);
      
      // Change the icon back to 'Copy' after 2 seconds
      setTimeout(() => setIsCopied(false), 2000);
    } catch (err) {
      console.error("Failed to copy text:", err);
    }
  };

  // 2. Native Share API Logic (Great for mobile devices)
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
      // Fallback if the browser doesn't support the Share API (like some desktop browsers)
      await handleCopy();
      alert("Response copied to clipboard to share!");
    }
  };

  return (
    <div className="max-w-[92%] md:max-w-[85%] rounded-2xl px-4 py-3 md:px-5 md:py-4 bg-slate-50 text-slate-800 self-start rounded-bl-sm border border-slate-200">
      <p className="leading-relaxed text-sm md:text-base">{text}</p>
      
      <div className="mt-3 flex items-center justify-between border-t border-slate-200/60 pt-3">
        <ResponsePlayer text={text} language={language} />
        
        {/* Action Buttons Container */}
        <div className="flex items-center gap-1 md:gap-2">
          
          {/* Copy Button */}
          <button 
            onClick={handleCopy}
            title="Copy response"
            className="p-1.5 text-slate-400 hover:text-teal-600 hover:bg-slate-100 rounded-md transition-colors"
          >
            {isCopied ? <Check size={18} className="text-teal-600" /> : <Copy size={18} />}
          </button>

          {/* Share Button */}
          <button 
            onClick={handleShare}
            title="Share response"
            className="p-1.5 text-slate-400 hover:text-teal-600 hover:bg-slate-100 rounded-md transition-colors"
          >
            <Share2 size={18} />
          </button>

          {/* Visual Divider */}
          <div className="w-px h-4 bg-slate-200 mx-1"></div>

          {/* Thumbs Up Button */}
          <button 
            onClick={() => handleFeedback('up')}
            className={`p-1.5 rounded-md transition-colors ${
              feedback === 'up' ? 'text-teal-600 bg-teal-100' : 'text-slate-400 hover:text-teal-600 hover:bg-slate-100'
            }`}
          >
            <ThumbsUp size={18} className={feedback === 'up' ? 'fill-current' : ''} />
          </button>
          
          {/* Thumbs Down Button */}
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