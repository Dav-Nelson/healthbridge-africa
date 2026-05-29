const express = require('express');
const router = express.Router();
const multer = require('multer');
const { transcribeAudio } = require('../services/groq');
const { generateHealthResponse } = require('../services/groq');

const upload = multer({ 
  storage: multer.memoryStorage(),
  limits: { fileSize: 10 * 1024 * 1024 }
});

// POST /api/voice/transcribe
router.post('/transcribe', upload.single('audio'), async (req, res) => {
  if (!req.file) {
    return res.status(400).json({ error: 'Audio file is required' });
  }
  try {
    const text = await transcribeAudio(req.file.buffer, req.file.mimetype);
    res.json({ success: true, text });
  } catch (error) {
    console.error('Transcription error:', error.message);
    res.status(500).json({ error: 'Transcription failed', message: error.message });
  }
});

// POST /api/voice/chat
// Full voice pipeline - transcribe + generate response
router.post('/chat', upload.single('audio'), async (req, res) => {
  if (!req.file) {
    return res.status(400).json({ error: 'Audio file is required' });
  }
  try {
    const text = await transcribeAudio(req.file.buffer, req.file.mimetype);
    const response = await generateHealthResponse(text);
    res.json({ 
      success: true,
      transcribed: text,
      response,
      disclaimer: 'This is not medical advice. Please see a doctor for diagnosis and treatment.'
    });
  } catch (error) {
    console.error('Voice chat error:', error.message);
    res.status(500).json({ error: 'Voice chat failed', message: error.message });
  }
});

module.exports = router;