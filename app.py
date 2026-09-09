"""Muse — Your Creative Growth Companion.

Entry point. Wires the presentation layer together:
  • cip.database  — SQLite persistence (Postgres/Supabase-ready)
  • cip.auth      — session management, login, signup, guest mode
  • cip.theme     — design-system CSS
  • cip.ai        — Gemini client (business logic — untouched)
  • cip.features  — AI feature functions (business logic — untouched)
  • cip.ui        — reusable UI components + navigation
  • cip.pages     — page renderers, sidebar, and router
"""
import streamlit as st

# Must be the very first Streamlit command.
st.set_page_config(
    page_title="Muse — Your Creative Growth Companion",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── 1. Styles (no AI dependency) ─────────────────────────────────────────────
from cip.theme import inject_styles
inject_styles()

# ── 2. Auth (no AI dependency) ───────────────────────────────────────────────
from cip.auth.auth import init_auth, is_authenticated, current_user

init_auth()

if not is_authenticated():
    from cip.auth.pages import render_landing, render_auth_gate

    # Handle ?_auth= query params emitted by the pure-HTML landing page CTAs
    _qp_auth = st.query_params.get("_auth", "")
    if _qp_auth == "guest":
        from cip.auth.auth import enter_as_guest
        st.query_params.clear()
        enter_as_guest()
        st.rerun()
    elif _qp_auth in ("login", "signup"):
        st.session_state["_auth_view"] = _qp_auth
        st.query_params.clear()
    elif _qp_auth == "back":
        st.session_state.pop("_auth_view", None)
        st.query_params.clear()

    if st.session_state.get("_auth_view") in ("login", "signup"):
        render_auth_gate()
    else:
        render_landing()
    st.stop()

# ── 3. Onboarding guard ───────────────────────────────────────────────────────
# From here on, cip.ai is safe to import (st.secrets is available in Streamlit context).
user = current_user()
if user and not user.get("is_guest") and not user.get("onboarded"):
    from cip.pages import render_onboarding
    render_onboarding()
    st.stop()

# ── 4. Main app ───────────────────────────────────────────────────────────────
from cip.ui import init_state
from cip.pages import render_sidebar, render_page

init_state()

# Navigation from clickable HTML cards (?go=<Page>). Consume once, then clear.
_go = st.query_params.get("go")
if _go:
    from cip.pages import ROUTES as _ROUTES

    if _go in _ROUTES:
        st.session_state.page = _go
    st.query_params.clear()

render_sidebar()
render_page()
