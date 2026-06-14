const express = require('express');
const router = express.Router();
const axios = require('axios');
const pool = require('../db/index');

router.post('/', async (req, res) => {
  const { query, language, sessionId } = req.body;
  
  if (!query || !sessionId) {
    return res.status(400).json({ error: 'Query and sessionId are required' });
  }

  try {
    // 1. Save user message to database
    await pool.query(
      'INSERT INTO messages (session_id, sender, text) VALUES ($1, $2, $3)',
      [sessionId, 'user', query]
    );

    // 2. Fetch recent history for context
    const historyRes = await pool.query(
      `SELECT sender, text FROM (
         SELECT sender, text, created_at FROM messages 
         WHERE session_id = $1 ORDER BY created_at DESC LIMIT 5
       ) AS recent_messages ORDER BY created_at ASC`,
      [sessionId]
    );

    // 3. Send query + history to Python
    // Python will handle the RAG database search internally
    const AI_PIPELINE_URL = process.env.AI_PIPELINE_URL || 'https://healthbridge-africa-ai-pipeline.onrender.com';
    const aiPipelineResponse = await axios.post(`${AI_PIPELINE_URL}/ask`, {
      question: query,
      language: language || 'en',
      history: historyRes.rows
    });

    const { answer, sources } = aiPipelineResponse.data;

    // 4. Save bot response
    await pool.query(
      'INSERT INTO messages (session_id, sender, text) VALUES ($1, $2, $3)',
      [sessionId, 'bot', answer]
    );

    res.json({ success: true, response: answer, sources });
  } catch (error) {
    console.error('Chat error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

module.exports = router;