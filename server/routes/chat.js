const express = require('express');
const router = express.Router();
const { generateHealthResponse } = require('../services/groq');

// POST /api/chat
router.post('/', async (req, res) => {
  const { query, language } = req.body;
  
  if (!query) {
    return res.status(400).json({ error: 'Query is required' });
  }

  try {
    const response = await generateHealthResponse(query);
    res.json({
      success: true,
      query,
      language: language || 'english',
      response,
      disclaimer: 'This is not medical advice. Please see a doctor for diagnosis and treatment.'
    });
  } catch (error) {
    console.error('Chat error:', error.message);
    res.status(500).json({ 
      error: 'Failed to generate response',
      message: error.message 
    });
  }
});

module.exports = router;