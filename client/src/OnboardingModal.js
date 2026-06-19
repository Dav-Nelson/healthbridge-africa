import React, { useState } from 'react';
import posthog from 'posthog-js';

export default function OnboardingModal({ onComplete }) {
  const [cityState, setCityState] = useState('');
  const [primaryLang, setPrimaryLang] = useState('English');
  const [secondaryLang, setSecondaryLang] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    posthog.capture('user_onboarding_completed', {
      city_state: cityState,
      primary_language: primaryLang,
      secondary_language: secondaryLang,
    });
    onComplete(); 
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-60 flex items-center justify-center z-50 p-4 backdrop-blur-sm">
      <div className="bg-white rounded-xl shadow-2xl p-6 w-full max-w-md border border-gray-100">
        <h2 className="text-xl font-bold text-gray-800 mb-2">Welcome to HealthBridge</h2>
        <p className="text-xs text-gray-500 mb-4">Please complete your profile to start your clinical consultation.</p>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-gray-600 uppercase tracking-wider">City / State</label>
            <input 
              type="text" 
              required
              className="mt-1 block w-full rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 p-2.5 border text-sm"
              value={cityState} 
              onChange={(e) => setCityState(e.target.value)} 
              placeholder="e.g., Lagos, LA" 
            />
          </div>
          <div>
            <label className="block text-xs font-semibold text-gray-600 uppercase tracking-wider">Primary Language</label>
            <select className="mt-1 block w-full rounded-lg border-gray-300 shadow-sm p-2.5 border text-sm bg-white" value={primaryLang} onChange={(e) => setPrimaryLang(e.target.value)}>
              <option>English</option>
              <option>Yoruba</option>
              <option>Hausa</option>
              <option>Igbo</option>
              <option>Pidgin</option>
            </select>
          </div>
          <div>
            <label className="block text-xs font-semibold text-gray-600 uppercase tracking-wider">Secondary Language (Optional)</label>
            <input 
              type="text" 
              className="mt-1 block w-full rounded-lg border-gray-300 shadow-sm p-2.5 border text-sm"
              value={secondaryLang} 
              onChange={(e) => setSecondaryLang(e.target.value)} 
              placeholder="e.g., French, Swahili"
            />
          </div>
          <button type="submit" className="w-full bg-blue-600 text-white font-semibold py-2.5 px-4 rounded-lg hover:bg-blue-700 transition shadow-md shadow-blue-200 mt-2">
            Start Consultation
          </button>
        </form>
      </div>
    </div>
  );
}