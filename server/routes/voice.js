const express = require('express');
const axios = require('axios');
const router = express.Router();
const multer = require('multer');
const { transcribeAudio } = require('../services/groq');

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
    // 1. Convert the file buffer into a standard Blob object
    const audioBlob = new Blob([req.file.buffer], { type: req.file.mimetype });
    
    // 2. Extract the user language from the frontend request (defaults to 'en')
    const selectedLanguage = req.body.language || 'en';

    // 3. Pack everything cleanly into a standard form object
    const formData = new FormData();
    formData.append('file', audioBlob, req.file.originalname || 'audio.wav');
    formData.append('language', selectedLanguage);
    // 4. Send it directly to Ibsa's Python FastAPI server
    const pipelineBaseUrl = process.env.AI_PIPELINE_URL || 'http://127.0.0.1:8000';
    const response = await axios.post(`${pipelineBaseUrl}/voice-agent`, formData);

    // 5. Send the AI pipeline data back to the frontend UI
    res.json({
      success: true,
      transcribed: response.data.user_text,
      response: response.data.answer,
      sources: response.data.sources,
      disclaimer: 'This is not medical advice. Please see a doctor for diagnosis and treatment.'
    });
  } catch (error) {
    console.error('Voice chat error:', error.message);
    res.status(500).json({ error: 'Voice chat failed', message: error.message });
  }
});

module.exports = router;