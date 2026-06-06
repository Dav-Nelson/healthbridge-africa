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
    return res.json({ success: true, text });
  } catch (error) {
    console.error('Transcription error:', error.message);
    return res.status(500).json({ error: 'Transcription failed', message: error.message });
  }
});

// POST /api/voice/chat
router.post('/chat', upload.single('audio'), async (req, res) => {
  if (!req.file) {
    return res.status(400).json({ error: 'Audio file is required' });
  }
  try {
    const selectedLanguage = req.body.language || 'en';

    // Create a fresh FormData boundary instance for every isolated request
    const formData = new FormData();
    const audioBlob = new Blob([req.file.buffer], { type: req.file.mimetype });
    
    formData.append('file', audioBlob, req.file.originalname || 'audio.wav');
    formData.append('language', selectedLanguage);

    const pipelineBaseUrl = process.env.AI_PIPELINE_URL || 'https://healthbridge-africa.onrender.com';
    
    const response = await axios.post(`${pipelineBaseUrl}/voice-chat`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      timeout: 15000
    });

    // Ensure we explicitly return the JSON structure cleanly to prevent lingering headers
    return res.json({
      success: true,
      transcribed: response.data.user_text || '',
      response: response.data.answer || '',
      audioPath: response.data.audio_file || null, 
      sources: response.data.sources || [],
      disclaimer: 'This is not medical advice. Please see a doctor for diagnosis and treatment.'
    });
  } catch (error) {
    console.error('Voice chat connection failure:', error.response?.data || error.message);
    return res.status(500).json({ error: 'Voice chat failed', message: error.message });
  }
});

// POST /api/voice/speak
router.post('/speak', async (req, res) => {
  try {
    const pipelineBaseUrl = process.env.AI_PIPELINE_URL || 'https://healthbridge-africa.onrender.com';
    
    const pythonResponse = await axios.post(`${pipelineBaseUrl}/speak`, req.body, {
      headers: { 'Content-Type': 'application/json' },
      responseType: 'text',
      timeout: 15000 
    });

    try {
      const jsonData = JSON.parse(pythonResponse.data);
      if (jsonData && jsonData.audio) {
        const audioBuffer = Buffer.from(jsonData.audio, 'base64');
        res.setHeader('Content-Type', 'audio/mpeg');
        res.setHeader('Content-Length', audioBuffer.length);
        return res.send(audioBuffer);
      }
    } catch (e) {
      // Data was not JSON, drop down to raw binary logic
    }

    const contentType = pythonResponse.headers['content-type'] || 'audio/mpeg';
    res.setHeader('Content-Type', contentType);
    return res.send(Buffer.from(pythonResponse.data, 'binary'));

  } catch (error) {
    console.error('Voice proxy /speak structural failure:', error.response?.data || error.message);
    return res.status(500).json({ 
      error: 'Proxy text-to-speech generation failure', 
      message: error.message 
    });
  }
});

module.exports = router;