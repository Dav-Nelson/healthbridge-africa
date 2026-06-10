import React from 'react';
import { HeartPulse, Globe } from 'lucide-react';

export default function Header({ language, setLanguage }) {
    // Added 'Amharic' straight into the core dropdown mapping array
    const languages = ['English', 'Pidgin', 'Oromo', 'Twi', 'Swahili', 'Amharic'];
    
    return (
        <header className='bg-white border-b border-teal-100 shadow-sm sticky top-0 z-10'>
            <div className='max-w-4xl mx-auto px-4 py-4 flex items-center justify-between'>
                <div className='flex items-center gap-2 text-teal-700'>
                    <HeartPulse size={28} className='animate-pulse'/>
                    <h1 className='text-xl md:text-2xl font-extrabold tracking-tight'>
                        HealthBridge Africa 
                    </h1>
                </div>
                <div className='flex items-center gap-2 bg-slate-50 px-3 py-2 rounded-xl border border-slate-200'>
                    <Globe size={18} className='text-slate-500'/>
                    <select
                        value={language}
                        onChange={(e) => setLanguage(e.target.value)}
                        className='bg-transparent text-sm font-semibold text-slate-700 outline-none cursor-pointer'
                    >
                        {languages.map((lang) => (
                            <option key={lang} value={lang}>{lang}</option>
                        ))}
                    </select>
                </div>
            </div>
        </header>
    );
}