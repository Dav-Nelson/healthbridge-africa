const Groq = require('groq-sdk');
require('dotenv').config();

const groq = new Groq({
  apiKey: process.env.GROQ_API_KEY
});

const SYSTEM_PROMPT = `You are HealthBridge Africa, a health information assistant for people across Africa.

RULES:
1. Answer ONLY using the context provided below.
2. If the context does not contain the answer, say: "I don't have reliable information on that. Please consult a healthcare provider."
3. Always end with: "This is not medical advice. Please see a doctor for diagnosis and treatment."
4. If the user describes an emergency (chest pain, difficulty breathing, unconsciousness, heavy bleeding), respond immediately with: "This sounds like a medical emergency. Please go to the nearest hospital immediately or call emergency services."
5. Be warm, clear, and speak like a knowledgeable friend — not a textbook.
6. Keep responses concise and easy to understand.

CONTEXT FROM KNOWLEDGE BASE:
{context}

USER QUESTION:
{question}`;

async function generateHealthResponse(question, context = '') {
  const prompt = SYSTEM_PROMPT
    .replace('{context}', context || 'No specific context available. Use general health knowledge.')
    .replace('{question}', question);

  const completion = await groq.chat.completions.create({
    messages: [{ role: 'user', content: prompt }],
    model: 'llama3-8b-8192',
    temperature: 0.3,
    max_tokens: 500
  });

  return completion.choices[0].message.content;
}

async function transcribeAudio(audioBuffer, mimetype) {
  const transcription = await groq.audio.transcriptions.create({
    file: audioBuffer,
    model: 'whisper-large-v3',
    language: 'en'
  });
  return transcription.text;
}

module.exports = { generateHealthResponse, transcribeAudio };