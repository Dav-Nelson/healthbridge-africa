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
Africa speak in their local language. Nigerian Pidgin, Amharic, Swahili,
or African English, and receive grounded, reliable health guidance drawn
from verified sources like WHO guidelines and African Ministry of Health
documents.

**It does not replace doctors. It helps people know when to see one.**

---

## How it works

```
User speaks (Pidgin · Oromo · Swahili · African English)
        ↓
Whisper STT → converts speech to text
        ↓
Embed query → semantic search over health knowledge base
        ↓
pgvector retrieves relevant WHO / MOH document chunks
        ↓
LLM generates grounded response from retrieved context only
        ↓
Kokoro TTS → converts response to natural voice audio
        ↓
User hears answer in accessible, clear Language
```

---

## Tech stack

| Layer | Technology | Why |
|-------|-----------|-----|
| Frontend | React | Voice-friendly component UI |
| Backend | Node.js + Express | PERN stack, orchestration layer |
| Database | PostgreSQL + pgvector (Supabase) | Data + vector embeddings in one place |
| STT | Whisper via Groq API | Multilingual, fast, free tier |
| TTS | Kokoro TTS | Open source, natural voice output |
| Voice pipeline | Pipecat | VAD + STT + LLM + TTS orchestration |
| LLM | Groq / Claude API | Fast grounded inference, free tiers |
| RAG | pgvector + embeddings | Retrieval over curated health documents |
| CI/CD | GitHub Actions | Automated tests on every pull request |
| Hosting | Render | Free tier, public internet from Week 2 |
| Analytics | PostHog | Session tracking and observability |

---

## Knowledge base sources

- World Health Organization (WHO) guidelines
- Nigerian Federal Ministry of Health (FMOH)
- Ethiopian Ministry of Health
- Ghana Health Service
- Kenya Ministry of Health

---

## The crew — Async Africa

| Name | Country | Role |
|------|---------|------|
| David Nelson | Nigeria 🇳🇬 | System Design · Backend development · 
| Ibukun Oluwafemi | Nigeria 🇳🇬 | Frontend developer · UI/UX | Health domain |
| Ibsa Magarsa | Ethiopia 🇪🇹 | AI pipeline · Python · Amharic validation |
| Peggy Eyram Attah | Ghana 🇬🇭 | User research · Tester recruitment · Twi validation |

---

## Getting started

```bash
# Clone the repo
git clone https://github.com/Dav-Nelson/healthbridge-africa.git

# Navigate into the project
cd healthbridge-africa

# Install dependencies
npm install

# Set up environment variables
cp .env.example .env
# Fill in your API keys: Groq, Supabase, PostHog

# Run development server
npm run dev
```

---

## Project structure

```
healthbridge-africa/
├── client/          # React frontend
├── server/          # Node.js + Express backend
│   ├── routes/      # API routes
│   ├── services/    # Voice pipeline, RAG, LLM services
│   └── db/          # PostgreSQL + pgvector setup
├── knowledge-base/  # Curated health documents (WHO, MOH)
├── tests/           # Unit and integration tests
└── .github/
    └── workflows/   # GitHub Actions CI/CD
```

---

## Safety disclaimer

HealthBridge Africa is an information and triage tool only.
It does not diagnose, prescribe, or replace professional medical advice.
Every response includes guidance on whether to seek professional care.
Always consult a qualified healthcare provider for medical decisions.

---

## The Build — weekly progress

| Week | Focus | Status |
|------|-------|--------|
| Week 1 | Problem & Blueprint | ✅ Complete |
| Week 2 | First Cut & Go Live | 🔄 In progress |
| Week 3 | The Hard Part | ⏳ Upcoming |
| Week 4 | The Noise | ⏳ Upcoming |
| Week 5 | The Hardening | ⏳ Upcoming |
| Week 6 | The Ship | ⏳ Upcoming |

---

## License

MIT — see [LICENSE](LICENSE)

---

*Built with ❤️ across Nigeria · Ethiopia · Ghana*
*The Build 2026 · NSK AI · The Udara Project*
