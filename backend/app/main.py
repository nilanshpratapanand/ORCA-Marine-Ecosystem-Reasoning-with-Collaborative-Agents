# main.py
#
# The API Gateway. Run this with:
#   uvicorn app.main:app --reload
# then open http://127.0.0.1:8000/docs to try it interactively.

from dotenv import load_dotenv
load_dotenv()  # load backend/.env before anything reads os.getenv

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.schemas import QueryRequest, QueryResponse
from app.agents import orchestrator, llm

app = FastAPI(title="ORCA API Gateway", version="0.2.0")

# Lets the React dev server (localhost:5173) call this API during development.
# Tighten this before any real deployment.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    """Pipeline freshness check — useful in the demo to show the system
    honestly reports its own state instead of pretending everything's live."""
    return {"status": "ok", "mode": "seeded_offline_demo_data"}


@app.get("/llm-status")
def llm_status():
    """Shows which LLM providers are wired up (in fallback order). Handy in the
    demo: 'text generation is Groq/Qwen with N free-tier fallbacks'."""
    configured = llm.configured_providers()
    return {
        "llm_enabled": bool(configured),
        "fallback_order": configured,
        "mode": "generated prose + regional-language translation" if configured
                else "offline templates (no API key set)",
    }


@app.post("/query", response_model=QueryResponse)
def query(req: QueryRequest):
    """The single entrypoint every stakeholder question goes through.
    All the actual multi-agent logic lives in orchestrator.py — keep this
    function thin; it's just validation + routing."""
    return orchestrator.handle_query(req)
