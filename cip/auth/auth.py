"""Session management — login, signup, guest mode, logout.

Bridges the database layer with Streamlit session state.
Keeps all ai.py-compatible session keys (g_niche, global_posts, etc.) in sync.
"""
import streamlit as st

from cip.database.db import (
    init_db,
    create_user,
    verify_password,
    get_profile,
    get_reports,
    get_deals,
    mark_onboarded,
)

_GUEST = {
    "id": 0,
    "name": "Guest Creator",
    "email": "guest@muse.app",
    "avatar": "🌟",
    "plan": "free",
    "onboarded": 1,
    "is_guest": True,
}


def init_auth():
    """Must be called once, before any render. Sets up DB + auth state defaults."""
    init_db()
    st.session_state.setdefault("user", None)
    st.session_state.setdefault("_auth_tab", "login")


def current_user() -> dict | None:
    return st.session_state.get("user")


def is_authenticated() -> bool:
    return st.session_state.get("user") is not None


# ── Public actions ────────────────────────────────────────────────────────────

def login(email: str, password: str) -> tuple:
    """Return (success: bool, error_msg: str)."""
    user = verify_password(email, password)
    if not user:
        return False, "Incorrect email or password."
    _set_session(user)
    return True, ""


def signup(name: str, email: str, password: str) -> tuple:
    if len(name.strip()) < 2:
        return False, "Please enter your full name."
    email = email.strip().lower()
    if "@" not in email or "." not in email.split("@")[-1]:
        return False, "Please enter a valid email address."
    if len(password) < 6:
        return False, "Password must be at least 6 characters."
    user = create_user(name.strip(), email, password)
    if not user:
        return False, "An account with that email already exists."
    _set_session(user)
    return True, ""


def logout():
    for k in list(st.session_state.keys()):
        del st.session_state[k]
    st.rerun()


def enter_as_guest():
    st.session_state["user"] = dict(_GUEST)
    st.session_state["reports"] = {}
    st.session_state["deals"] = []
    st.session_state["metrics"] = {}
    st.session_state["page"] = "Dashboard"
    # No st.rerun() here — caller (app.py) reruns after clearing query params.


def complete_onboarding(uid: int):
    mark_onboarded(uid)
    if st.session_state.get("user"):
        st.session_state["user"]["onboarded"] = 1
    st.rerun()


# ── Internal helpers ──────────────────────────────────────────────────────────

def _set_session(user: dict):
    st.session_state["user"] = {**user, "is_guest": False}
    st.session_state["reports"] = {}
    st.session_state["deals"] = []
    st.session_state["metrics"] = {}
    st.session_state["page"] = "Dashboard"
    _load_profile_to_session(user["id"])
    _load_reports_to_session(user["id"])
    _load_deals_to_session(user["id"])


def _load_profile_to_session(uid: int):
    """Populate the session_state keys that cip.ai.get_profile() and get_context() read."""
    p = get_profile(uid)
    if not p:
        return
    st.session_state["global_posts"]   = p.get("recent_posts", "")
    st.session_state["g_niche"]        = p.get("niche", "")
    st.session_state["g_platforms"]    = p.get("platforms", [])
    st.session_state["g_followers"]    = p.get("followers", "")
    st.session_state["g_engagement"]   = p.get("engagement", "")
    st.session_state["g_age"]          = p.get("age_range", "")
    st.session_state["g_gender"]       = p.get("gender_split", "")
    st.session_state["g_geo"]          = p.get("geography", "")
    st.session_state["g_tone"]         = p.get("tone", [])
    st.session_state["g_past_brands"]  = p.get("past_brands", "")
    st.session_state["g_no_go"]        = p.get("no_go", "")
    # Extended profile fields
    st.session_state["g_bio"]          = p.get("bio", "")
    st.session_state["g_username"]     = p.get("username", "")
    st.session_state["g_goals"]        = p.get("goals", "")
    st.session_state["g_content_style"] = p.get("content_style", "")


def _load_reports_to_session(uid: int):
    db_reports = get_reports(uid)
    st.session_state["reports"] = {r["title"]: r["content"] for r in db_reports}


def _load_deals_to_session(uid: int):
    """Convert DB deal rows to the pandas-friendly dict format render_deals() expects."""
    from cip.ui import safe_float as _safe_float

    db_deals = get_deals(uid)
    deals = []
    for d in db_deals:
        deals.append({
            "_db_id":       d["id"],
            "Brand":        d["brand"],
            "Date":         d.get("campaign_date", ""),
            "Amount (₹)":  _safe_float(d.get("deal_value", 0)),
            "Engagement":   _safe_float(d.get("engagement", 0)),
            "Deliverables": d.get("deliverables", ""),
            "Status":       d.get("status", "Pending"),
            "Payment":      d.get("payment_status", d.get("status", "Pending")),
            "Notes":        d.get("notes", ""),
        })
    st.session_state["deals"] = deals
