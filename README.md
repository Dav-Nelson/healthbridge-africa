# HealthBridge Africa

> Speak in your language. Get reliable health guidance.

A multilingual voice health agent for Nigeria, Ghana, Ethiopia, and Kenya.
Built by Async Africa for The Build 2026 by NSK AI and The Udara Project.

Live: https://healthbridge-africa.vercel.app
GitHub: https://github.com/Dav-Nelson/healthbridge-africa

---

## The Problem

Six hundred million people across Sub-Saharan Africa face a health question
with nowhere reliable to turn. Google is in English. Clinics are hours away.
WhatsApp rumours fill the gap, and people act on wrong information or do
nothing at all. Preventable conditions become emergencies because the first
point of contact failed.

---

## What We Built

HealthBridge Africa is a voice-first AI health agent that lets people speak
or type health questions in their own language and receive grounded,
conversational guidance drawn from a curated knowledge base built on WHO
guidelines and country-level health protocols.

The assistant remembers context across a conversation, asks clarifying
questions instead of giving flat one-shot answers, and responds in text
with voice playback and inline clinical imagery.

It does not replace doctors. It helps people know when to see one.

---

## Supported Languages

English, Nigerian Pidgin, Swahili, Oromo, Twi, Amharic.

Voice transcription is strongest for English, Swahili, and Amharic, which
Whisper-large-v3 supports natively. Pidgin and Twi route through
English-mode transcription since Whisper has no dedicated model for either.
Typed input in all six languages is unaffected by this limitation.

Gemini 2.5 Flash handles generation and has meaningfully better multilingual
coverage than the Llama-3.1-8B model used in earlier weeks, particularly
for Amharic and Oromo. Twi remains the weakest supported language due to
limited training data in available open models.

---

## How It Works
User speaks or types

|

React Frontend (Vercel)

|

Node.js + Express Gateway (Railway)

helmet, CORS, rate limiting, input validation

|

FastAPI AI Pipeline (Railway)

Whisper-large-v3 (Groq)        voice to text
Llama-3.3-70b (Groq)           language detection and English translation
Gemini embedding-001 (Google)  query embedding, 768 dimensions
pgvector search (Neon)         top-5 grounded health chunks
Gemini 2.5 Flash (Google)      RAG generation in user's language
gTTS                           audio synthesis, in-memory, Base64

|

Text response + inline disease image + voice playback with speed control


Conversation history is stored per session in Neon PostgreSQL. The pipeline
retrieves the last 6 messages for context on every request. Users can delete
their full conversation history from both device and server via Settings.

---

## Tech Stack

| Layer | Technology | Notes |
|---|---|---|
| Frontend | React + Tailwind CSS | Deployed on Vercel |
| Gateway | Node.js + Express | Deployed on Railway |
| Security | helmet + express-rate-limit | CORS locked to Vercel domain |
| AI Pipeline | FastAPI (Python) | Deployed on Railway |
| Database | PostgreSQL + pgvector (Neon) | Conversations + vector embeddings |
| STT | Whisper-large-v3 via Groq | Voice transcription |
| Language Detection | Llama-3.3-70b via Groq | With medical terminology anchors |
| Generation | Gemini 2.5 Flash via Google | Multilingual RAG generation |
| Embeddings | Gemini embedding-001 via Google | 768-dimensional normalized vectors |
| TTS | gTTS | In-memory synthesis, Base64 output |
| Analytics | PostHog | Session tracking, geography, retention |
| CI | GitHub Actions | Backend and frontend test suites |

---

## Knowledge Base

15+ conditions covered per country, grounded in official national guidelines.

Conditions: Malaria, Typhoid Fever, Cholera, Tuberculosis, HIV/AIDS,
Lassa Fever, Meningitis, Dengue Fever, Measles, Chickenpox, Mpox,
Scabies, Ringworm, Eczema, Conjunctivitis, Jaundice, Malnutrition,
Hypertension, Diabetes, Sickle Cell Disease, Schistosomiasis,
Maternal and Neonatal Health.

Sources: WHO Global Guidelines, Nigeria NCDC and FMoH, Ghana Health Service,
Kenya Ministry of Health, Federal Ministry of Health Ethiopia and EPHI.

65 total chunks embedded via Gemini embedding-001 and stored in Neon
with pgvector for semantic retrieval. See ai-pipeline/knowledge-base/sources.md
for full source attribution.

---

## Security

