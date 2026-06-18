import React from 'react';
import { X, HelpCircle, ChevronDown, ChevronUp } from 'lucide-react';
import { useState } from 'react';

const faqs = [
  {
    question: "Is HealthBridge Africa a replacement for a doctor?",
    answer: "No — HealthBridge Africa is a health information and triage tool, not a medical service. It helps you understand symptoms, know when to seek care, and get reliable health information in your language. Always consult a qualified healthcare provider for diagnosis and treatment."
  },
  {
    question: "What languages are supported?",
    answer: "HealthBridge Africa supports English, Nigerian Pidgin, Swahili, Oromo, Twi, and Amharic. You can switch languages anytime using the dropdown in the top right of the screen. The AI will respond in whichever language you select."
  },
  {
    question: "Is my conversation private?",
    answer: "Your conversations are stored securely and linked only to your device session. Your session is tied to your browser on this device — clearing your browser data will start a fresh session."
  },
  {
    question: "How accurate is the information?",
    answer: "Responses are grounded in verified sources including WHO guidelines and country-level health data from Nigeria, Ghana, Ethiopia, and Kenya. The AI does not guess or fabricate answers — if it does not have reliable information on a topic, it will tell you so and recommend consulting a healthcare professional."
  },
  {
    question: "How do I use the voice feature?",
    answer: "Tap the microphone button in the chat input area and speak your health question in your chosen language, then tap the stop button. HealthBridge will transcribe what you said, understand it, and respond in text. You can then tap the Listen button on any response to hear it read back to you."
  },
  {
    question: "What should I do in a medical emergency?",
    answer: "If you or someone nearby is experiencing a medical emergency — such as difficulty breathing, chest pain, heavy bleeding, or loss of consciousness — do not use HealthBridge Africa. Go to the nearest hospital immediately or call your local emergency services."
  }
];

function FAQItem({ question, answer }) {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="border border-slate-200 rounded-xl overflow-hidden">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between p-4 text-left bg-white hover:bg-slate-50 transition-colors"
      >
        <span className="text-sm font-semibold text-slate-800 pr-4">{question}</span>
        {isOpen
          ? <ChevronUp size={16} className="text-teal-600 flex-shrink-0" />
          : <ChevronDown size={16} className="text-slate-400 flex-shrink-0" />
        }
      </button>
      {isOpen && (
        <div className="px-4 pb-4 bg-slate-50 border-t border-slate-100">
          <p className="text-sm text-slate-600 leading-relaxed pt-3">{answer}</p>
        </div>
      )}
    </div>
  );
}

export default function HelpModal({ onClose }) {
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4 backdrop-blur-sm">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-lg border border-slate-100 flex flex-col max-h-[85vh]">

        <div className="flex items-center justify-between p-5 border-b border-slate-100 flex-shrink-0">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-teal-50 flex items-center justify-center">
              <HelpCircle size={18} className="text-teal-600" />
            </div>
            <div>
              <h2 className="text-base font-bold text-slate-800">Help & FAQ</h2>
              <p className="text-xs text-slate-400">Common questions about HealthBridge Africa</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-slate-100 rounded-lg text-slate-400 hover:text-slate-600 transition-colors"
          >
            <X size={18} />
          </button>
        </div>

        <div className="overflow-y-auto p-5 flex flex-col gap-3">
          {faqs.map((faq, index) => (
            <FAQItem key={index} question={faq.question} answer={faq.answer} />
          ))}
        </div>

        <div className="p-4 border-t border-slate-100 flex-shrink-0">
          <p className="text-[11px] text-slate-400 text-center">
            HealthBridge Africa is not a medical service. Always consult a qualified healthcare provider.
          </p>
        </div>
      </div>
    </div>
  );
}