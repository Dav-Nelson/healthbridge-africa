// server/services/db_search.js
const pool = require('../db/index');

/**
 * Searches the knowledge base for relevant chunks
 * @param {Array} queryEmbedding - The embedding vector of the user's query
 * @returns {Promise<Array>} - List of relevant text chunks
 */
async function searchKnowledgeBase(queryEmbedding) {
  // We use the <=> operator for Cosine Distance
  // 1 - distance = similarity. We order by distance ascending.
  const query = `
    SELECT text 
    FROM knowledge_base 
    ORDER BY embedding <=> $1::vector 
    LIMIT 3;
  `;
  
  // Note: pgvector expects the embedding as a string or array format
  const embeddingString = JSON.stringify(queryEmbedding);
  const result = await pool.query(query, [embeddingString]);
  
  return result.rows.map(row => row.text);
}

module.exports = { searchKnowledgeBase };