# Muse — Your Creative Growth Companion

10 AI-powered tools that learn your voice, grow your audience, and help you
close better brand deals — all in one Streamlit workspace.

Built with Streamlit + Google Gemini (configurable model, defaults to the 3.x flash line) + SQLite.

## Features

* **Caption Magic** — photo → captions, hashtags, trending songs, reel ideas
* **Content Studio** — content plans + hooks/titles/CTAs in your voice
* **Pre-Publish** — virality, engagement, brand safety, fact/copyright check
* **Growth Coach** — 30-day plan, problem solver, on-demand AI coach
* **Brand Match** — brand fit score, reputation check, campaign brief, social commerce
* **Brand DNA** — one-page media kit (authority, niche, SWOT)
* **Creator Earnings** — deal CRM with revenue charts
* **Wellbeing** — check-in, burnout predictor, fake-audience detector
* **Trends** — live-grounded briefing (Google Search grounding)
* **Insights / Library / Profile / Settings** — reports, memory, plans

## Quickstart

```bash
pip install -r requirements.txt
streamlit run app.py
```

Open http://localhost:8501 — landing → Sign up / Sign in / Try as Guest →
60-sec onboarding → Dashboard.

## API key (paste-only)

You only need to edit **one line**. No code changes.

1. Get a free key: https://aistudio.google.com/app/apikey
2. Open `.streamlit/secrets.toml`:
   ```toml
   GEMINI_API_KEY = "PASTE_YOUR_KEY_HERE"
   ```
   Paste your key inside the quotes, save.
3. Restart:
   ```bash
   streamlit run app.py
   ```

Notes:
* `.streamlit/secrets.toml` is git-ignored. Commit only
  `.streamlit/secrets.toml.example`.
* `GEMINI_API_KEY` env var also works (takes precedence).
* Without a key the app still boots — AI tools show a setup hint instead
  of crashing (`cip/ai.py:is_ai_configured`, `require_api_key`).

## Project structure

```
app.py                  # entry: theme → auth gate → onboarding → sidebar+router
cip/
  ai.py                 # lazy Gemini client + get_context/get_profile
  features.py           # prompts + JSON schemas + markdown formatters
  pages.py              # page renderers + ROUTES router
  ui.py                 # nav, themes, store_report/store_deal, widgets
  theme.py              # design-system CSS
  auth/auth.py          # login/signup/guest, session sync
  auth/pages.py         # landing + auth gate
  database/db.py        # SQLite (users, creator_profiles, saved_reports, deals)
.streamlit/
  config.toml           # Streamlit theme
  secrets.toml          # YOUR key (ignored) — just paste
  secrets.toml.example  # committed template
Logo.png
requirements.txt
```

## Database

Default `muse.db` (falls back to legacy `musely.db` if present).
Override: `DB_PATH=/path/to.db streamlit run app.py`.
Swap for Postgres/Supabase by replacing `_conn()` in `cip/database/db.py` —
function signatures stay the same.

Passwords are PBKDF2-HMAC-SHA256 hashed (`pbkdf2$salt$hash`) with legacy
sha256 fallback for old accounts.

## Security notes

* `secrets.toml` + `*.db` + `.env` are ignored — never commit keys or DBs.
* AI queries go to Google Gemini. Reports/profiles stay in local SQLite.
* Brand reputation / fake-audience results are AI heuristics — verify
  high-value deals independently.

## Troubleshooting

* `Gemini API key not configured` → paste key into
  `.streamlit/secrets.toml`, restart.
* Blank AI output → model returned non-JSON; raw output is shown + saved.
* Live search unavailable → song/trend tips fall back to base knowledge.
