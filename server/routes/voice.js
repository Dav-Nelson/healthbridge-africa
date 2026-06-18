const express = require('express');
const axios = require('axios');
const router = express.Router();
const multer = require('multer');
const pool = require('../db/index');

const upload = multer({ 
  storage: multer.memoryStorage(),
  limits: { fileSize: 10 * 1024 * 1024 }
});

const getPipelineUrl = () => process.env.AI_PIPELINE_URL || 'https://healthbridge-africa-ai-pipeline.onrender.com';

// Shared helper: save a message and fetch recent history for a session
async function saveMessage(sessionId, role, content, language) {
  await pool.query(
    'INSERT INTO conversations (session_id, role, content, language) VALUES ($1, $2, $3, $4)',
    [sessionId, role, content, language || 'en']
  );
}

async function getHistory(sessionId, limit = 6) {
  const result = await pool.query(
    `SELECT role, content FROM (
       SELECT role, content, created_at FROM conversations 
       WHERE session_id = $1 ORDER BY created_at DESC LIMIT $2
     ) AS recent ORDER BY created_at ASC`,
    [sessionId, limit]
  );
  // ask_rag expects { sender, text } shaped history — map role -> sender, content -> text
  return result.rows.map(r => ({ sender: r.role, text: r.content }));
}

// POST /api/voice/chat — full voice flow: audio -> transcribe -> RAG answer (text only)
router.post('/chat', upload.single('audio'), async (req, res) => {
  if (!req.file) {
    return res.status(400).json({ error: 'Audio file is required' });
  }
  try {
    const selectedLanguage = req.body.language || 'en';
    const sessionId = req.body.sessionId;

    if (!sessionId) {
      return res.status(400).json({ error: 'sessionId is required' });
    }

    const pipelineBaseUrl = getPipelineUrl();

    // Step 1: transcribe audio to text via FastAPI /transcribe
    const transcribeForm = new FormData();
    const audioBlob = new Blob([req.file.buffer], { type: req.file.mimetype });
    transcribeForm.append('file', audioBlob, req.file.originalname || 'audio.wav');

    const transcribeResponse = await axios.post(
      `${pipelineBaseUrl}/transcribe?language=${selectedLanguage}`,
      transcribeForm,
      { headers: { 'Content-Type': 'multipart/form-data' }, timeout: 45000 }
    );

    const transcribedText = transcribeResponse.data.text || '';
    if (!transcribedText.trim()) {
      return res.status(422).json({ error: 'Could not understand the audio. Please try again.' });
    }

    // Step 2: save user message, fetch history
    await saveMessage(sessionId, 'user', transcribedText, selectedLanguage);
    const history = await getHistory(sessionId);

    // Step 3: ask the grounded RAG question via FastAPI /ask
    const askResponse = await axios.post(`${pipelineBaseUrl}/ask`, {
      question: transcribedText,
      language: selectedLanguage,
      history: history
    }, {
      headers: { 'Content-Type': 'application/json' },
      timeout: 45000
    });

    const answer = askResponse.data.answer || '';

    // Step 4: save bot response
    await saveMessage(sessionId, 'bot', answer, selectedLanguage);

    return res.json({
      success: true,
      transcribed: transcribedText,
      response: answer,
      sources: askResponse.data.sources || [],
      disclaimer: 'This is not medical advice. Please see a doctor for diagnosis and treatment.'
    });
  } catch (error) {
    console.error('Voice chat failure:', error.response?.data || error.message);
    return res.status(500).json({ error: 'Voice chat failed', message: error.message });
  }
});

// POST /api/voice/text-chat — typed text flow with history
router.post('/text-chat', async (req, res) => {
  try {
    const { message, language, sessionId } = req.body;

    if (!message || !sessionId) {
      return res.status(400).json({ error: 'Message and sessionId are required' });
    }

    await saveMessage(sessionId, 'user', message, language);
    const history = await getHistory(sessionId);

    const pipelineBaseUrl = getPipelineUrl();
    const response = await axios.post(`${pipelineBaseUrl}/ask`, {
      question: message,
      language: language || 'en',
      history: history
    }, {
      headers: { 'Content-Type': 'application/json' },
      timeout: 45000
    });

    const answer = response.data.answer || '';
    await saveMessage(sessionId, 'bot', answer, language);

    return res.json({
      success: true,
      transcribed: message,
      response: answer,
      sources: response.data.sources || [],
      disclaimer: 'This is not medical advice. Please see a doctor for diagnosis and treatment.'
    });
  } catch (error) {
    console.error('Text chat failure:', error.response?.data || error.message);
    return res.status(500).json({ error: 'Text chat failed', message: error.message });
  }
});

// POST /api/voice/speak — text -> audio, called separately by frontend after displaying text
router.post('/speak', async (req, res) => {
  try {
    const pipelineBaseUrl = getPipelineUrl();
    
    const pythonResponse = await axios.post(`${pipelineBaseUrl}/speak`, req.body, {
      headers: { 'Content-Type': 'application/json' },
      responseType: 'text',
      timeout: 45000
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
      // Data was not JSON string, fallback to processing raw response stream
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