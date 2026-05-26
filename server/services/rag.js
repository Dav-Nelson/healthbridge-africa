// RAG Pipeline Service

const supabase = require('../db');

async function searchKnowledgeBase(query) {
  // TODO: embed query, search pgvector, return top chunks
  console.log('Searching knowledge base for:', query);
  return [];
}

async function generateResponse(query, context) {
  // TODO: call Ollama LLM with system prompt + context + query
  return 'RAG response generation coming soon';
}

module.exports = { searchKnowledgeBase, generateResponse };
