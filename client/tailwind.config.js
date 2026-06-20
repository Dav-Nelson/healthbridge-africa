/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        health: {
          bg: '#180E09',           // Dark Cocoa (Slightly cooler brown, less muddy)
          surface: '#271710',      // Deep Mahogany
          chat: '#352014',         // Warm Kola Brown
          accent: '#E59500',       // Ghana Gold (Brighter, truer yellow-gold)
          accentLight: '#FFB81C',  // Bright Kente Yellow
          aiBubble: '#0A4A25',     // Naija Forest Green (Rich, vibrant Nigerian green, but dark-mode safe)
          userBubble: '#8C3D10',   // Rich Terracotta/Bronze
          textPrimary: '#FDF6E3',  // Clean Ivory
          textSecondary: '#C2A889',// Warm Sand
          border: '#452A18',       // Dark Cocoa Border
        }
      },
      fontFamily: {
        brand: ['"Playfair Display"', 'serif'],
        body: ['"DM Sans"', 'sans-serif'],
      },
      animation: {
        'spin-slow': 'spin 40s linear infinite',
      }
    },
  },
  plugins: [],
}