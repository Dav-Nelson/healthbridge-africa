[33mddf9b64[m[33m ([m[1;36mHEAD[m[33m -> [m[1;32mmain[m[33m, [m[1;31morigin/main[m[33m, [m[1;31morigin/HEAD[m[33m)[m fix: correct knowledge base paths for ingestion + expand RAG query to top-5 chunks with improved system prompt
[33m6a52d19[m feat: add inline disease imagery to bot responses using Wikimedia Commons
[33m55522e3[m docs: overhaul entire knowledge base — consistent structure, 15+ conditions per country, correct language references, expanded Ethiopia and sources index
[33m6e77ed7[m docs: rewrite WHO-guidelines.md with complete, consistent, expanded 15-condition coverage
[33m2cbfc33[m fix: prevent autoplay loop by guarding with hasAutoPlayedRef
[33m5a58bf3[m fix: wrap fetchAndPlayAudio in useCallback to resolve useEffect dependency lint error
[33mb279975[m feat: add audio playback speed control with localStorage persistence to improve user experience
[33m5f12819[m feat: implement auto-play audio in ResponsePlayer using localStorage preference and useEffect
[33me993ee1[m fix(ui): improve responsiveness and overflow handling
[33m314e0fd[m feat: add HelpModal and SettingsPanel components
[33ma8be823[m Add real consultation history tab with localStorage session persistence
[33m1499427[m migrate embeddings from local sentence-transformers to Gemini API
[33mddc6ba3[m Fix request timeouts from 15s to 45s across all voice routes to absorb Render free-tier cold starts
[33m502af4b[m Week 6 prep: fix critical pipeline bugs, clean dead code, add conversational memory
[33m41116bc[m Update manifest for temporary configuration
[33m09daf05[m Fix medical card clipping and remove unused logo assets
[33mec9153a[m Finalize RAG architecture with Neon PostgreSQL and clean up dependencies
[33m55656a4[m feat: upgrade chat responses to medical-style cards with feedback icons
[33m5bd6f65[m Merge pull request #15 from Dav-Nelson/ibukun/frontend
[33mf96b8ae[m Update ingest script and generate vector store
[33m94141ec[m[33m ([m[1;31morigin/ibukun/frontend[m[33m, [m[1;32mibukun/frontend[m[33m)[m Merge branch 'main' into ibukun/frontend
[33m66328f6[m feat: add responsive mobile menu drawer toggle overlay
[33mb78b8a9[m fix: explicitly add Twi and Zulu to onboarding dropdown
[33mc854f4a[m fix: make onboarding inclusive for Ethiopian traffic and fix submit rate-limits
[33m45c2f9a[m Merge pull request #13 from ibukun/frontend (Sync & UI Overhaul)
[33med8cc71[m fix: dynamically translate medical disclaimer text fields
[33m900c0b9[m fix: remove unused Footer import to resolve Vercel build crash
[33md816e72[m feat: complete navigation sidebar container and optimize interactive card states
[33m73c8ba6[m feat: complete UI overhaul, medical dashboard layout, and onboarding tracking
[33maf6b6ba[m chore: resolve merge conflicts and fix posthog setup
[33m9dae939[m Merge branch 'main' into ibukun/frontend
[33m89f7b95[m chore: add posthog-js to package dependencies
[33md6bf473[m chore: integrate posthog analytics seamlessly
[33mb412fc2[m fix: resolve cloud deployment health checks and finalize posthog client config
[33mf1e7359[m feat(tts): implement dynamic regional voice accents and optimize language profiles
[33m7f1f759[m chore(rag): optimize quota metrics by utilizing llama-3.1-8b-instant across translation and execution layers
[33mc3101e4[m fix(proxy): fix syntax layout and separate voice and text routing endpoints cleanly
[33m5314abf[m fix(proxy): unify endpoint fallback urls across voice routes
[33m55f1581[m fix(proxy): add explicit response returns and isolate form-data instantiation
[33m0c039bf[m fix(proxy): reinforce stream parsing and expand timeouts across voice routes
[33m3375356[m fix(api): patch voice-chat language mapping and unify base64 audio handling
[33m10802cf[m fix: synchronize payload structures and content decoding across pipeline layers
[33m6c17d08[m fix: translate payload language shortcodes in python speak engine
[33m8ace5b4[m fix: enforce production python pipeline url fallback to repair connection failure
[33mef30c7d[m perf: strip duplicate blob allocation to resolve web service memory limit crash
[33m52d674f[m fix: resolve index lock and map payload key to audio_file
[33mef15892[m fix: restore rag query module to working production state
[33m8152e35[m feat: expose root standalone /speak endpoint on fastapi layer
[33m2b19214[m fix: refactor express voice router proxy to target new python root speak endpoint directly
[33mca00bf5[m fix: implement aggressive fallback routing parameters on voice speak endpoint proxy
[33ma136dc7[m fix: register proxy /speak route inside express voice router context
[33mf51642c[m feat: implement Amharic support and fix local API audio routing
[33m6884bab[m fix: universal text-to-speech stream decoding fallback layer
[33m0b33810[m fix: align frontend payload parameters to short ISO codes and fix media stream interpretation
[33m933ce13[m fix: active import resolution and add fail-safe runtime vector fallback mechanisms
[33mcded4a3[m fix: instantiate groq client inside query module to resolve NameError
[33m390044f[m fix: forward language context payload to fastapi and patch production network fallback url
[33mdf7c55c[m fix: enforce structural dictionary returns and make RAG alignment language-agnostic
[33ma2ce7f5[m fix: resolve import syntax alignment in speak module
[33m7d7a8e9[m fix: refactor audio translation layer and convert TTS output to Base64 stream
[33m5844ba0[m data: populate empty markdown files in knowledge-base
[33m687fd20[m fix: update test file to pass CI checks
[33mbd8b055[m Merge branch 'ibukun/frontend' of https://github.com/Dav-Nelson/healthbridge-africa into ibukun/frontend
[33m19aae6f[m fix: add gtts package for text to speech engine
[33m6c81cc6[m feat: update Footer with multilingual medical disclaimer
[33mf501331[m feat: add dynamic multilingual translations to ChatDisplay UI
[33mc3d8643[m feat: add dynamic input placeholders and pass language state to Footer
[33md970c62[m refactor: integrate BotMessageBubble and dynamic translations into ChatDisplay
[33mdbf9d47[m feat: create BotMessageBubble with feedback and action buttons
[33maeaf0b6[m fix: add openai library for api client imports
[33mca5b21c[m fix: remove whisper compilation dependency and add explicit setuptools
[33mae49009[m fix: pre-install setuptools for legacy build support
[33mfe73a59[m fix: upgrade docker python base image to 3.11 for numpy compatibility
[33m1410d05[m Merge branch 'david/backend'
[33m20a15fe[m chore: add Dockerfile and optimize requirements for deployment
[33m612d863[m feat: complete local end-to-end integration across frontend, backend, and ai-pipeline
[33me68d6f3[m Update ghana health knowledge base
[33m935d542[m[33m ([m[1;31morigin/Yaa-Peggy-patch-2[m[33m)[m Update ghana-health-facts.md
[33m9e3257e[m Ethiopia Health Facts Knowledge Base Document from Ibsa
[33mebcab3c[m Merge remote changes into ibsa/ai-pipeline
[33m458a82a[m WIP: Week 3 embedding pipeline and language improvements
[33mb0fc73a[m Add comprehensive Ethiopia health facts knowledge base
[33m2eb9822[m Resolve final merge conflicts in whisper transcription script
[33m5c58bdc[m Merge branch 'main' into ibsa/ai-pipeline
[33m039d3d0[m Improve RAG retrieval and knowledge base integration
[33mece7d41[m Fix vector store paths and RAG improvements
[33m536f804[m test: mock Groq service to bypass live API credential requirement in CI pipeline
[33mc024577[m query and ingest updatede
[33m28b58ad[m Fix RAG paths and knowledge base integration
[33m6e0cc93[m Rename knowledge-base to knowledge
[33mcf74400[m Week 2 progress: Groq RAG pipeline and multilingual voice agent
[33m920741f[m Setup AI pipeline environment and Whisper test
[33mf58aa72[m #7 ibsa/ai-pipeline Implemented and improved the AI pipeline.
[33m3341677[m Merge branch 'ibsa/ai-pipeline' of https://github.com/Dav-Nelson/healthbridge-africa into ibsa/ai-pipeline
[33m811c0a7[m query and ingest updatede
[33m63a4ed2[m #6 Update Ghana health knowledge base and regional facts
[33mee67daa[m[33m ([m[1;31morigin/Yaa-Peggy-patch-1[m[33m)[m Update ghana-health-facts.md
[33m4000d3e[m Merge AI voice orchestration and multilingual Groq RAG pipeline
[33me01131a[m test: mock Groq service to bypass live API credential requirement in CI pipeline
[33mffa473b[m Fix RAG paths and knowledge base integration
[33m647af06[m style: link global tailwind styles to fix unstyled frontend layout
[33mc799f80[m chore: setup standard react build structures and tailwind config for UI layout
[33m3dbc181[m feat: merge Week 2 frontend components and UI state updates
[33m783961e[m ci: bypass restricted fork secrets environment block for patch
[33m125b96a[m test(ci): add environment fallback string to Groq client initialization to prevent fork PR test failures
[33m84d8019[m fix(frontend): resolve layout broken styles and Tailwind typos in Header component
[33m593b476[m fix(frontend): refactor state updates in App.js to use safe functional callbacks
[33mdaf1d23[m Merge branch 'main' of https://github.com/Dav-Nelson/healthbridge-africa into ibukun/frontend
[33m39d0865[m feat: complete Week 2 progress on the UI components and connect backend voice/chat APIs
[33m5d73bdf[m feat: create the ResponsePlayer component
[33m1604ade[m feat: create the ChatDisplay component
[33m0ac78b6[m feat: create Footer component
[33mff3e177[m feat: create Footer component and corrected a typo on line 9 of the Header component
[33m4c31cc7[m Rename knowledge-base to knowledge
[33m1832c13[m Week 2 progress: Groq-based multilingual RAG voice pipeline
[33m116f324[m Week 2 progress: Groq RAG pipeline and multilingual voice agent
[33m4081d02[m fix: resolve groq api model deprecation and install dependencies
[33mb40ec85[m feat: merge verified backend architecture and trigger staging deployment
[33m23d9375[m Improve database connection logic and error handling
[33mc8ff884[m Update CI workflow for HealthBridge Africa
[33m88bb2b3[m ci: inject DATABASE_URL secret into test environment
[33m1df378d[m feat: complete backend with Groq AI integration and voice pipeline
[33m54ae9c5[m Setup AI pipeline environment and Whisper test
[33m55ce715[m fix: code on line 23 as languages not language
[33m190b534[m refractor: integrate Header component into App.js
[33m5110c3a[m feat: create Header component
[33m8fac764[m Merge branch 'main' of https://github.com/Dav-Nelson/healthbridge-africa
[33m45565d7[m feat: added the RAG knowledge base files for each African country
[33m9d280c4[m feat: backend server running with 3 passing tests
[33m062acca[m Update languages and team roles in README
[33m7ab477a[m Merge branch 'main' of https://github.com/Dav-Nelson/healthbridge-africa
[33md3b6f53[m feat: initialize HealthBridge Africa project structure
[33m97a1e31[m Update copyright holder in LICENSE file
[33mccaa35e[m Revise README for HealthBridge Africa project
[33me71d065[m Initial commit
