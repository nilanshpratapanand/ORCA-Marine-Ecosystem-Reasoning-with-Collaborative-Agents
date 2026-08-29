# agents/reasoning.py
#
# The Reasoning/Synthesis Agent. Turns (question + retrieved data + domain
# advisory output + time scope) into one natural-language answer, then hands
# it to the Language Agent to render in the user's language.
#
# It works WITHOUT any API key: if no LLM provider is configured (see llm.py)
# it uses a template. Add a GROQ_API_KEY (or any of the other free tiers) to
# backend/.env and it upgrades to real generated prose automatically — no
# other file changes.
#
# Hallucination guard: the prompt only ever lets the model talk about numbers
# that came from `cond` / the specialist's evidence — it never invents a fact.

from app.agents import language, llm


def synthesize_answer(question, region_data, advisory, cond, time_ctx, lang) -> dict:
    """Returns {answer, confidence, method, translation_method, evidence}.
    `answer` is already localized into the user's language."""
    if not region_data["found"]:
        text = (
            f"I don't have data for that region yet ({region_data['reason']}). "
            "Rather than guess, I'm flagging this as insufficient data — "
            "try one of the seeded demo regions (Kerala, Chennai, Visakhapatnam, "
            "Odisha, West Bengal, Gujarat, Mumbai)."
        )
        localized, tmethod = language.localize(text, lang, None)
        return {"answer": localized, "confidence": 0.0, "method": "insufficient_data",
                "translation_method": tmethod, "evidence": []}

    # 1. Build the English answer (LLM if any provider configured, else template).
    english, method = _generate(question, region_data, advisory, cond, time_ctx)

    # 2. Prepend a location / scope clause if the match wasn't exact.
    prefix = _scope_prefix(region_data, time_ctx)
    if prefix:
        english = f"{prefix} {english}"

    # 3. Localize into the user's language.
    localized, tmethod = language.localize(english, lang, advisory.get("verdict_tag"))

    return {
        "answer": localized,
        "confidence": advisory["confidence"],
        "method": method,
        "translation_method": tmethod,
        "evidence": advisory.get("evidence", []),
    }


def _generate(question, region_data, advisory, cond, time_ctx) -> tuple[str, str]:
    prompt = f"""You are one lens of a marine advisory system. A user asked: "{question}"
They are asking about: {time_ctx['scope_label']}.

The ONLY data you may use (do not invent any number not listed):
Effective conditions: {cond}
Specialist advisory ({advisory['framing']}): {advisory.get('recommendation')}
Evidence the specialist used: {advisory.get('evidence')}

Write 2-3 short sentences answering the user in the voice of that specialist.
State the recommendation first, then the key evidence. Do not add any fact not above."""

    text, provider = llm.complete(prompt, max_tokens=220)
    if text:
        return text, f"llm:{provider}"
    return _template_fallback(region_data, advisory, cond, time_ctx), "template"


def _scope_prefix(region_data: dict, time_ctx: dict) -> str:
    r = region_data["resolution"]
    if r["match_type"] == "assumed_default":
        return (
            f"You didn't name a location, so I'm assuming the {region_data['region_name']} "
            f"(name a port for a tighter read)."
        )
    if r["match_type"] == "broad":
        return (
            f"'{r['matched_on']}' is broad — showing the {region_data['region_name']} as representative."
        )
    return ""


def _template_fallback(region_data: dict, advisory: dict, cond: dict, time_ctx: dict) -> str:
    freshness = f" (data is {region_data['age_hours']:.1f}h old)" if region_data["age_hours"] > 24 else ""
    scope = time_ctx["scope_label"]
    body = advisory["recommendation"]
    ev = advisory.get("evidence", [])
    why = f" Basis: {'; '.join(ev)}." if ev else ""
    scope_note = "" if scope == "today" else f" [asked about: {scope}]"
    return f"{body}{why}{freshness}{scope_note}"
