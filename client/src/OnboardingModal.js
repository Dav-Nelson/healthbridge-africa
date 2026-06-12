import React, { useState } from 'react';
import posthog from 'posthog-js';

export default function OnboardingModal({ onComplete }) {
  const [cityState, setCityState] = useState('');
  const [primaryLang, setPrimaryLang] = useState('English');
  const [secondaryLang, setSecondaryLang] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (isLoading) return;

    setIsLoading(true);

    try {
      // Capture data securely to PostHog
      posthog.capture('user_onboarding_completed', {
        city_state: cityState,
        primary_language: primaryLang,
        secondary_language: secondaryLang || 'None',
      });
      
      // Execute the callback to dismiss the modal
      onComplete();
    } catch (error) {
      console.error("Tracking failed:", error);
      onComplete(); // Ensure user isn't stuck if an analytics blocker blocks the script
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-60 flex items-center justify-center z-50 p-4 backdrop-blur-sm">
      <div className="bg-white rounded-xl shadow-2xl p-6 w-full max-w-md border border-gray-100 transform transition-all animate-in fade-in zoom-in-95 duration-200">
        <h2 className="text-xl font-bold text-gray-800 mb-2">Welcome to HealthBridge</h2>
        <p className="text-xs text-gray-500 mb-4">Please complete your profile to start your clinical consultation.</p>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          {/* City / State Input */}
          <div>
            <label className="block text-xs font-semibold text-gray-600 uppercase tracking-wider">City / Country</label>
            <input 
              type="text" 
              required
              disabled={isLoading}
              className="mt-1 block w-full rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 p-2.5 border text-sm disabled:bg-gray-50 disabled:text-gray-400"
              value={cityState} 
              onChange={(e) => setCityState(e.target.value)} 
              placeholder="e.g., Addis Ababa, ET or Lagos, NG" 
            />
          </div>

          {/* Primary Language Choice Dropdown */}
          <div>
            <label className="block text-xs font-semibold text-gray-600 uppercase tracking-wider">Primary Language</label>
            <select 
              disabled={isLoading}
              className="mt-1 block w-full rounded-lg border-gray-300 shadow-sm p-2.5 border text-sm bg-white focus:border-blue-500 focus:ring-blue-500 disabled:bg-gray-50" 
              value={primaryLang} 
              onChange={(e) => setPrimaryLang(e.target.value)}
            >
              <option value="English">English</option>
              <option value="Afan Oromo">Afan Oromo (Oromiffa)</option>
              <option value="Amharic">Amharic (አማርኛ)</option>
              <option value="French">French (Français)</option>
              <option value="Hausa">Hausa</option>
              <option value="Igbo">Igbo</option>
              <option value="Pidgin">Pidgin English</option>
              <option value="Swahili">Swahili (Kiswahili)</option>
              <option value="Yoruba">Yoruba</option>
              <option value="Other">Other Language</option>
            </select>
          </div>

          {/* Optional Secondary Language Input */}
          <div>
            <label className="block text-xs font-semibold text-gray-600 uppercase tracking-wider">Secondary Language (Optional)</label>
            <input 
              type="text" 
              disabled={isLoading}
              className="mt-1 block w-full rounded-lg border-gray-300 shadow-sm p-2.5 border text-sm focus:border-blue-500 focus:ring-blue-500 disabled:bg-gray-50"
              value={secondaryLang} 
              onChange={(e) => setSecondaryLang(e.target.value)} 
              placeholder="e.g., French, Amharic, Swahili"
            />
          </div>

          {/* Optimized Button with Async Loading Protection */}
          <button 
            type="submit" 
            disabled={isLoading}
            className="w-full bg-blue-600 text-white font-semibold py-2.5 px-4 rounded-lg hover:bg-blue-700 transition shadow-md shadow-blue-200 mt-2 flex items-center justify-center disabled:opacity-70 disabled:cursor-not-allowed"
          >
            {isLoading ? (
              <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
            ) : (
              "Start Consultation"
            )}
          </button>
        </form>
      </div>
    </div>
  );
}