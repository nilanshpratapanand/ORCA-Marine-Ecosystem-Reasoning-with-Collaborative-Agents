# ORCA — Ocean Reasoning with Collaborative Agents

AI agentic conversational platform for marine ecosystem data (SST, chlorophyll,
weather, satellite EO) — **SIH 2026 PS #26176 for ISRO**.

Ask a marine question in your own language; a team of collaborating AI agents
(language → planning → data retrieval → weather/ocean analytics → geospatial →
risk → reasoning) works out an evidence-backed answer with a visible trace.

## Quick start

New here? **Read [SETUP.md](SETUP.md)** — clone, install, run, in order.

```
cd backend
py -3.12 -m venv venv
venv\Scripts\activate
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

Then in a second terminal:

```
cd frontend
npm install
npm run dev
```

Backend docs: http://127.0.0.1:8000/docs · UI: http://127.0.0.1:5173

## Docs

- [SETUP.md](SETUP.md) — dev environment setup + daily workflow + common errors
- [docs/BUILD_GUIDE.md](docs/BUILD_GUIDE.md) — how a question flows through the agents
- [docs/contracts.md](docs/contracts.md) — data-shape contract
