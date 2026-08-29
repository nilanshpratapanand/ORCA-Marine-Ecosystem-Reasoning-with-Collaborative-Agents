# agents/language.py
#
# The Language Agent. The PS puts explicit "emphasis on supporting Indian
# regional languages" — auto-detect the language of the question and answer
# back in the SAME language. This agent does two things:
#
#   1. detect(question)      -> which language the user wrote in
#   2. localize(text, lang)  -> the English answer, rendered in that language
#
# Detection is by Unicode script block (reliable, zero-dependency) plus a
# romanised-Hindi keyword check (so "kal machli pakadne jaana theek hai?"
# is recognised as Hindi even though it's typed in Latin letters).
#
# Translation: if ANTHROPIC_API_KEY is set, we ask Claude to translate the
# final answer (keeping all numbers intact). If not, we still return the
# English text but tagged with the detected language, plus a few hard-coded
# phrase translations for the highest-value fisherman replies so the offline
# demo shows *something* in-language. Wiring the real LLM in is one env var.

import re

from app.agents import llm


# Unicode script ranges for the major Indian scripts.
_SCRIPT_RANGES = [
    ("hi", "Hindi",     r"[ऀ-ॿ]"),   # Devanagari (Hindi/Marathi)
    ("bn", "Bengali",   r"[ঀ-৿]"),
    ("ta", "Tamil",     r"[஀-௿]"),
    ("te", "Telugu",    r"[ఀ-౿]"),
    ("kn", "Kannada",   r"[ಀ-೿]"),
    ("ml", "Malayalam", r"[ഀ-ൿ]"),
    ("gu", "Gujarati",  r"[઀-૿]"),
    ("or", "Odia",      r"[଀-୿]"),
    ("pa", "Punjabi",   r"[਀-੿]"),
]

# Romanised-Hindi / Hinglish give-aways (typed in Latin letters).
_HINGLISH_HINTS = {
    "kya", "kaise", "kaisa", "hai", "hain", "kal", "aaj", "aj", "parso", "machli",
    "machhli", "samundar", "samudra", "jaana", "jana", "jaun", "jau", "jaoon",
    "theek", "thik", "safe", "khatra", "mausam", "lehar", "leher", "hawa",
    "batao", "bता", "chahiye", "nikalna", "nikle", "kitna", "kitni", "kahan",
    "kaha", "abhi", "raat", "subah", "shaam",
}


def detect(question: str) -> dict:
    """Return {code, name, source} for the language the question is written in.
    Defaults to English."""
    for code, name, pattern in _SCRIPT_RANGES:
        if re.search(pattern, question):
            return {"code": code, "name": name, "source": "unicode_script"}

    words = set(re.findall(r"[a-z]+", question.lower()))
    if words & _HINGLISH_HINTS:
        return {"code": "hi", "name": "Hindi (romanised)", "source": "hinglish_keywords"}

    return {"code": "en", "name": "English", "source": "default"}


# Minimal offline phrase map for the most common fisherman verdicts. Keyed by a
# stable tag the reasoning agent passes through, NOT by matching English prose.
_OFFLINE_PHRASES = {
    "hi": {
        "safe_go": "समुद्र में जाना सुरक्षित है।",
        "do_not_go": "समुद्र में मत जाइए — मौसम ख़राब है।",
        "caution": "सावधानी से जाइए और निकलने से पहले दोबारा जाँच करें।",
    },
    "bn": {
        "safe_go": "সমুদ্রে যাওয়া নিরাপদ।",
        "do_not_go": "সমুদ্রে যাবেন না — আবহাওয়া খারাপ।",
        "caution": "সতর্ক থেকে যান, রওনার আগে আবার দেখে নিন।",
    },
    "ta": {
        "safe_go": "கடலுக்குச் செல்வது பாதுகாப்பானது.",
        "do_not_go": "கடலுக்குச் செல்ல வேண்டாம் — வானிலை மோசம்.",
        "caution": "எச்சரிக்கையுடன் செல்லுங்கள்; புறப்படும் முன் மீண்டும் சரிபார்க்கவும்.",
    },
}


def localize(text: str, lang: dict, verdict_tag: str | None = None) -> tuple[str, str]:
    """Return (localized_text, method). method is one of
    'not_needed' | 'llm:<provider>' | 'offline_phrase' | 'english_fallback'."""
    code = lang["code"]
    if code == "en":
        return text, "not_needed"

    prompt = (
        f"Translate the following marine advisory into {lang['name']}. "
        f"Keep every number, unit, coordinate and place name exactly as-is. "
        f"Return only the translation, nothing else.\n\n{text}"
    )
    translated, provider = llm.complete(prompt, max_tokens=400, temperature=0.0)
    if translated:
        return translated, f"llm:{provider}"

    # No LLM provider available — offline handling.
    if verdict_tag and code in _OFFLINE_PHRASES and verdict_tag in _OFFLINE_PHRASES[code]:
        phrase = _OFFLINE_PHRASES[code][verdict_tag]
        return f"{phrase}\n({text})", "offline_phrase"

    return (
        f"{text}\n[{lang['name']} translation needs an LLM — add GROQ_API_KEY (or any provider) to backend/.env]",
        "english_fallback",
    )
