// src/utils/tracking.js

// Store API key as a named constant at the top as requested
const POSTHOG_API_KEY = "https://eu.posthog.com/project/197662/web";

export const startSilentTracking = async (selectedLanguage) => {
  // Step 1 — IP Geolocation (silent fetch)
  let geoData = { city: "unknown", country: "unknown", country_code: "unknown" };
  
  try {
    const geoResponse = await fetch('https://ipapi.co/json/');
    if (geoResponse.ok) {
      const data = await geoResponse.json();
      geoData = {
        city: data.city || "unknown",
        country: data.country_name || "unknown",
        country_code: data.country || "unknown"
      };
    }
  } catch (error) {
    // Fail gracefully and completely silently
  }

  // Step 2 — PostHog Event (silent fetch)
  try {
    const timestamp = new Date().toISOString();
    // Generate a random 6-character string for the distinct ID
    const random6chars = Math.random().toString(36).substring(2, 8);
    const distinctId = `user_${Date.now()}_${random6chars}`;
    
    // Capture browser language safely
    const languageSecondary = typeof navigator !== 'undefined' && navigator.language 
      ? navigator.language 
      : "unknown";

    const payload = {
      api_key: POSTHOG_API_KEY,
      event: "healthbridge_session_start",
      properties: {
        distinct_id: distinctId,
        platform: "HealthBridge Africa",
        timestamp: timestamp,
        language_primary: selectedLanguage?.name || "unknown",
        language_secondary: languageSecondary,
        city: geoData.city,
        country: geoData.country,
        country_code: geoData.country_code
      }
    };

    // Fire silently using keepalive: true
    fetch('https://app.posthog.com/capture/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
      keepalive: true // Ensures the request completes even if the user navigates away
    }).catch(() => {
      // Total silence if the tracking call itself gets blocked (e.g., by Brave or uBlock Origin)
    });

  } catch (error) {
    // Total silence for any execution errors
  }
};