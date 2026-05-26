const express = require('express');
const router = express.Router();

// POST /api/chat
router.post('/', async (req, res) => {
  const { query, language } = req.body;
  if (!query) return res.status(400).json({ error: 'Query is required' });
  // TODO: integrate RAG pipeline + LLM
  res.json({ 
    message: 'Chat endpoint - coming soon',
    received: { query, language }
  });
});

module.exports = router;
