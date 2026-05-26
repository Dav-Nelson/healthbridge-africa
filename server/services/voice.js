// Voice Pipeline Service

async function transcribeAudio(audioBuffer) {
  // TODO: Call Whisper via Ollama or Groq API
  return 'Transcription coming soon';
}

async function textToSpeech(text) {
  // TODO: Call Kokoro TTS
  return null;
}

module.exports = { transcribeAudio, textToSpeech };
