"""Reusable UI components, navigation helpers, and persistence wrappers (presentation only)."""
import base64
import os
from contextlib import contextmanager
from urllib.parse import quote

import streamlit as st

from .ai import get_context


def logo_img(height: int = 36, cls: str = "") -> str:
    """Return an <img> tag with Logo.png embedded as base64, or SVG sparkles fallback."""
    try:
        logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Logo.png")
        with open(logo_path, "rb") as fh:
            b64 = base64.b64encode(fh.read()).decode()
        src = f"data:image/png;base64,{b64}"
    except Exception:
        src = ""
    if src:
        return f'<img src="{src}" alt="Muse" style="height:{height}px;width:auto;display:block;" class="{cls}" />'
    return icon("sparkles", height, "#fff")

# ── SVG Icon System (Heroicons outline, 24×24) ────────────────────────────────
_SVG_ICONS: dict[str, str] = {
    "home":      '<path d="m2.25 12 8.954-8.955c.44-.439 1.152-.439 1.591 0L21.75 12M4.5 9.75v10.125c0 .621.504 1.125 1.125 1.125H9.75v-4.875c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125V21h4.125c.621 0 1.125-.504 1.125-1.125V9.75M8.25 21h8.25"/>',
    "photo":     '<path d="M2.25 15.75l5.159-5.159a2.25 2.25 0 0 1 3.182 0l5.159 5.159m-1.5-1.5 1.409-1.409a2.25 2.25 0 0 1 3.182 0l2.909 2.909m-18 3.75h16.5a1.5 1.5 0 0 0 1.5-1.5V6a1.5 1.5 0 0 0-1.5-1.5H3.75A1.5 1.5 0 0 0 2.25 6v12a1.5 1.5 0 0 0 1.5 1.5Zm10.5-11.25h.008v.008h-.008V8.25Zm.375 0a.375.375 0 1 1-.75 0 .375.375 0 0 1 .75 0Z"/>',
    "pen":       '<path d="m16.862 4.487 1.687-1.688a1.875 1.875 0 1 1 2.652 2.652L10.582 16.07a4.5 4.5 0 0 1-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 0 1 1.13-1.897l8.932-8.931Zm0 0L19.5 7.125M18 14v4.75A2.25 2.25 0 0 1 15.75 21H5.25A2.25 2.25 0 0 1 3 18.75V8.25A2.25 2.25 0 0 1 5.25 6H10"/>',
    "shield":    '<path d="M9 12.75 11.25 15 15 9.75m-3-7.036A11.959 11.959 0 0 1 3.598 6 11.99 11.99 0 0 0 3 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285Z"/>',
    "trending":  '<path d="M2.25 18 9 11.25l4.306 4.306a11.95 11.95 0 0 1 5.814-5.518l2.74-1.22m0 0-5.94-2.281m5.94 2.28-2.28 5.941"/>',
    "link":      '<path d="M13.19 8.688a4.5 4.5 0 0 1 1.242 7.244l-4.5 4.5a4.5 4.5 0 0 1-6.364-6.364l1.757-1.757m13.35-.622 1.757-1.757a4.5 4.5 0 0 0-6.364-6.364l-4.5 4.5a4.5 4.5 0 0 0 1.242 7.244"/>',
    "sparkles":  '<path d="M9.813 15.904 9 18.75l-.813-2.846a4.5 4.5 0 0 0-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 0 0 3.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 0 0 3.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 0 0-3.09 3.09ZM18.259 8.715 18 9.75l-.259-1.035a3.375 3.375 0 0 0-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 0 0 2.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 0 0 2.456 2.456L21.75 6l-1.035.259a3.375 3.375 0 0 0-2.456 2.456ZM16.894 20.567 16.5 21.75l-.394-1.183a2.25 2.25 0 0 0-1.423-1.423L13.5 18.75l1.183-.394a2.25 2.25 0 0 0 1.423-1.423l.394-1.183.394 1.183a2.25 2.25 0 0 0 1.423 1.423l1.183.394-1.183.394a2.25 2.25 0 0 0-1.423 1.423Z"/>',
    "chart-pie": '<path d="M10.5 6a7.5 7.5 0 1 0 7.5 7.5h-7.5V6Z"/><path d="M13.5 10.5H21A7.5 7.5 0 0 0 13.5 3v7.5Z"/>',
    "chart-bar": '<path d="M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 1.125 1.125v6.75C7.5 20.496 6.996 21 6.375 21h-2.25A1.125 1.125 0 0 1 3 19.875v-6.75ZM9.75 8.625c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125v11.25c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 0 1-1.125-1.125V8.625ZM16.5 4.125c0-.621.504-1.125 1.125-1.125h2.25C20.496 3 21 3.504 21 4.125v15.75c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 0 1-1.125-1.125V4.125Z"/>',
    "currency":  '<path d="M12 6v12m-3-2.818.879.659c1.171.879 3.07.879 4.242 0 1.172-.879 1.172-2.303 0-3.182C13.536 12.219 12.768 12 12 12c-.725 0-1.45-.22-2.003-.659-1.106-.879-1.106-2.303 0-3.182s2.9-.879 4.006 0l.415.33M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z"/>',
    "heart":     '<path d="M21 8.25c0-2.485-2.099-4.5-4.688-4.5-1.935 0-3.597 1.126-4.312 2.733-.715-1.607-2.377-2.733-4.313-2.733C5.1 3.75 3 5.765 3 8.25c0 7.22 9 12 9 12s9-4.78 9-12Z"/>',
    "fire":      '<path d="M15.362 5.214A8.252 8.252 0 0 1 12 21 8.25 8.25 0 0 1 6.038 7.047 8.287 8.287 0 0 0 9 9.601a8.983 8.983 0 0 1 3.361-6.867 8.21 8.21 0 0 0 3 2.48Z"/><path d="M12 18a3.75 3.75 0 0 0 .495-7.468 5.99 5.99 0 0 0-1.925 3.547 5.975 5.975 0 0 1-2.133-1.001A3.75 3.75 0 0 0 12 18Z"/>',
    "user":      '<path d="M15.75 6a3.75 3.75 0 1 1-7.5 0 3.75 3.75 0 0 1 7.5 0ZM4.501 20.118a7.5 7.5 0 0 1 14.998 0A17.933 17.933 0 0 1 12 21.75c-2.676 0-5.216-.584-7.499-1.632Z"/>',
    "archive":   '<path d="m20.25 7.5-.625 10.632a2.25 2.25 0 0 1-2.247 2.118H6.622a2.25 2.25 0 0 1-2.247-2.118L3.75 7.5M10 11.25h4M3.375 7.5h17.25c.621 0 1.125-.504 1.125-1.125v-1.5c0-.621-.504-1.125-1.125-1.125H3.375c-.621 0-1.125.504-1.125 1.125v1.5c0 .621.504 1.125 1.125 1.125Z"/>',
    "sliders":   '<path d="M10.5 6h9.75M10.5 6a1.5 1.5 0 1 1-3 0m3 0a1.5 1.5 0 1 0-3 0M3.75 6H7.5m3 12h9.75m-9.75 0a1.5 1.5 0 0 1-3 0m3 0a1.5 1.5 0 0 0-3 0m-3.75 0H7.5m9-6h3.75m-3.75 0a1.5 1.5 0 0 1-3 0m3 0a1.5 1.5 0 0 0-3 0m-9.75 0h9.75"/>',
    "logout":    '<path d="M8.25 9V5.25A2.25 2.25 0 0 1 10.5 3h6a2.25 2.25 0 0 1 2.25 2.25v13.5A2.25 2.25 0 0 1 16.5 21h-6a2.25 2.25 0 0 1-2.25-2.25V15m-3 0-3-3m0 0 3-3m-3 3H15"/>',
    "x":         '<path d="M6 18 18 6M6 6l12 12"/>',
    "check":     '<path d="M4.5 12.75l6 6 9-13.5"/>',
    "arrow-r":   '<path d="M13.5 4.5 21 12m0 0-7.5 7.5M21 12H3"/>',
    "plus":      '<path d="M12 4.5v15m7.5-7.5h-15"/>',
}


