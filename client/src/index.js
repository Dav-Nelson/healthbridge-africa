import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';
import posthog from 'posthog-js';
import reportWebVitals from './reportWebVitals';

// Safely grabs the token from your .env file
const POSTHOG_KEY = process.env.REACT_APP_POSTHOG_KEY;

posthog.init(POSTHOG_KEY, {
  api_host: 'https://eu.i.posthog.com',
  person_profiles: 'identified_only',
  capture_pageview: true // Automatically captures page views across your app
});

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

// If you want to start measuring performance in your app, pass a function
reportWebVitals();