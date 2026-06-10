const express = require('express');
const router = express.Router();
const axios = require('axios');

// POST /api/chat
router.post('/', async (req, res) => {
  const { query, language } = req.body;
  
  if (!query) {
    return res.status(400).json({ error: 'Query is required' });
  }

  try {
    // Trim slashes and use your explicit live pipeline URL if the environment variable isn't configured on Render yet
    const AI_PIPELINE_URL = process.env.AI_PIPELINE_URL 
      ? process.env.AI_PIPELINE_URL.replace(/\/$/, "")
      : 'https://healthbridge-africa-ai-pipeline.onrender.com';

    // Forward BOTH the question and the language code down to the Python RAG endpoint
    const aiPipelineResponse = await axios.post(`${AI_PIPELINE_URL}/ask`, {
      question: query,
      language: language || 'en'
    });

    // Extract data sent back from the Python FastAPI server
    const { answer, similarity_score, sources, language: detectedLanguage } = aiPipelineResponse.data;

    // Return the response back to your live frontend application
    res.json({
      success: true,
      query,
      language: detectedLanguage || language || 'english',
      response: answer,
      similarity_score,
      sources,
      disclaimer: 'This is not medical advice. Please see a doctor for diagnosis and treatment.'
    });
  } catch (error) {
    console.error('Chat error connecting to AI Pipeline:', error.message);
    res.status(500).json({ 
      error: 'Failed to generate response from AI pipeline',
      message: error.message 
    });
  }
});

module.exports = router;