def icon(name: str, size: int = 18, color: str = "currentColor", cls: str = "") -> str:
    """Return an inline SVG string for the named Heroicon."""
    content = _SVG_ICONS.get(name, _SVG_ICONS["x"])
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" '
        f'viewBox="0 0 24 24" fill="none" stroke="{color}" '
        f'stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" '
        f'style="display:inline-block;vertical-align:middle;flex-shrink:0" '
        f'class="ms-icon {cls}">{content}</svg>'
    )

# Grouped, creator-focused navigation.
# Each item is (icon, label, page_key); a group title of None renders ungrouped.
NAV_GROUPS = [
    (None, [
        ("home",     "Home",             "Dashboard"),
    ]),
    ("Create", [
        ("photo",    "Caption Magic",    "Caption Magic"),
        ("pen",      "Content Studio",   "Content Studio"),
        ("shield",   "Pre-Publish",      "Pre-Publish"),
    ]),
    ("Grow", [
        ("trending", "Growth Coach",     "Growth Coach"),
        ("link",     "Brand Match",      "Brand Match"),
    ]),
    ("Insights", [
        ("sparkles", "Brand DNA",        "Brand DNA"),
        ("chart-pie","Insights",         "Insights"),
    ]),
    ("Business", [
        ("currency", "Creator Earnings", "Creator Earnings"),
    ]),
    ("Care", [
        ("heart",    "Wellbeing",        "Wellbeing"),
    ]),
    ("Discover", [
        ("fire",     "Trends",           "Trends"),
    ]),
    ("Settings", [
        ("user",     "Profile",          "Profile"),
        ("archive",  "My Library",       "Library"),
        ("sliders",  "Settings",         "Settings"),
    ]),
]


