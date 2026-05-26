# AI Pipeline — HealthBridge Africa

This folder is owned by **Ibsa Magarsa** (Ethiopia 🇪🇹)

## Structure
- `stt/` — Whisper Speech-to-Text via Ollama
- `tts/` — Kokoro Text-to-Speech
- `embeddings/` — Document embedding pipeline using nomic-embed-text
- `knowledge-base/` — Curated health documents

## Setup
1. Install Ollama: https://ollama.com
2. Pull required models:
```bash
ollama pull llama3
ollama pull nomic-embed-text
```

## Requirements
- Python 3.10+
- Ollama running locally on port 11434