| Control | Implementation |
|---|---|
| HTTP security headers | helmet.js |
| CORS | Locked to healthbridge-africa.vercel.app |
| Rate limiting | 60 req per 15 min general, 20 req per 15 min on AI endpoints |
| Input validation | 2000 character max on all text inputs |
| File upload limit | 10 MB via multer |
| SQL injection protection | Parameterized queries throughout |
| Secrets management | All keys in .env files, excluded via .gitignore |
| HTTPS | Enforced at platform level by Vercel and Railway |

---

## Data and Privacy

Conversations are stored in Neon PostgreSQL, linked only to an anonymous
device session ID. No name, email, or personal identity is collected.

Users can delete all conversation data from both device and server at any
time via Settings, which calls DELETE /api/voice/history/:sessionId.

Automatic data expiry after 90 days is planned and not yet implemented.

---

## Known Limitations

Twi, Amharic, and Oromo language quality is inconsistent. Gemini 2.5 Flash
performs significantly better than Llama-3.1-8B for these languages, but
reliable fluent generation in Twi specifically remains a known gap. The
pipeline includes degenerate output detection at both character and
sentence level, with language-specific safe fallback messages when a
response is detected as broken.

Pidgin and Twi voice transcription route through English-mode Whisper, which
degrades accuracy for voice input in these two languages specifically.

The FAQ panel is in English only regardless of the active language setting.

Disease images sourced from Wikimedia Commons have not been reviewed by a
dermatologist. Several URLs returned broken images in production testing.
Clinically validated imagery from Mind the Gap or Black Derm Directory is
the planned replacement.

No user authentication exists. Sessions are device-bound via localStorage.
Two people sharing a device share a session unless one clears history.

Free-tier hosting on Railway after Render suspended the service due to
free-tier compute exhaustion from team testing.

---

## Getting Started

```bash
git clone https://github.com/Dav-Nelson/healthbridge-africa.git
cd healthbridge-africa

# Backend dependencies
npm install

# Frontend dependencies
cd client && npm install && cd ..

# AI pipeline dependencies
cd ai-pipeline && pip install -r requirements.txt && cd ..

# Environment variables
cp .env.example .env
# Fill in: GROQ_API_KEY, GEMINI_API_KEY, DATABASE_URL, PostHog key
# Repeat for client/.env and ai-pipeline/.env

# Run backend
npm run dev

# Run frontend (separate terminal)
cd client && npm start

# Run AI pipeline (separate terminal, from ai-pipeline/)
uvicorn api.main:app --reload --port 8000
```

---

## Ingesting the Knowledge Base

Run this once after cloning, or whenever knowledge base documents change:

```bash
cd ai-pipeline
python -m rag.ingest_to_db
```

Clears existing chunks, re-embeds all five documents via Gemini, and stores
vectors in Neon. Requires DATABASE_URL and GEMINI_API_KEY in ai-pipeline/.env.

---

## Running Tests

```bash
# Backend tests
npm test

# Frontend tests
cd client && npm test -- --watchAll=false
```

---

## Project Structure
healthbridge-africa/

client/                   React frontend

src/

components/           Header, ChatDisplay, BotMessageBubble,

ResponsePlayer, SettingsPanel, HelpModal,

HistoryPanel

OnboardingModal.js

App.js

server/                   Node.js + Express gateway

routes/                 voice.js, health.js

db/                     Neon PostgreSQL connection

ai-pipeline/              FastAPI RAG pipeline

api/                    main.py

rag/                    query.py, ingest_to_db.py

tts/                    speak.py

knowledge-base/         WHO + 4 country health documents

tests/                    Backend test suite

.github/workflows/        CI: backend and frontend on every push

---

## The Team

| Name | Country | Role |
|---|---|---|
| David Nelson | Nigeria | Team lead, backend and architecture |
| Ibukun Oluwafemi | Nigeria | Frontend development, UI/UX, African design system |
| Ibsa Magarsa | Ethiopia | AI pipeline, Amharic and Oromo validation |
| Peggy Eyram Attah | Ghana | User research, tester recruitment, Twi validation |

---

## Safety Disclaimer

HealthBridge Africa is an information and triage tool only. It does not
diagnose, prescribe, or replace professional medical advice. Every response
includes guidance on when to seek professional care. Always consult a
qualified healthcare provider for medical decisions.

---

## License

MIT. See LICENSE.

Built across Nigeria, Ethiopia, and Ghana.
The Build 2026 by NSK AI and The Udara Project.
