"""Gemini client, AI helpers, and creator context.

Business logic — prompts, API integration, and data processing live here.
The client is lazy: the app boots (landing, auth, dashboard) even when no
``GEMINI_API_KEY`` is configured. AI helpers call ``_ensure_key()`` which
shows a friendly setup hint (paste-only `.streamlit/secrets.toml`) and stops
cleanly instead of crashing.
"""
import json
import os

import streamlit as st
from google import genai
from google.genai import types


_PLACEHOLDERS = {
    "",
    "your-api-key-here",
    "paste_your_key_here",
    "paste-your-key-here",
    "paste_your_gemini_api_key_here",
    "your_key_here",
    "changeme",
}


def _is_placeholder(value: str) -> bool:
    return value.strip().lower() in _PLACEHOLDERS


def _get_api_key() -> str:
    """Resolve the key from env first, then Streamlit secrets (safe).

    Returns "" when missing OR still set to the placeholder from
    `.streamlit/secrets.toml`, so the app shows a friendly setup hint
    instead of calling Gemini with an invalid key.
    """
    env_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if env_key and not _is_placeholder(env_key):
        return env_key
    try:
        # st.secrets may not exist (no secrets.toml) — never crash here.
        val = (st.secrets.get("GEMINI_API_KEY", "") or "").strip()
        if val and not _is_placeholder(val):
            return val
        return ""
    except Exception:
        return ""


API_KEY = _get_api_key()


def _get_model() -> str:
    """Resolve model name: env GEMINI_MODEL > secrets GEMINI_MODEL > default.

    Default follows Google's retirement notice (2.5-flash 404 → 3.6-flash).
    Override in `.streamlit/secrets.toml` with e.g.
    GEMINI_MODEL = "gemini-2.0-flash" if your key needs another version.
    """
    for source in (
        os.environ.get("GEMINI_MODEL", "").strip(),
        _safe_secret("GEMINI_MODEL"),
    ):
        if source:
            return source
    # 2.5-flash returns 404 for new keys (retired) — Google's notice points
    # to the 3.x flash line, so default there; fallbacks cover the rest.
    return "gemini-3.6-flash"


def _safe_secret(key: str) -> str:
    try:
        return (st.secrets.get(key, "") or "").strip()
    except Exception:
        return ""


GEMINI_MODEL = _get_model()

# Tried in order when the primary model fails with 404 (retired) or 403
# (project not enabled for that model line). Covers old keys (2.x) and
# new keys (3.x) with the default config.
MODEL_FALLBACKS = [
    GEMINI_MODEL,
    "gemini-2.5-flash",
    "gemini-3.6-flash",
    "gemini-flash-latest",
    "gemini-2.0-flash",
    "gemini-1.5-flash",
]
# De-dupe while preserving order.
_seen = set()
MODEL_FALLBACKS = [m for m in MODEL_FALLBACKS if m and not (m in _seen or _seen.add(m))]

_client_instance = None


def get_client():
    """Return a cached genai.Client, or None when no key is configured."""
    global _client_instance
    if _client_instance is not None:
        return _client_instance
    if not API_KEY:
        return None
    try:
        _client_instance = genai.Client(api_key=API_KEY)
        return _client_instance
    except Exception:
        return None


# Kept for backwards-compat imports (cip.features). May be None when
# no key is set — prefer get_client() in new code.
try:
    client = get_client()
except Exception:
    client = None


def is_ai_configured() -> bool:
    """True when a key is present and a client can be built."""
    return bool(API_KEY) and get_client() is not None


def missing_key_message() -> str:
    return (
        "🔑 **Gemini API key not configured.**\n\n"
        "1. Get a free key: https://aistudio.google.com/app/apikey\n"
        "2. Open `.streamlit/secrets.toml` and paste it here:\n\n"
        '```toml\nGEMINI_API_KEY = "PASTE_YOUR_KEY_HERE"\n```\n\n'
        "3. Save + restart: `streamlit run app.py`"
    )


def require_api_key() -> bool:
    """Show a setup hint and return False when AI is unavailable."""
    if is_ai_configured():
        return True
    st.warning(missing_key_message())
    return False