def init_state():
    """Initialise session state (UI + shared stores). Safe to call multiple times."""
    st.session_state.setdefault("reports", {})
    st.session_state.setdefault("deals", [])
    st.session_state.setdefault("metrics", {})
    st.session_state.setdefault("page", "Dashboard")


# ── Safe parsing helpers (never crash on "" / None / bad input) ─────────────

def safe_float(value, default: float = 0.0) -> float:
    try:
        if value is None or (isinstance(value, str) and not value.strip()):
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def safe_first_name(name: str, fallback: str = "Creator") -> str:
    try:
        parts = (name or "").strip().split()
        return parts[0] if parts else fallback
    except Exception:
        return fallback


# ── Persistence helpers ──────────────────────────────────────────────────────

# Map report title → report_type label for the library
_REPORT_TYPES = {
    "Media Kit": "Brand DNA", "Content Plan": "Content", "Hook Generator": "Content",
    "Photo Caption Match": "Captions", "Pre-Publish Check": "Pre-Publish",
    "Growth Plan": "Growth", "Problem Solver": "Growth",
    "Brand Fit Check": "Brand", "Brand Reputation Check": "Brand",
    "Campaign Brief": "Brand", "Social Commerce": "Brand",
    "Deals & Revenue Summary": "Earnings",
    "Wellbeing Check-In": "Wellbeing", "Burnout Predictor": "Wellbeing",
    "Fake Audience Analysis": "Wellbeing", "Trends Hub": "Trends",
}


def store_report(title: str, content: str):
    """Write to session state AND persist to DB (if signed in)."""
    st.session_state.reports[title] = content
    user = st.session_state.get("user")
    if user and not user.get("is_guest"):
        from cip.database.db import save_report as _db_save
        rtype = _REPORT_TYPES.get(title, "General")
        _db_save(user["id"], rtype, title, content)


def store_deal(deal: dict):
    """Accept canonical DB-format keys, persist to DB, build clean display record."""
    user = st.session_state.get("user")
    db_id = None
    if user and not user.get("is_guest"):
        from cip.database.db import create_deal as _db_deal
        db_id = _db_deal(user["id"], deal)
    # Build pandas-friendly display record with no redundant DB internals
    display = {
        "_db_id":       db_id,
        "Brand":        deal.get("brand", ""),
        "Date":         deal.get("campaign_date", ""),
        "Amount (₹)":  safe_float(deal.get("deal_value", 0)),
        "Engagement":   safe_float(deal.get("engagement", 0)),
        "Deliverables": deal.get("deliverables", ""),
        "Status":       deal.get("status", "Pending"),
        "Payment":      deal.get("payment_status", deal.get("status", "Pending")),
        "Notes":        deal.get("notes", ""),
    }
    st.session_state.deals.append(display)


def delete_deal_by_idx(idx: int):
    """Remove deal from session state AND DB (if signed in)."""
    deals = st.session_state.deals
    if 0 <= idx < len(deals):
        user = st.session_state.get("user")
        if user and not user.get("is_guest"):
            db_id = deals[idx].get("_db_id")
            if db_id:
                from cip.database.db import delete_deal as _db_del
                _db_del(db_id, user["id"])
        deals.pop(idx)


