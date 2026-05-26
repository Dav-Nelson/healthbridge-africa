const express = require('express');
const router = express.Router();

// POST /api/voice/transcribe
router.post('/transcribe', async (req, res) => {
  // TODO: integrate Whisper STT via Ollama or Groq
  res.json({ message: 'Voice transcription endpoint - coming soon' });
});

// POST /api/voice/speak
router.post('/speak', async (req, res) => {
  // TODO: integrate Kokoro TTS
  res.json({ message: 'TTS endpoint - coming soon' });
});

module.exports = router;
