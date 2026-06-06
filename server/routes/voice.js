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
    const selectedLanguage = req.body.language || 'en';

    const formData = new FormData();
    const audioBlob = new Blob([req.file.buffer], { type: req.file.mimetype });
    
    formData.append('file', audioBlob, req.file.originalname || 'audio.wav');
    formData.append('language', selectedLanguage);

    // FIXED fallback to point directly to your live production Python pipeline instance
    const pipelineBaseUrl = process.env.AI_PIPELINE_URL || 'https://healthbridge-africa.onrender.com';
    const response = await axios.post(`${pipelineBaseUrl}/voice-chat`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });

    res.json({
      success: true,
      transcribed: response.data.user_text,
      response: response.data.answer,
      audioPath: response.data.audio_file, 
      sources: response.data.sources,
      disclaimer: 'This is not medical advice. Please see a doctor for diagnosis and treatment.'
    });
  } catch (error) {
    console.error('Voice chat connection failure:', error.response?.data || error.message);
    res.status(500).json({ error: 'Voice chat failed', message: error.message });
  }
});

// POST /api/voice/speak
router.post('/speak', async (req, res) => {
  try {
    const pipelineBaseUrl = process.env.AI_PIPELINE_URL || 'https://healthbridge-africa.onrender.com';
    
    const pythonResponse = await axios.post(`${pipelineBaseUrl}/speak`, req.body, {
      responseType: 'arraybuffer',
      headers: { 'Content-Type': 'application/json' }
    });

    const contentType = pythonResponse.headers['content-type'] || 'audio/mpeg';
    res.setHeader('Content-Type', contentType);

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