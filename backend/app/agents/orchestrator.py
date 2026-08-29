# agents/orchestrator.py
#
# The Orchestrator Agent: the "manager." Reads the query, calls the right
# specialist agents in the right order, and merges their outputs into one
# response — INCLUDING an agent_trace list showing exactly which agents fired
# and why. That trace is your proof, in the live demo and in judge Q&A, that
# this is genuinely multi-agent and not one chatbot call wearing a costume.
#
# Flow:
#   Language  ->  Time Context  ->  Data Retrieval  ->  Domain Advisory  ->  Reasoning/Synthesis

from app.agents import data_retrieval, domain_advisory, reasoning, language, time_context
from app.schemas import QueryRequest, QueryResponse, AgentTraceEntry


def handle_query(req: QueryRequest) -> QueryResponse:
    trace: list[AgentTraceEntry] = []

    # 1. Language Agent — detect what language to answer in.
    lang = language.detect(req.question)
    trace.append(AgentTraceEntry(
        agent="language",
        action=f"detected {lang['name']} (via {lang['source']})",
        confidence=0.9 if lang["source"] != "default" else 1.0,
    ))

    # 2. Time Context Agent — today / tomorrow / day after?
    time_ctx = time_context.resolve(req.question)
    trace.append(AgentTraceEntry(
        agent="time_context",
        action=f"scope = {time_ctx['scope_label']}"
               + (f" (matched '{time_ctx['matched_on']}')" if time_ctx["matched_on"] else " (no time phrase, defaulting to today)"),
        confidence=1.0,
    ))

    # 3. Data Retrieval Agent — which region, and its numbers.
    region_data = data_retrieval.fetch_region_data(req.region, req.question)
    res = region_data["resolution"]
    trace.append(AgentTraceEntry(
        agent="data_retrieval",
        action=(f"resolved region '{region_data['region_id']}' "
                f"({res['match_type']}"
                + (f" on '{res['matched_on']}'" if res["matched_on"] else "")
                + ")") if region_data["found"]
               else f"no data for '{region_data['region_id']}'",
        confidence=1.0 if region_data["found"] else 0.0,
    ))

    if not region_data["found"]:
        result = reasoning.synthesize_answer(req.question, region_data, {}, {}, time_ctx, lang)
        trace.append(AgentTraceEntry(agent="reasoning", action="returned insufficient-data response", confidence=0.0))
        return QueryResponse(
            answer=result["answer"],
            role=req.role,
            region_used=region_data["region_id"],
            region_match=res["match_type"],
            time_scope=time_ctx["scope_label"],
            detected_language=lang["name"],
            confidence=0.0,
            evidence=[],
            citations=[],
            agent_trace=trace,
            data_freshness_warning="No data for this region in the current seeded dataset.",
        )

    # 4. Merge current reading + forecast into the conditions for the asked day.
    cond = data_retrieval.conditions_at(region_data, time_ctx["day_offset"])
    if cond.get("is_forecast"):
        trace.append(AgentTraceEntry(
            agent="data_retrieval",
            action=f"applied {cond['day_label']} forecast: waves {cond['wave_height_m']}m, wind {cond['wind_speed_kmph']} km/h",
            confidence=0.85,
        ))
    elif cond.get("forecast_gap"):
        trace.append(AgentTraceEntry(
            agent="data_retrieval",
            action=f"no forecast for {time_ctx['scope_label']} — using latest reading",
            confidence=0.5,
        ))

    # 5. Domain Advisory Agent — the specialist matching the user's role.
    meta = {
        "age_hours": region_data["age_hours"],
        "source": region_data["data"].get("source"),
        "region_name": region_data["region_name"],
    }
    advisory_fn = domain_advisory.ROLE_TO_AGENT[req.role]
    advisory = advisory_fn(cond, meta)
    trace.append(AgentTraceEntry(
        agent=f"domain_advisory:{advisory['framing']}",
        action="produced role-tailored recommendation — evidence: " + "; ".join(advisory.get("evidence", []))[:160],
        confidence=advisory["confidence"],
    ))

    # 6. Reasoning/Synthesis Agent — prose + localization.
    result = reasoning.synthesize_answer(req.question, region_data, advisory, cond, time_ctx, lang)
    trace.append(AgentTraceEntry(
        agent="reasoning",
        action=f"synthesized answer (text: {result['method']}, translation: {result['translation_method']})",
        confidence=result["confidence"],
    ))

    freshness_warning = None
    if region_data["age_hours"] > 24:
        freshness_warning = f"Data is {region_data['age_hours']:.1f} hours old — showing last known reading, not live."

    return QueryResponse(
        answer=result["answer"],
        role=req.role,
        region_used=region_data["region_id"],
        region_match=res["match_type"],
        time_scope=time_ctx["scope_label"],
        detected_language=lang["name"],
        confidence=result["confidence"],
        evidence=result["evidence"],
        citations=[f"seeded_demo:{region_data['region_id']}"],  # swap for real MOSDAC/INCOIS dataset IDs later
        agent_trace=trace,
        data_freshness_warning=freshness_warning,
    )
