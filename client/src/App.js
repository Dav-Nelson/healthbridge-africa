import React, { useState } from 'react';
import Header from './components/Header';

export default function App() {
  const [language, setLanguage] = useState('English');

  return (
    <div className='min-h-screen bg-slate-50 flex flex-col font-snas text-slate-800'>

      <Header language={language} setLanguage={setLanguage}/>

      <main className='flex-1 p-8 text-center text-slate-500 font-medium mt-10'>

      </main>
    </div>
  );
}