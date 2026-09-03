# agents/llm.py
#
# One place that talks to language models. Everything else (reasoning.py,
# language.py) calls llm.complete() and doesn't care which provider answered.
#
# Design: a FALLBACK CASCADE of free-tier providers. We try them in order;
# the first one that has an API key set AND returns a response wins. If every
# provider fails (or none is configured), complete() returns (None, None) and
# the caller falls back to its offline template — so the app never hard-fails
# just because a free tier is rate-limited or down.
#
# All providers except Anthropic speak the OpenAI /chat/completions dialect,
# so one function handles the lot. Add a provider by adding a row to _PROVIDERS.
#
# Configure via backend/.env (see .env.example):
#   GROQ_API_KEY=...            <- primary (Qwen on Groq, fast + free)
#   CEREBRAS_API_KEY=...        <- fallback
#   OPENROUTER_API_KEY=...      <- fallback (many :free models)
#   GEMINI_API_KEY=...          <- fallback (Google AI Studio free tier)
#   MISTRAL_API_KEY=...         <- fallback
#   TOGETHER_API_KEY=...        <- fallback
#   ANTHROPIC_API_KEY=...       <- fallback (paid; last by default)
#
# Optional overrides:
#   LLM_PROVIDER_ORDER=groq,cerebras,gemini      (comma list; default is all)
#   GROQ_MODEL=qwen/qwen3-32b   (per-provider *_MODEL override)
#   LLM_DEBUG=1                 (print which provider/model was tried + errors)

import os

try:
    from dotenv import load_dotenv
    load_dotenv()  # pick up backend/.env when running scripts or uvicorn
except Exception:
    pass

import httpx

_TIMEOUT = float(os.getenv("LLM_TIMEOUT", "20"))
_DEBUG = os.getenv("LLM_DEBUG", "").strip() not in ("", "0", "false", "False")


def _log(msg: str) -> None:
    if _DEBUG:
        print(f"[llm] {msg}")


# name -> (env_key, base_url, default_model, dialect)
# Model names drift. If a provider 404s on its model, set <NAME>_MODEL in .env
# to a current one (hit its /models endpoint to list). Verified working Sep 2026.
_PROVIDERS = {
    "groq":       ("GROQ_API_KEY",       "https://api.groq.com/openai/v1",                          "qwen/qwen3.8-27b",                             "openai"),
    "cerebras":   ("CEREBRAS_API_KEY",   "https://api.cerebras.ai/v1",                              "gpt-oss-120b",                                "openai"),
    "openrouter": ("OPENROUTER_API_KEY", "https://openrouter.ai/api/v1",                            "qwen/qwen3-32b:free",                          "openai"),
    "gemini":     ("GEMINI_API_KEY",     "https://generativelanguage.googleapis.com/v1beta/openai", "gemini-flash-lite-latest",                     "openai"),
    "mistral":    ("MISTRAL_API_KEY",    "https://api.mistral.ai/v1",                               "mistral-small-latest",                         "openai"),
    "together":   ("TOGETHER_API_KEY",   "https://api.together.xyz/v1",                             "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free", "openai"),
    "anthropic":  ("ANTHROPIC_API_KEY",  "https://api.anthropic.com/v1",                            "claude-3-5-haiku-latest",                      "anthropic"),
}

_DEFAULT_ORDER = ["groq", "cerebras", "openrouter", "gemini", "mistral", "together", "anthropic"]


def _order() -> list[str]:
    raw = os.getenv("LLM_PROVIDER_ORDER", "").strip()
    if not raw:
        return _DEFAULT_ORDER
    names = [n.strip() for n in raw.split(",") if n.strip() in _PROVIDERS]
    return names or _DEFAULT_ORDER


def _model_for(name: str, default: str) -> str:
    return os.getenv(f"{name.upper()}_MODEL", "").strip() or default


def configured_providers() -> list[str]:
    """Which providers currently have an API key set, in try-order."""
    out = []
    for name in _order():
        env_key = _PROVIDERS[name][0]
        if os.getenv(env_key):
            out.append(name)
    return out


def available() -> bool:
    return bool(configured_providers())


def complete(prompt: str, max_tokens: int = 300, system: str | None = None,
             temperature: float = 0.3) -> tuple[str | None, str | None]:
    """Try each configured provider in order. Return (text, provider_name),
    or (None, None) if every provider is missing/failing."""
    last_err = None
    for name in _order():
        env_key, base_url, default_model, dialect = _PROVIDERS[name]
        key = os.getenv(env_key)
        if not key:
            continue
        model = _model_for(name, default_model)
        try:
            _log(f"trying {name} ({model})")
            if dialect == "anthropic":
                text = _anthropic_chat(key, base_url, model, prompt, system, max_tokens, temperature)
            else:
                text = _openai_chat(key, base_url, model, prompt, system, max_tokens, temperature)
            if text:
                _log(f"ok <- {name}")
                return text.strip(), name
        except Exception as e:  # rate limit, bad model name, network, etc.
            last_err = f"{name}: {type(e).__name__}: {e}"
            _log(f"fail {last_err}")
            continue
    _log(f"all providers exhausted ({last_err})")
    return None, None


def _openai_chat(key, base_url, model, prompt, system, max_tokens, temperature) -> str:
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    resp = httpx.post(
        f"{base_url}/chat/completions",
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        json={"model": model, "messages": messages, "max_tokens": max_tokens, "temperature": temperature},
        timeout=_TIMEOUT,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


def _anthropic_chat(key, base_url, model, prompt, system, max_tokens, temperature) -> str:
    body = {
        "model": model,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "messages": [{"role": "user", "content": prompt}],
    }
    if system:
        body["system"] = system
    resp = httpx.post(
        f"{base_url}/messages",
        headers={
            "x-api-key": key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        json=body,
        timeout=_TIMEOUT,
    )
    resp.raise_for_status()
    return resp.json()["content"][0]["text"]
