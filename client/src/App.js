import React, { useState, useRef } from 'react';
import { Mic, Square, Send, MessageSquare, Settings, History, HelpCircle, Menu, X } from 'lucide-react';
import Header from './components/Header';
import ChatDisplay from './components/ChatDisplay';
import OnboardingModal from './OnboardingModal';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

const LANGUAGE_ISO_MAP = {
  'english': 'en',
  'pidgin': 'pcm',
  'swahili': 'sw',
  'oromo': 'om',
  'twi': 'tw',
  'amharic': 'am'
};

const getOrCreateSessionId = () => {
  let sessionId = sessionStorage.getItem('chat_session_id');
  if (!sessionId) {
    sessionId = crypto.randomUUID();
    sessionStorage.setItem('chat_session_id', sessionId);
  }
  return sessionId;
};

export default function App() {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [language, setLanguage] = useState('English');
  const [showOnboarding, setShowOnboarding] = useState(true);

  const [activeTab, setActiveTab] = useState('consultation');
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

  const getCleanLanguageCode = () => {
    const currentLang = language.toLowerCase();
    return LANGUAGE_ISO_MAP[currentLang] || currentLang;
  };

  const handleSendMessage = async (textToProcess) => {
    if (!textToProcess.trim()) return;

    setMessages(prev => [...prev, { sender: 'user', text: textToProcess }]);
    setInputValue('');
    setIsLoading(true);

    try {
      const targetCode = getCleanLanguageCode();
      const sessionId = getOrCreateSessionId();

      const response = await fetch(`${API_BASE_URL}/api/voice/text-chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: textToProcess,
          language: targetCode,
          sessionId: sessionId
        }),
      });

      if (!response.ok) throw new Error('API response failed');
      const data = await response.json();

      setMessages(prev => [...prev, {
        sender: 'bot',
        text: data.response,
        language: targetCode
      }]);
    } catch (error) {
      console.error("Chat Error:", error);
      setMessages(prev => [...prev, { sender: 'bot', text: "Sorry, I am having trouble connecting to the server right now." }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleTextSubmit = (e) => {
    e.preventDefault();
    handleSendMessage(inputValue);
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) audioChunksRef.current.push(event.data);
      };

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        stream.getTracks().forEach(track => track.stop());
        await processVoiceAudio(audioBlob);
      };

      mediaRecorder.start();
      setIsRecording(true);
    } catch (error) {
      console.error("Microphone Error:", error);
      alert("Unable to access the microphone. Please allow permissions.");
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  const processVoiceAudio = async (audioBlob) => {
    setIsLoading(true);
    const targetCode = getCleanLanguageCode();
    const sessionId = getOrCreateSessionId();

    const formData = new FormData();
    formData.append('audio', audioBlob, 'recording.webm');
    formData.append('language', targetCode);
    formData.append('sessionId', sessionId);

    try {
      const response = await fetch(`${API_BASE_URL}/api/voice/chat`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) throw new Error('Voice chat failed');

      const data = await response.json();

      if (data.transcribed) {
        setMessages(prev => [...prev, { sender: 'user', text: data.transcribed }]);
      }

      setMessages(prev => [...prev, {
        sender: 'bot',
        text: data.response,
        language: targetCode
      }]);
    } catch (error) {
      console.error("Voice Chat Error:", error);
      setMessages(prev => [...prev, { sender: 'bot', text: "Sorry, I couldn't process your voice message." }]);
    } finally {
      setIsLoading(false);
    }
  };

  const inputTranslations = {
    English: {
      placeholder: "Type your health question...",
      recording: "Listening...",
      disclaimer: "This system is not a substitute for professional medical advice. Always consult a certified doctor."
    },
    Pidgin: {
      placeholder: "Type your health question...",
      recording: "I dey listen...",
      disclaimer: "This system no be doctor substitute. Make you always check certified doctor."
    },
    Swahili: {
      placeholder: "Andika swali lako la afya...",
      recording: "Inasikiliza...",
      disclaimer: "Mfumo huu sio mbadala wa ushauri wa kitaalamu wa matibabu. Daima shauriana na daktari aliyethibitishwa."
    },
    Oromo: {
      placeholder: "Gaaffii fayyaa kee barreessi...",
      recording: "Dhaggeeffachaa jira...",
      disclaimer: "Sirni kun gorsa yaala ogeessaa bakka hin bu'u. Yeroo mara ogeessa fayyaa hayyama qabu mariisisi."
    },
    Twi: {
      placeholder: "Kyerɛw wo apɔwmuden asɛm...",
      recording: "Mretie...",
      disclaimer: "Eyi nsi aduruyɛ ho afutuo ananmu. Bere biara kɔbɔ oduruyɛfoɔ a ɔwɔ tumi krataa kɔkɔ."
    },
    Amharic: {
      placeholder: "የጤና ጥያቄዎን እዚህ ይጻፉ...",
      recording: "እያዳመጥኩ ነው...",
      disclaimer: "ይህ ዘዴ የባለሙያ የህክምና ምክርን አይተካም። ሁልጊዜ የተረጋገጠ ዶክተር ያማክሩ።"
    }
  };

  const tInput = inputTranslations[language] || inputTranslations.English;

  return (
    <div className="min-h-screen bg-slate-50 flex font-sans antialiased overflow-hidden relative">

      {showOnboarding && (
        <OnboardingModal onComplete={(selectedLanguage) => {
          if (selectedLanguage) setLanguage(selectedLanguage);
          setShowOnboarding(false);
        }} />
      )}

      <div
        className={`fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-sm transition-opacity duration-300 ${
          isMobileMenuOpen ? 'opacity-100 pointer-events-auto' : 'opacity-0 pointer-events-none'
        } md:hidden`}
        onClick={() => setIsMobileMenuOpen(false)}
      >
        <aside
          className={`w-72 bg-slate-900 h-screen p-6 text-slate-400 flex flex-col justify-between transform transition-transform duration-300 ease-out ${
            isMobileMenuOpen ? 'translate-x-0' : '-translate-x-full'
          }`}
          onClick={(e) => e.stopPropagation()}
        >
          <div className="flex flex-col gap-6 w-full">
            <div className="flex items-center justify-between">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-teal-500 to-emerald-400 flex items-center justify-center text-white shadow-md font-bold text-lg">
                HB
              </div>
              <button
                onClick={() => setIsMobileMenuOpen(false)}
                className="p-2 hover:bg-slate-800 rounded-lg text-slate-400"
              >
                <X size={20} />
              </button>
            </div>
            <hr className="border-slate-800" />

            <nav className="flex flex-col gap-2">
              <button
                onClick={() => { setActiveTab('consultation'); setIsMobileMenuOpen(false); }}
                className={`flex items-center gap-3 w-full p-3.5 rounded-xl font-medium transition ${
                  activeTab === 'consultation' ? 'bg-slate-800 text-teal-400' : 'hover:bg-slate-800/50 hover:text-slate-200'
                }`}
              >
                <MessageSquare size={20} />
                <span>Consultation Room</span>
              </button>
              <button
                onClick={() => { setActiveTab('history'); setIsMobileMenuOpen(false); }}
                className={`flex items-center gap-3 w-full p-3.5 rounded-xl font-medium transition ${
                  activeTab === 'history' ? 'bg-slate-800 text-teal-400' : 'hover:bg-slate-800/50 hover:text-slate-200'
                }`}
              >
                <History size={20} />
                <span>Medical History</span>
              </button>
            </nav>
          </div>

          <div className="flex flex-col gap-2 w-full">
            <button className="flex items-center gap-3 w-full p-3.5 rounded-xl font-medium hover:bg-slate-800/50 hover:text-slate-200 transition">
              <HelpCircle size={20} />
              <span>Help & FAQ</span>
            </button>
            <button
              onClick={() => { setActiveTab('settings'); setIsMobileMenuOpen(false); }}
              className={`flex items-center gap-3 w-full p-3.5 rounded-xl font-medium transition ${
                activeTab === 'settings' ? 'bg-slate-800 text-teal-400' : 'hover:bg-slate-800/50 hover:text-slate-200'
              }`}
            >
              <Settings size={20} />
              <span>System Settings</span>
            </button>
          </div>
        </aside>
      </div>

      <aside className="hidden md:flex w-20 bg-slate-900 h-screen flex flex-col items-center justify-between py-6 text-slate-400 border-r border-slate-800 flex-shrink-0">
        <div className="flex flex-col items-center gap-6 w-full">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-teal-500 to-emerald-400 flex items-center justify-center text-white shadow-md shadow-teal-900/30 font-bold text-lg">
            HB
          </div>
          <hr className="w-8 border-slate-800" />

          <button
            onClick={() => setActiveTab('consultation')}
            className={`p-3 rounded-xl transition relative group ${
              activeTab === 'consultation' ? 'bg-slate-800 text-teal-400 shadow-inner' : 'hover:text-slate-200'
            }`}
          >
            <MessageSquare size={22} />
            <span className="absolute left-full ml-4 px-2 py-1 bg-slate-950 text-white text-xs rounded opacity-0 group-hover:opacity-100 transition whitespace-nowrap z-50 shadow-xl pointer-events-none">Consultation</span>
          </button>
          <button
            onClick={() => setActiveTab('history')}
            className={`p-3 rounded-xl transition relative group ${
              activeTab === 'history' ? 'bg-slate-800 text-teal-400 shadow-inner' : 'hover:text-slate-200'
            }`}
          >
            <History size={22} />
            <span className="absolute left-full ml-4 px-2 py-1 bg-slate-950 text-white text-xs rounded opacity-0 group-hover:opacity-100 transition whitespace-nowrap z-50 shadow-xl pointer-events-none">History</span>
          </button>
        </div>

        <div className="flex flex-col items-center gap-4 w-full">
          <button className="p-3 hover:bg-slate-800 hover:text-slate-200 rounded-xl transition">
            <HelpCircle size={22} />
          </button>
          <button
            onClick={() => setActiveTab('settings')}
            className={`p-3 rounded-xl transition relative group ${
              activeTab === 'settings' ? 'bg-slate-800 text-teal-400 shadow-inner' : 'hover:text-slate-200'
            }`}
          >
            <Settings size={22} />
            <span className={`absolute left-0 w-1 h-4 bg-teal-500 rounded-r-full left-0 top-[18px] transition-transform ${activeTab === 'settings' ? 'scale-100' : 'scale-0'}`}></span>
          </button>
        </div>
      </aside>

      <div className="flex-1 flex flex-col h-screen overflow-hidden">

        <div className="flex items-center bg-white border-b border-slate-200 px-4 md:px-0">
          <button
            onClick={() => setIsMobileMenuOpen(true)}
            className="p-2 mr-1 text-slate-600 hover:bg-slate-50 rounded-lg block md:hidden transition"
          >
            <Menu size={24} />
          </button>
          <div className="flex-1">
            <Header language={language} setLanguage={setLanguage} />
          </div>
        </div>

        <main className="flex-grow flex flex-col max-w-4xl mx-auto w-full px-4 md:px-6 pt-4 pb-6 h-[calc(100vh-80px)] overflow-hidden">

          {activeTab === 'consultation' && (
            <>
              <ChatDisplay
                messages={messages}
                isLoading={isLoading}
                language={getCleanLanguageCode()}
              />

              <div className="bg-white rounded-2xl shadow-md shadow-slate-100/80 border border-slate-200 p-3 md:p-4 flex-shrink-0">
                <form onSubmit={handleTextSubmit} className="flex items-center gap-2 md:gap-3">
                  <button
                    type="button"
                    onClick={isRecording ? stopRecording : startRecording}
                    className={`p-3.5 md:p-4 rounded-xl flex-shrink-0 transition-all ${
                      isRecording
                        ? 'bg-red-500 hover:bg-red-600 text-white animate-pulse shadow-lg shadow-red-200'
                        : 'bg-slate-100 hover:bg-slate-200 text-slate-600'
                    }`}
                  >
                    {isRecording ? <Square size={18} fill="currentColor"/> : <Mic size={18} />}
                  </button>

                  <input
                    type="text"
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                    placeholder={isRecording ? tInput.recording : tInput.placeholder}
                    disabled={isRecording || isLoading}
                    className="flex-grow p-3.5 md:p-4 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-teal-500 focus:bg-white outline-none transition-all disabled:opacity-50 text-xs md:text-base"
                  />

                  <button
                    type="submit"
                    disabled={!inputValue.trim() || isLoading || isRecording}
                    className="p-3.5 md:p-4 bg-teal-600 hover:bg-teal-700 text-white rounded-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed flex-shrink-0"
                  >
                    <Send size={18} />
                  </button>
                </form>

                <p className="text-[10px] md:text-[11px] text-slate-400 text-center mt-3 font-medium px-2">
                  {tInput.disclaimer}
                </p>
              </div>
            </>
          )}

          {activeTab === 'history' && (
            <div className="flex-grow bg-white rounded-2xl shadow-sm border border-slate-200 p-6 flex flex-col items-center justify-center text-slate-400">
              <History size={48} className="text-slate-300 mb-3" />
              <p className="text-base font-medium text-slate-700">No Consultation History Yet</p>
              <p className="text-xs text-center mt-1">Your localized medical discussions will appear recorded here securely.</p>
            </div>
          )}

          {activeTab === 'settings' && (
            <div className="flex-grow bg-white rounded-2xl shadow-sm border border-slate-200 p-6 flex flex-col items-center justify-center text-slate-400">
              <Settings size={48} className="text-slate-300 mb-3" />
              <p className="text-base font-medium text-slate-700">System Preferences</p>
              <p className="text-xs text-center mt-1">Audio metrics, regional accent parameters, and data logs controls.</p>
            </div>
          )}

        </main>
      </div>

    </div>
  );
}