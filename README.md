# ORCA — Ocean Reasoning with Collaborative Agents

AI agentic conversational platform for marine ecosystem data (SST, chlorophyll,
weather, satellite EO) — **SIH 2026 PS #26176 for ISRO**.

Ask a marine question in your own language; a team of collaborating AI agents
(language → planning → data retrieval → weather/ocean analytics → geospatial →
risk → reasoning) works out an evidence-backed answer with a visible trace.

## Quick start (Windows)

**Clean PC?** Download just **`install-orca.bat`**
([raw link](https://raw.githubusercontent.com/nilanshpratapanand/ORCA-Marine-Ecosystem-Reasoning-with-Collaborative-Agents/main/install-orca.bat))
and double-click it. It installs Git / Python 3.12 / Node if missing, downloads
this repo to your Desktop, sets up backend + frontend, and offers to start it.

**Already have the repo?**

1. Double-click **`setup.bat`** — builds the backend venv, installs everything.
   Re-runnable.
2. Put a free Groq key in `backend\.env` (`GROQ_API_KEY=...`, from
   https://console.groq.com/keys) — optional, the app runs without it.
3. Double-click **`run.bat`** — starts backend + frontend.

Backend docs: http://127.0.0.1:8000/docs · UI: http://127.0.0.1:5173

By hand, or on Mac/Linux? **[SETUP.md](SETUP.md)** has every step + a
common-errors table.

## Docs

- [SETUP.md](SETUP.md) — dev environment setup + daily workflow + common errors
- [docs/BUILD_GUIDE.md](docs/BUILD_GUIDE.md) — how a question flows through the agents
- [docs/contracts.md](docs/contracts.md) — data-shape contract
