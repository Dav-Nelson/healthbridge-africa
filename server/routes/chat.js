const express = require('express');
const router = express.Router();
const axios = require('axios'); // Added axios to make HTTP requests to the AI pipeline

// POST /api/chat
router.post('/', async (req, res) => {
  const { query, language } = req.body;
  
  if (!query) {
    return res.status(400).json({ error: 'Query is required' });
  }

  try {
    // Define the AI pipeline URL. Fallback to localhost:8000 if env variable isn't loaded yet.
    const AI_PIPELINE_URL = process.env.AI_PIPELINE_URL || 'http://127.0.0.1:8000';

    // Forward the query directly to Ibsa's verified Python RAG endpoint
    const aiPipelineResponse = await axios.post(`${AI_PIPELINE_URL}/ask`, {
      question: query
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