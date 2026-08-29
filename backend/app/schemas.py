# schemas.py
#
# Pydantic models = the "shape" of data flowing in and out of the API.
# FastAPI uses these to auto-validate requests and auto-generate docs
# (visit /docs once the server is running to see this in action).

from pydantic import BaseModel
from typing import Literal, Optional


# What the frontend sends us
class QueryRequest(BaseModel):
    question: str                                  # the user's natural-language question
    role: Literal["fisherman", "researcher", "disaster_ops"] = "fisherman"
    region: Optional[str] = None                    # e.g. "arabian_sea_kerala" — if None, orchestrator resolves from the question


# One entry in the "which agents fired" trace — this is your judge Q&A proof
# that the system is genuinely multi-agent, not a single chatbot call.
class AgentTraceEntry(BaseModel):
    agent: str
    action: str
    confidence: Optional[float] = None


# What we send back to the frontend
class QueryResponse(BaseModel):
    answer: str
    role: str
    region_used: Optional[str]
    region_match: Optional[str] = None              # how the region was resolved: explicit / named / broad / assumed_default
    time_scope: Optional[str] = None               # "today", "tomorrow morning", ...
    detected_language: Optional[str] = None
    confidence: float
    evidence: list[str] = []                        # the specific numbers + rules behind the recommendation
    citations: list[str]
    agent_trace: list[AgentTraceEntry]
    data_freshness_warning: Optional[str] = None
