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
router.post('/chat', upload.single('audio'), async (req, res) => {
  if (!req.file) {
    return res.status(400).json({ error: 'Audio file is required' });
  }
  try {
    const audioBlob = new Blob([req.file.buffer], { type: req.file.mimetype });
    const selectedLanguage = req.body.language || 'en';

    const formData = new FormData();
    formData.append('file', audioBlob, req.file.originalname || 'audio.wav');
    formData.append('language', selectedLanguage);

    const pipelineBaseUrl = process.env.AI_PIPELINE_URL || 'http://127.0.0.1:8000';
    const response = await axios.post(`${pipelineBaseUrl}/voice-chat`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });

    res.json({
      success: true,
      transcribed: response.data.user_text,
      response: response.data.answer,
      audioPath: response.data.audio_path,
      sources: response.data.sources,
      disclaimer: 'This is not medical advice. Please see a doctor for diagnosis and treatment.'
    });
  } catch (error) {
    console.error('Voice chat error:', error.response?.data || error.message);
    res.status(500).json({ error: 'Voice chat failed', message: error.message });
  }
});

// =========================================================================
// ADDED: POST /api/voice/speak (Proxies requests to the Python AI pipeline)
// =========================================================================
router.post('/speak', async (req, res) => {
  try {
    // Falls back to render URL if the local AI_PIPELINE_URL env variable isn't specified
    const pipelineBaseUrl = process.env.AI_PIPELINE_URL || 'https://healthbridge-africa.onrender.com';
    
    // Explicitly target the text-to-speech microservice path on your Python app
    const pythonResponse = await axios.post(`${pipelineBaseUrl}/api/voice/speak`, req.body, {
      responseType: 'arraybuffer', // Crucial: tells axios to preserve the raw binary chunk buffers
      headers: { 'Content-Type': 'application/json' }
    });

    // Pass the exact headers returned from python back to the React app
    const contentType = pythonResponse.headers['content-type'] || 'audio/mp3';
    res.setHeader('Content-Type', contentType);

    // Ship the binary buffer payload to the frontend
    return res.send(Buffer.from(pythonResponse.data));

  } catch (error) {
    console.error('Voice proxy /speak structural failure:', error.response?.data || error.message);
    return res.status(500).json({ 
      error: 'Proxy text-to-speech generation failure', 
      message: error.message 
    });
  }
});

module.exports = router;