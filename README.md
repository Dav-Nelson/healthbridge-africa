# HealthBridge Africa 🌍

> A multilingual voice health agent for Africa.
> Speak in your language, get reliable health guidance.

Built by **Async Africa** for [The Build 2026](https://theudaraproject.com)
by NSK AI · The Udara Project.

---

## The problem

Millions of Africans face a health question with nowhere reliable to turn.
Google is in English. Clinics are far. WhatsApp rumours are dangerous.
The result: people delay care, act on wrong information, or do nothing.
Preventable conditions become emergencies.

## Our solution

HealthBridge Africa is a voice-first AI health agent that lets people across
Africa speak or type in their local language — English, Nigerian Pidgin,
Swahili, Oromo, Twi, or Amharic — and receive grounded, conversational health
guidance drawn from a curated knowledge base built on WHO guidelines and
country-level health facts for Nigeria, Ghana, Ethiopia, and Kenya.

The assistant remembers context across a conversation, asks clarifying
questions rather than giving flat one-shot answers, and responds in text
first — with an option to play the response back as audio.

When the AI explains a condition, a relevant clinical image is shown inline —
sourced from Wikimedia Commons and selected to reflect how conditions present
on darker skin tones.

**It does not replace doctors. It helps people know when to see one.**

---

## How it works
User speaks or types (English · Pidgin · Swahili · Oromo · Twi · Amharic)
↓
Express.js gateway (Node.js) — routes by payload type
↓
┌─────────────────────────────────────────┐

│   FastAPI pipeline (Render)             │

│                                         │

│ 1. Whisper STT (Groq)                   │ → voice to text

│ 2. Cross-lingual alignment              │ → Llama-3.1-8B, standardizes

│                                         │   query to English for search

│ 3. Semantic retrieval                   │ → pgvector on Neon, top-k=5

│                                         │   grounded health chunks

│ 4. Conversational RAG inference         │ → Llama-3.1-8B-Instant, answers

│                                         │   in the user's language, with

│                                         │   conversation history

│ 5. Audio synthesis (on demand)          │ → gTTS, in-memory, Base64

└─────────────────────────────────────────┘
↓
Text response shown immediately

→ Inline disease image shown where relevant (Wikimedia Commons)

→ User can tap "Listen" for voice playback with adjustable speed (0.75x–1.5x)

Conversation history is stored in Neon Postgres per session, so the
assistant can refer back to earlier parts of the conversation and ask
follow-up questions instead of treating every message as a cold start.
Users can delete their session data from both the device and the server
via the Settings panel.

---

## Tech stack

| Layer | Technology | Why |
|-------|-----------|-----|
| Frontend | React (Create React App) + Tailwind CSS | Fast iteration, component-based UI |
| Gateway | Node.js + Express | Public-facing proxy, isolates the AI pipeline from direct internet traffic |
| Security | helmet + express-rate-limit | HTTP security headers, CORS lockdown, rate limiting |
| AI Pipeline | FastAPI (Python) | Stateless, containerized RAG orchestration |
| Database | PostgreSQL + pgvector (Neon) | Conversation history + vector embeddings in one place, free tier |
| STT | Whisper-large-v3 via Groq API | Fast, multilingual, generous free tier |
| Translation | Llama-3.1-8B (temp=0.0) via Groq | Deterministic cross-lingual alignment before retrieval |
| LLM (inference) | Llama-3.1-8B-Instant via Groq | Fast, conversational, grounded responses; high free-tier limits |
| Embeddings | Gemini Embedding API (gemini-embedding-001, 768-dim) | High-quality semantic embeddings, free tier |
| TTS | gTTS | Free, in-memory synthesis, regional accent routing for English |
| Analytics | PostHog | Session tracking, location and language insights |
| Hosting (frontend) | Vercel | Free tier, instant deploys |
| Hosting (pipeline + gateway) | Render | Free tier, containerized services |
| CI | GitHub Actions | Backend and frontend test suites run independently on every push |

---

## Supported languages

English, Nigerian Pidgin, Swahili, Oromo, Twi, Amharic.

Voice transcription accuracy is strongest for English, Swahili, and Amharic,
which Whisper-large-v3 supports natively. Pidgin and Twi voice input
currently routes through English-mode transcription as a stopgap, since
Whisper does not have dedicated support for either — typed input in these
languages does not have this limitation, since translation (via Llama-3.1-8B)
handles them independently of speech recognition.

Audio playback uses a West African-accented English voice (via gTTS's
`com.ng` regional routing) for English, Pidgin, and as the fallback voice
for Twi and Oromo. Swahili and Amharic use their own native gTTS voices.
Twi has no dedicated voice in any free TTS engine we evaluated; this is a
known limitation, not a configuration gap.

---

## Knowledge base

The knowledge base covers 15+ conditions per country, structured consistently
across all five documents and grounded in official national health guidelines.

**Conditions covered:** Malaria, Typhoid Fever, Cholera, Tuberculosis,
HIV/AIDS, Lassa Fever, Meningitis, Dengue Fever, Measles, Chickenpox,
Mpox/Monkeypox, Scabies, Ringworm, Eczema, Conjunctivitis, Jaundice,
Malnutrition, Hypertension, Diabetes, Sickle Cell Disease,
Schistosomiasis/Bilharzia, Maternal & Neonatal Health.

**Sources:**
- World Health Organization (WHO) global guidelines
- Nigeria Centre for Disease Control (NCDC) / Federal Ministry of Health
- Ghana Health Service (GHS) clinical guidelines
- Kenya Ministry of Health (MoH) national protocols
- Federal Ministry of Health (FMoH) Ethiopia / Ethiopian Public Health Institute

Knowledge base documents are chunked, embedded via Gemini Embedding API,
and stored in Neon Postgres with pgvector for semantic retrieval.
See `ai-pipeline/knowledge-base/sources.md` for full source attribution.

---

## Security

| Control | Implementation |
|---------|---------------|
| HTTP security headers | helmet.js |
| CORS | Locked to production Vercel domain only |
| Rate limiting | 60 req/15 min general; 20 req/15 min on AI endpoints |
| Input validation | 2000 character max on all text inputs |
| File upload limit | 10 MB hard limit via multer |
| SQL injection | Parameterized queries throughout (psycopg2 + node-postgres) |
| Secrets management | All keys in .env files, excluded via .gitignore |
| HTTPS | Enforced at platform level by Vercel and Render |

---

## Data & privacy

Conversations are stored in Neon PostgreSQL, linked only to an anonymous
device session ID — no name, email, or personal identity is collected.

Users can delete their full conversation history from both the device and
the server at any time via Settings → Clear my session.

Automatic data expiry after 90 days is planned but not yet implemented.

---

## The crew — Async Africa

| Name | Country | Role |
|------|---------|------|
| David Nelson | Nigeria 🇳🇬 | Team lead · backend & architecture · code review |
| Ibukun Oluwafemi | Nigeria 🇳🇬 | Frontend developer · UI/UX |
| Ibsa Magarsa | Ethiopia 🇪🇹 | AI pipeline · Python · Amharic & Oromo validation |
| Peggy Eyram Attah | Ghana 🇬🇭 | User research · tester recruitment · Twi validation |

---

## Getting started

```bash
# Clone the repo
git clone https://github.com/Dav-Nelson/healthbridge-africa.git
cd healthbridge-africa

# Install backend dependencies
npm install

# Install frontend dependencies
cd client && npm install && cd ..

# Install AI pipeline dependencies
cd ai-pipeline && pip install -r requirements.txt && cd ..

# Set up environment variables (repeat for client/ and ai-pipeline/ as needed)
cp .env.example .env
# Fill in: GROQ_API_KEY, DATABASE_URL (Neon), GEMINI_API_KEY, PostHog key

# Run the backend
npm run dev

# Run the frontend (separate terminal)
cd client && npm start

# Run the AI pipeline (separate terminal, from ai-pipeline/)
uvicorn api.main:app --reload --port 8000
```

---

## Ingesting the knowledge base

Run this once after cloning, or whenever the knowledge base documents change:

```bash
cd ai-pipeline
python -m rag.ingest_to_db
```

This clears existing chunks, re-embeds all five documents via Gemini, and
stores the vectors in Neon. Requires `DATABASE_URL` and `GEMINI_API_KEY`
in `ai-pipeline/.env`.

---

## Running tests

```bash
# Backend tests (Express routes)
npm test

# Frontend tests (React components)
cd client && npm test -- --watchAll=false
```

These are scoped independently — the root test command only runs backend
tests, and the frontend has its own React-aware test runner.

---

## Project structure
healthbridge-africa/

├── client/                  # React frontend

│   └── src/

│       ├── components/      # Header, ChatDisplay, BotMessageBubble, etc.

│       └── App.js

├── server/                  # Node.js + Express gateway

│   ├── routes/              # voice.js (chat, text-chat, speak, history), health.js

│   └── db/                  # Neon Postgres connection

├── ai-pipeline/             # FastAPI RAG + voice pipeline

│   ├── api/                 # main.py — /ask, /transcribe, /speak

│   ├── rag/                 # query.py, ingest_to_db.py

│   ├── tts/                 # speak.py

│   └── knowledge-base/      # Curated health documents (WHO + 4 country files)

├── tests/                   # Backend test suite

└── .github/

└── workflows/           # CI — backend + frontend tests on every push

---

## Known limitations

- **Pidgin and Twi voice transcription** currently route through English-mode Whisper as a stopgap — accuracy is degraded for voice input in these languages specifically. Typed input is unaffected.
- **No user authentication** — sessions are anonymous and device-bound via localStorage. Two people sharing a device share a session unless one clears it.
- **FAQ is English-only** regardless of the active language setting.
- **Free-tier hosting** means occasional 20–40 second cold-start delays on the AI pipeline after periods of inactivity.
- **Feedback collection relies on manual Google Forms** alongside PostHog analytics. This works at low user volume but won't scale — a sentiment analysis agent tied directly to the product, surfacing user satisfaction and pain points automatically from real conversations, is planned for a future phase.

See the Week 6 postmortem for the full list of known issues and planned fixes.

---

## Safety disclaimer

HealthBridge Africa is an information and triage tool only.
It does not diagnose, prescribe, or replace professional medical advice.
Every response includes guidance on whether to seek professional care.
Always consult a qualified healthcare provider for medical decisions.

---

## License

MIT — see [LICENSE](LICENSE)

---

*Built with ❤️ across Nigeria · Ethiopia · Ghana*
*The Build 2026 · NSK AI · The Udara Project*