def plan_gate(feature_name: str, required: str = "pro") -> bool:
    """Soft subscription gate. Shows an upgrade banner and returns False if access denied."""
    user = st.session_state.get("user")
    plan = user.get("plan", "free") if user else "free"
    rank = {"free": 0, "pro": 1, "agency": 2}
    if rank.get(plan, 0) >= rank.get(required, 1):
        return True
    label = required.title()
    st.markdown(
        f'<div class="ms-plan-gate">'
        f'<span class="ms-plan-lock">🔒 {label}</span> '
        f'<strong>{feature_name}</strong> is available on the <strong>{label}</strong> plan. '
        f'<a href="?go=Settings" target="_self">Upgrade now →</a>'
        f'</div>',
        unsafe_allow_html=True,
    )
    return False


def go_to(page):
    """Navigate to a page and rerun."""
    st.session_state.page = page
    st.rerun()


def nav_href(page):
    """Build a query-param link used by clickable HTML cards."""
    return f"?go={quote(page)}"


# ── Shared widgets (unchanged behaviour from original) ──────────────────────────
def download_and_copy(label, md_content, filename):
    col1, col2 = st.columns([2, 3])
    with col1:
        st.download_button(
            f"⬇️ Download {label} (.md)",
            md_content,
            file_name=filename,
            mime="text/markdown",
        )
    with col2:
        with st.expander("📋 Copy to clipboard"):
            st.code(md_content, language="markdown")


def context_warning():
    """Show a warning if global context is empty."""
    if not get_context():
        st.info("💡 Add your recent posts in Settings → Profile for more personalised results.")


