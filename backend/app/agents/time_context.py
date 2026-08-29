# agents/time_context.py
#
# The Time Context Agent. One job: work out WHICH DAY the user is asking about.
# The PS asks for questions like "Is it safe to venture into the sea TOMORROW
# MORNING?" — so "today" vs "tomorrow" vs "day after" has to actually change
# the answer. This agent turns the phrasing into a day_offset (0/1/2/3) that
# data_retrieval.conditions_at() then uses to pull the right forecast slice.
#
# Keyword-based on purpose (English + romanised Hindi). Swap for a proper
# temporal parser (e.g. duckling / an LLM) once the pipeline works end to end.

# phrase -> day_offset. Longest / most specific phrases first.
_TODAY = ["today", "aaj", "aj", "abhi", "right now", "is waqt", "currently", "now",
          "आज", "இன்று", "আজ"]
_TOMORROW = ["tomorrow", "tmrw", "tmr", "kal", "kl", "next morning", "morning after",
             "कल", "நாளை", "আগামীকাল", "কাল"]
_DAY_AFTER = ["day after tomorrow", "day after", "parso", "parason", "in two days", "2 days",
              "परसों", "परसो", "நாளை மறுநாள்"]
_IN_THREE = ["in three days", "in 3 days", "3 days", "teen din", "narso", "तीन दिन"]

# Time-of-day hints — we don't have hourly data in the MVP, but we surface the
# phrase so the answer can acknowledge it ("tomorrow morning") and so a later
# hourly-forecast upgrade has a hook to slot into.
_MORNING = ["morning", "subah", "sunrise", "dawn", "early", "सुबह", "காலை", "সকাল"]
_EVENING = ["evening", "shaam", "sham", "sunset", "dusk", "शाम", "மாலை", "সন্ধ্যা"]
_NIGHT = ["night", "raat", "tonight", "aaj raat", "overnight", "रात", "இரவு", "রাত"]


import re


def _normalize(question: str) -> str:
    # Punctuation -> spaces, collapse runs, pad ends, so we can match whole
    # words/phrases and avoid e.g. "रात" (night) matching inside "गुजरात"
    # (Gujarat). We keep the Indic script block U+0900–U+0D7F explicitly
    # because Python's \w drops the combining vowel signs (matras).
    text = re.sub(r"[।॥]", " ", question.lower())
    text = re.sub(r"[^\w\sऀ-ൿ]", " ", text)
    return " " + re.sub(r"\s+", " ", text) + " "


def _match(question: str, phrases: list[str]) -> str | None:
    q = _normalize(question)
    for p in sorted(phrases, key=len, reverse=True):
        if f" {p} " in q:
            return p
    return None


def resolve(question: str) -> dict:
    """Return {day_offset, scope_label, matched_on, time_of_day}.

    scope_label is a human string for the answer/trace ("today",
    "tomorrow morning", ...). day_offset defaults to 0 (today) when nothing
    time-like is said."""
    day_offset = 0
    matched_on = None

    for phrases, offset in (
        (_IN_THREE, 3),
        (_DAY_AFTER, 2),
        (_TOMORROW, 1),
        (_TODAY, 0),
    ):
        hit = _match(question, phrases)
        if hit:
            day_offset = offset
            matched_on = hit
            break

    tod = None
    for phrases, name in ((_MORNING, "morning"), (_EVENING, "evening"), (_NIGHT, "night")):
        if _match(question, phrases):
            tod = name
            break

    base_label = {0: "today", 1: "tomorrow", 2: "the day after tomorrow", 3: "in three days"}[day_offset]
    scope_label = f"{base_label} {tod}".strip() if tod else base_label

    return {
        "day_offset": day_offset,
        "scope_label": scope_label,
        "matched_on": matched_on or (tod if tod else None),
        "time_of_day": tod,
    }