def friendly_ai_error(err: Exception) -> str:
    """Return a short actionable hint for common Gemini API failures."""
    text = f"{err}".lower()
    if "403" in text or "permission_denied" in text or "denied access" in text:
        return (
            "🔒 **API key rejected (403 PERMISSION_DENIED).** The model is fine — "
            "Google is refusing this key/project.\n\n"
            "1. Your key must be a **Gemini API key from AI Studio** "
            "(https://aistudio.google.com/app/apikey) — it starts with `AIza`. "
            "OAuth tokens or Cloud keys with restrictions will 403.\n"
            "2. At AI Studio, create the key with no referrer/IP restrictions "
            "(or add yours), and enable the **Generative Language API** if prompted.\n"
            "3. Paste only the key inside the quotes in `.streamlit/secrets.toml`, "
            "save, restart."
        )
    if "404" in text or "not_found" in text or "not found" in text or "no longer available" in text:
        return (
            "🧩 **Model not available (404).** Your key works but this model "
            "is retired for it. Set `GEMINI_MODEL = \"...\"` in "
            "`.streamlit/secrets.toml` to the model Google names in the error, "
            "save, restart."
        )
    if "429" in text or "quota" in text or "resource_exhausted" in text:
        return (
            "⏳ **Quota / rate limit hit.** Wait a minute and retry. "
            "Free keys have per-minute limits."
        )
    return ""


def _ensure_key():
    if is_ai_configured():
        return
    # Friendly Streamlit stop (no traceback) when called from a page.
    try:
        st.warning(missing_key_message())
        st.stop()
    except Exception:
        pass
    raise RuntimeError(
        "GEMINI_API_KEY_MISSING: paste your key into .streamlit/secrets.toml "
        "(see .streamlit/secrets.toml.example)"
    )


def get_context():
    """Return the global creator posts text for AI prompts."""
    return st.session_state.get("global_posts", "").strip()


def get_profile():
    """Return structured profile dict from sidebar inputs."""
    return {
        "niche": st.session_state.get("g_niche", ""),
        "platforms": st.session_state.get("g_platforms", []),
        "followers": st.session_state.get("g_followers", ""),
        "age_range": st.session_state.get("g_age", ""),
        "gender_split": st.session_state.get("g_gender", ""),
        "geography": st.session_state.get("g_geo", ""),
        "tone": st.session_state.get("g_tone", []),
        "engagement_rate": st.session_state.get("g_engagement", ""),
        "past_brands": st.session_state.get("g_past_brands", ""),
        "no_go": st.session_state.get("g_no_go", ""),
    }


def _is_retriable(err: Exception) -> bool:
    """True for per-model failures worth falling through (404 retired, 403 not enabled)."""
    text = f"{err}".lower()
    code = getattr(getattr(err, "response", None), "status_code", "")
    return (
        "404" in text
        or "not_found" in text
        or "not found" in text
        or "no longer available" in text
        or "403" in text
        or "permission_denied" in text
        or "denied access" in text
        or code in (403, 404)
    )


def _is_model_not_found(err: Exception) -> bool:
    return _is_retriable(err)


def generate_with_fallback(client, contents, config=None):
    """Try MODEL_FALLBACKS in order; raise friendly error if all fail."""
    last_err = None
    for model in MODEL_FALLBACKS:
        try:
            if config is None:
                return client.models.generate_content(model=model, contents=contents)
            return client.models.generate_content(model=model, contents=contents, config=config)
        except Exception as err:
            last_err = err
            if not _is_retriable(err):
                raise
            continue
    raise RuntimeError(
        "Gemini model not available (404 NOT_FOUND for "
        f"{', '.join(MODEL_FALLBACKS)}). "
        "Your API key works but none of these models are enabled for it. "
        "Set a working version in `.streamlit/secrets.toml` as "
        'GEMINI_MODEL = "gemini-2.0-flash" (or the model Google suggests in '
        "the error) then restart. Original error: "
        f"{last_err}"
    ) from last_err


def ask_ai(prompt):
    _ensure_key()
    c = get_client()
    response = generate_with_fallback(c, prompt)
    return response.text


def ask_ai_with_search(prompt):
    _ensure_key()
    c = get_client()
    try:
        response = generate_with_fallback(
            c,
            prompt,
            config=types.GenerateContentConfig(
                tools=[types.Tool(google_search=types.GoogleSearch())]
            ),
        )
        return response.text, True
    except Exception:
        return ask_ai(prompt), False


def ask_ai_json(prompt):
    raw = ask_ai(prompt + "\n\nRespond ONLY with valid JSON. No markdown fences, no commentary.")
    text = raw.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.lower().startswith("json"):
            text = text[4:]
    try:
        return json.loads(text), raw
    except Exception:
        return None, raw