# ── Premium presentation primitives ─────────────────────────────────────────────
def hero(eyebrow, title, subtitle, pillars):
    pill_html = "".join(f'<span class="pill">{p}</span>' for p in pillars)
    st.markdown(
        f'<div class="cip-hero">'
        f'<span class="eyebrow">{eyebrow}</span>'
        f'<h1>{title}</h1>'
        f'<p class="sub">{subtitle}</p>'
        f'<div class="pillars">{pill_html}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


def section_label(text):
    st.markdown(f'<div class="cip-section-label">{text}</div>', unsafe_allow_html=True)


def module_header(icon, title, subtitle):
    st.markdown(
        f'<div class="cip-module-head">'
        f'<div class="cip-module-icon">{icon}</div>'
        f'<div><div class="cip-module-title">{title}</div>'
        f'<div class="cip-module-sub">{subtitle}</div></div></div>',
        unsafe_allow_html=True,
    )


def metric_card(icon, label, value, sub, tone="neutral"):
    tone_cls = {"good": "tone-good", "warn": "tone-warn", "bad": "tone-bad"}.get(tone, "")
    bar_cls = {
        "good": "bar-good", "warn": "bar-warn", "bad": "bar-bad", "accent": "bar-accent"
    }.get(tone, "bar-neutral")
    st.markdown(
        f'<div class="cip-metric"><div class="bar {bar_cls}"></div>'
        f'<div class="m-top"><span class="m-ico">{icon}</span>'
        f'<span class="m-label">{label}</span></div>'
        f'<div class="m-value {tone_cls}">{value}</div>'
        f'<div class="m-sub">{sub}</div></div>',
        unsafe_allow_html=True,
    )


@contextmanager
def module(icon, title, subtitle):
    """Render a module header, then yield inside a styled card container."""
    module_header(icon, title, subtitle)
    with st.container(border=True):
        yield


# ══════════════════════════════════════════════════════════════════════════════
# PER-MODULE VISUAL IDENTITY
# Each page gets a unique icon, accent, hero, and empty state. Presentation only.
# ══════════════════════════════════════════════════════════════════════════════
MODULE_THEMES = {
    "Brand DNA": dict(
        icon="🧬", accent="#FF5FA2", accent2="#FF9EC9", text="light",
        hero="linear-gradient(135deg,#FF7EB6 0%,#FF8FBF 45%,#FFB39C 110%)",
        eyebrow="Your creator identity",
        subtitle="A one-page snapshot of who you are — for brand pitches and self-reflection.",
        empty_title="Let's uncover your Brand DNA ✨",
        empty_text="Add a few recent posts in your profile, then generate a media kit that captures your voice, niche, and audience.",
        intro=True, done_keys=["Media Kit"],
    ),
    "Content Studio": dict(
        icon="✍️", accent="#F2890B", accent2="#FBC04A", text="light",
        hero="linear-gradient(135deg,#FF9A4D 0%,#F9A826 55%,#FFD36E 120%)",
        eyebrow="Create in your voice",
        subtitle="Captions, reel hooks, titles, CTAs, and a 7-day calendar — all in your voice.",
        empty_title="Ready to create something 🧡",
        empty_text="Pick a tab and Muse will draft content that sounds just like you.",
        intro=True, done_keys=["Content Plan", "Hook Generator"],
    ),
    "Caption Magic": dict(
        icon="📸", accent="#8B5CF6", accent2="#C4B5FD", text="light",
        hero="linear-gradient(135deg,#A78BFA 0%,#8B5CF6 55%,#C4B5FD 120%)",
        eyebrow="Photo to post in seconds",
        subtitle="Upload a photo and get matching captions, hashtags, trending songs, and reel ideas.",
        empty_title="Drop a photo, get magic 💜",
        empty_text="Upload any photo and we'll match it with captions, hashtags, and trending sounds.",
        intro=True, done_keys=["Photo Caption Match"],
    ),
    "Pre-Publish": dict(
        icon="🛡️", accent="#FB5E78", accent2="#FDA4AF", text="light", title="Pre-Publish Checker",
        hero="linear-gradient(135deg,#FB7185 0%,#F43F5E 55%,#FDA4AF 120%)",
        eyebrow="Post with confidence",
        subtitle="Check virality, engagement, brand safety, fact-checks, and copyright before you post.",
        empty_title="Check before you post 🛡️",
        empty_text="Paste a draft and get a virality, engagement, and brand-safety read in seconds.",
        intro=True, done_keys=["Pre-Publish Check"],
    ),
    "Growth Coach": dict(
        icon="📈", accent="#0EA371", accent2="#6EE7B7", text="light",
        hero="linear-gradient(135deg,#34D399 0%,#10B981 55%,#86EFAC 120%)",
        eyebrow="Grow with a plan",
        subtitle="A 30-day growth plan, a problem solver, and an on-demand AI coach.",
        empty_title="Let's map your growth 🌱",
        empty_text="Get a personalised 30-day roadmap, fixes for what's stuck, and answers whenever you need them.",
        intro=True, done_keys=["Growth Plan", "Problem Solver"],
    ),
    "Brand Match": dict(
        icon="🤝", accent="#B8902A", accent2="#F4D77E", text="dark",
        hero="linear-gradient(135deg,#E6B450 0%,#D4AF37 50%,#F4D77E 120%)",
        eyebrow="Premium partnerships",
        subtitle="Brand fit, reputation checks, campaign briefs, and social commerce.",
        empty_title="Find your perfect brand fit 🤝",
        empty_text="Paste a brand brief to score the fit, vet their reputation, and craft your pitch.",
        intro=True, done_keys=["Brand Fit Check", "Brand Reputation Check", "Campaign Brief", "Social Commerce"],
    ),
    "Creator Earnings": dict(
        icon="💰", accent="#047857", accent2="#34D399", text="light",
        hero="linear-gradient(135deg,#059669 0%,#10B981 55%,#34D399 120%)",
        eyebrow="Know your numbers",
        subtitle="Track every brand deal — revenue, engagement, and trends. Stays in this session only.",
        empty_title="Start tracking your income 💚",
        empty_text="Log your first brand deal and watch your revenue, engagement, and trends come to life.",
    ),
    "Wellbeing": dict(
        icon="💖", accent="#EC6FA9", accent2="#FFC4DD", text="dark",
        hero="linear-gradient(135deg,#FFC4DD 0%,#FFB3D1 55%,#FFD9C7 120%)",
        eyebrow="Create sustainably",
        subtitle="Gentle check-ins, burnout prediction, and audience-authenticity analysis.",
        empty_title="Take a gentle moment 💗",
        empty_text="A supportive check-in on burnout, negativity, and sustainable routines — whenever you need it.",
        intro=True, done_keys=["Wellbeing Check-In", "Burnout Predictor", "Fake Audience Analysis"],
    ),
    "Trends": dict(
        icon="🔥", accent="#FF4D6D", accent2="#FFC24B", text="light",
        hero="linear-gradient(120deg,#FF5F8F 0%,#FF8A5B 45%,#FFC24B 100%)",
        eyebrow="What's hot right now",
        subtitle="Latest trending topics, sounds, buzzing creators, and platform news — on demand.",
        empty_title="Catch the wave 🔥",
        empty_text="Pull a fresh briefing on trending topics, sounds, and creators in your niche.",
    ),
    "Insights": dict(
        icon="📊", accent="#6E5A86", accent2="#A99BC0", text="light",
        hero="linear-gradient(135deg,#4A3B63 0%,#2D1B3D 70%,#5B4B7A 120%)",
        eyebrow="Your executive summary",
        subtitle="Everything you've created this session, combined into one shareable document.",
        empty_title="Your insights, all in one place 📊",
        empty_text="Create with any tool and your reports gather here as a polished, shareable summary.",
    ),
    "Profile": dict(
        icon="⚙️", accent="#7C6A86", accent2="#B0A2BC", text="light", title="Your Profile",
        hero="linear-gradient(135deg,#8B7A98 0%,#7C6A86 60%,#A99BB6 120%)",
        eyebrow="Make Muse yours",
        subtitle="Tell Muse about you once — every tool personalises around it.",
    ),
    "Library": dict(
        icon="📚", accent="#6E5A86", accent2="#A99BC0", text="light", title="My Library",
        hero="linear-gradient(135deg,#4A3B63 0%,#6E5A86 55%,#A99BC0 120%)",
        eyebrow="Your creative archive",
        subtitle="Every report, caption set, and plan you've ever created — saved, searchable, and downloadable.",
    ),
    "Settings": dict(
        icon="🔧", accent="#7C6A86", accent2="#B0A2BC", text="light", title="Settings",
        hero="linear-gradient(135deg,#8B7A98 0%,#7C6A86 60%,#A99BB6 120%)",
        eyebrow="Account & workspace",
        subtitle="Manage your account, upgrade your plan, and control your data.",
    ),
}


def _hex_to_rgba(hex_color, alpha):
    try:
        h = (hex_color or "").lstrip("#")
        if len(h) == 3:
            h = "".join(c * 2 for c in h)
        if len(h) != 6:
            return f"rgba(255,126,182,{alpha})"
        r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        return f"rgba({r},{g},{b},{alpha})"
    except Exception:
        return f"rgba(255,126,182,{alpha})"


def apply_module_theme(theme):
    """Inject per-page accent variables so native CTAs/tabs adopt the module color."""
    accent = theme.get("accent")
    if not accent:
        return
    accent2 = theme.get("accent2", accent)
    st.markdown(
        f"<style>:root{{--ms-mod:{accent};"
        f"--ms-mod-grad:linear-gradient(135deg,{accent},{accent2});}}</style>",
        unsafe_allow_html=True,
    )


def module_hero(key, theme):
    text = theme.get("text", "light")
    st.markdown(
        f'<div class="ms-mhero {text}" style="background:{theme.get("hero")}">'
        f'<span class="eyebrow">{theme.get("eyebrow", "")}</span>'
        f'<div class="row"><div class="icon">{theme.get("icon", "✨")}</div>'
        f'<div><div class="title">{theme.get("title", key)}</div>'
        f'<div class="sub">{theme.get("subtitle", "")}</div></div></div>'
        f'</div>',
        unsafe_allow_html=True,
    )


def module_empty(key, theme=None):
    """Render a themed, on-brand empty state for a module."""
    theme = theme or MODULE_THEMES.get(key, {})
    accent = theme.get("accent", "#FF7EB6")
    accent2 = theme.get("accent2", accent)
    bg = f"linear-gradient(135deg,{_hex_to_rgba(accent, 0.12)},{_hex_to_rgba(accent2, 0.07)})"
    border = _hex_to_rgba(accent, 0.40)
    bubble = f"linear-gradient(135deg,{_hex_to_rgba(accent, 0.24)},{_hex_to_rgba(accent2, 0.16)})"
    st.markdown(
        f'<div class="ms-empty" style="background:{bg};border:1px dashed {border}">'
        f'<div class="bubble" style="background:{bubble}">{theme.get("icon", "✨")}</div>'
        f'<div class="txt">'
        f'<div class="et">{theme.get("empty_title", "")}</div>'
        f'<p>{theme.get("empty_text", "")}</p></div></div>',
        unsafe_allow_html=True,
    )


@contextmanager
def module_page(key):
    """Themed module shell: per-page accent, custom hero, card container, empty state."""
    theme = MODULE_THEMES.get(key, {})
    apply_module_theme(theme)
    module_hero(key, theme)
    with st.container(border=True):
        if theme.get("intro"):
            reports = st.session_state.get("reports", {})
            if not any(k in reports for k in theme.get("done_keys", [])):
                module_empty(key, theme)
        yield
