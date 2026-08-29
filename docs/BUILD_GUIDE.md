# ORCA Starter Kit — Build Guide

This is a working, minimal slice of the full ORCA architecture from the project
proposal — enough to run locally today, demo the "collaborative agents" concept
honestly, and extend piece by piece as you both get more comfortable with
Python and React. It runs entirely offline on seeded sample data, so nobody is
blocked on the MOSDAC account approval to start building or rehearsing.

## Where this fits in the full plan

The proposal describes a much bigger system (real MOSDAC/INCOIS/Bhuvan
ingestion, PostGIS, Redis, vector search, WebSocket streaming, Docker
Compose). This starter kit builds the **core spine** first: API Gateway →
Orchestrator Agent → Data Retrieval Agent → Domain Advisory Agents →
Reasoning Agent → back to the user. Everything else in the proposal is an
upgrade you bolt onto this spine once it works — you do not need to build
the whole architecture before you have something demoable.

## 1. Run the backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000/docs — FastAPI auto-generates an interactive page
where you can fire test queries without even needing the frontend yet. Try
the `/query` endpoint with:

```json
{ "question": "Should I go fishing off Kerala today?", "role": "fisherman" }
```

If you get a JSON answer back with an `agent_trace` list, the backend works.

## 2. Run the frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://127.0.0.1:5173. Make sure the backend is running first — the
frontend calls `http://127.0.0.1:8000` directly (see `src/api.js`).

## 3. How a question flows through the system

```
You type a question in the browser
  -> App.jsx sends it to POST /query (src/api.js)
  -> main.py routes it to orchestrator.handle_query()
  -> orchestrator calls, in order:
       1. language.py       — detects the query language (script + Hinglish
                              keywords); the answer is rendered back in it
       2. time_context.py   — "today / kal / parso / tomorrow morning" -> day_offset
       3. data_retrieval.py — resolves the region (state / city / sea / coast,
                              English + Devanagari + Tamil), returns numbers,
                              and merges in the forecast slice for that day
       4. domain_advisory.py— fisherman / researcher / disaster_ops framing,
                              plus an evidence[] list of the numbers + rules used
       5. reasoning.py      — one readable answer, then localized via language.py
  -> orchestrator returns answer + agent_trace + evidence + region_match +
     time_scope + detected_language + confidence + citations
  -> App.jsx renders the answer, a row of chips (language / time / region /
     confidence), a "Why — evidence used" panel, and the full agent trace —
     the trace is your proof in judge Q&A that agents really are separate
     and collaborating, not one chatbot call in a costume.
```

Set `ANTHROPIC_API_KEY` in `backend/.env` to turn on (a) nicer prose from
`reasoning.py` and (b) real translation into the detected language. Without a
key everything still runs: templated prose, and a few hard-coded in-language
verdicts for the fisherman role (Hindi / Tamil / Bengali).

Each agent is its own file with one job. That separation is the whole point
of "Collaborative Agents" in the PS title — and it's also just good practice:
you can improve the Reasoning Agent without touching Data Retrieval at all.

## 4. What to build next, in priority order

1. **Swap the seeded dataset for real data.** Once your MOSDAC account is
   approved, write `mosdac_job.py` / `incois_job.py` (see proposal Section 5)
   to populate a real database, then change `data_retrieval.load_dataset()`
   to query it instead of the JSON file. Nothing else needs to change —
   that's the payoff of the agent split.
2. **Add the map view.** `MapView.jsx` with Leaflet + a Bhuvan WMS tile
   layer, per the proposal's frontend tree.
3. **Add the chart panel.** Time-series of SST/chlorophyll — you already
   have the raw numbers via the `researcher` role's response.
4. **Turn on the LLM.** `cp backend/.env.example backend/.env` and paste in a
   free `GROQ_API_KEY` (console.groq.com/keys). `llm.py` then routes prose +
   translation through Groq/Qwen, with Cerebras / OpenRouter / Gemini /
   Mistral / Together / Anthropic as automatic fallbacks if you add their keys
   too. No code changes. Check `GET /llm-status` to see what's wired, and run
   with `LLM_DEBUG=1` the first time to confirm the model name is current.
5. **Add streaming.** Replace the single POST with the `/stream` WebSocket
   from the proposal so the frontend shows agents "firing" live during the
   demo — this is a strong visual for judges.

## 5. Learning path if Python is new to you

You do not need to learn Python to Data-Retrieval-Agent depth before
touching this code — read `data_retrieval.py` and `domain_advisory.py`
first; they're the simplest (plain functions and dictionaries, no
frameworks). `main.py` and `schemas.py` use FastAPI/Pydantic "magic"
(decorators, type hints) that's fine to treat as boilerplate at first and
understand later. Comfortable-in-C helps more than you'd think: Python
functions, `if`/`for`, and dictionaries (Python's version of a hash
map/struct) aren't a big leap.

Suggested order to actually read the code, not just run it:
`data_retrieval.py` → `domain_advisory.py` → `reasoning.py` →
`orchestrator.py` → `schemas.py` → `main.py`.

## 6. Sanity-checked already

The core agent logic (data retrieval → domain framing → synthesis, plus the
"insufficient data" honesty path for unknown regions) was run and verified
end to end before this kit was handed to you — see the four example
questions and answers used to check it in the handoff notes. The FastAPI
HTTP layer itself and the npm frontend build weren't runnable in the
environment this was built in (no package-registry access there), so run
`uvicorn` and `npm run dev` yourselves as the first thing you do — if
something doesn't start, paste the error back and it's a five-minute fix.
