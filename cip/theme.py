"""Muse — central design system.

A single source of truth for the brand's look & feel. Design tokens (COLORS,
SPACING, RADII, SHADOWS, TYPOGRAPHY) are defined in Python and compiled into CSS
custom properties, then consumed by every component via `var(--ms-*)`.

Warm · creative · premium · friendly · creator-first.
Presentation only — no business logic here.
"""
import streamlit as st

# ── BRAND ───────────────────────────────────────────────────────────────────
BRAND_NAME = "Muse"
BRAND_TAGLINE = "Your Creative Growth Companion"

# ── COLORS ──────────────────────────────────────────────────────────────────
COLORS = {
    "primary": "#FF7EB6",          # rosy pink
    "secondary": "#FFB3D1",        # soft blush
    "accent": "#F9A826",           # warm amber
    "bg": "#FFF8F3",               # warm cream
    "surface": "#FFFFFF",          # cards
    "surface-2": "#FFF1EC",        # peachy tint
    "text": "#2D1B3D",             # deep plum
    "muted": "#7C6A86",            # muted mauve
    "success": "#7BC47F",          # soft green
    "danger": "#EC5F73",           # warm coral
    "border": "rgba(45,27,61,0.07)",
    "border-strong": "rgba(45,27,61,0.12)",
}

# ── SPACING (px) ──────────────────────────────────────────────────────────────
SPACING = {"xs": 6, "sm": 10, "md": 18, "lg": 28, "xl": 44, "2xl": 64}

# ── RADII (px) ────────────────────────────────────────────────────────────────
RADII = {"sm": 14, "md": 20, "lg": 28, "xl": 36, "pill": 999}

# ── SHADOWS (warm, soft) ──────────────────────────────────────────────────────
SHADOWS = {
    "soft": "0 6px 22px -12px rgba(45,27,61,0.16)",
    "card": "0 16px 44px -22px rgba(45,27,61,0.22)",
    "glow": "0 16px 38px -16px rgba(255,126,182,0.55)",
    "amber": "0 16px 38px -18px rgba(249,168,38,0.45)",
}

# ── TYPOGRAPHY ────────────────────────────────────────────────────────────────
TYPOGRAPHY = {
    "body": "'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
    "display": "'Fraunces', 'Plus Jakarta Sans', Georgia, serif",
}


def _root_vars():
    parts = []
    for k, v in COLORS.items():
        parts.append(f"--ms-{k}:{v};")
    for k, v in RADII.items():
        parts.append(f"--ms-r-{k}:{v}px;")
    for k, v in SPACING.items():
        parts.append(f"--ms-sp-{k}:{v}px;")
    for k, v in SHADOWS.items():
        parts.append(f"--ms-shadow-{k}:{v};")
    parts.append(f"--ms-font-body:{TYPOGRAPHY['body']};")
    parts.append(f"--ms-font-display:{TYPOGRAPHY['display']};")
    return ":root{" + "".join(parts) + "}"


_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Fraunces:opsz,wght@9..144,500;9..144,600;9..144,700&display=swap');

html, body, [class*="css"], .stApp, section[data-testid="stSidebar"], input, textarea, button, select {
    font-family: var(--ms-font-body);
}

.stApp {
    background:
        radial-gradient(1200px 600px at 8% -10%, rgba(255,179,209,0.45), transparent 55%),
        radial-gradient(1000px 560px at 100% 0%, rgba(249,168,38,0.18), transparent 50%),
        radial-gradient(900px 700px at 50% 120%, rgba(255,126,182,0.16), transparent 55%),
        var(--ms-bg);
    color: var(--ms-text);
}

.block-container {
    padding-top: 2.1rem;
    padding-bottom: 3.5rem;
    max-width: 1200px;
}

/* Headings */
h1, h2, h3, h4 { color: var(--ms-text); letter-spacing: -0.01em; font-weight: 700; }
.stApp p, .stApp li, .stApp label, .stMarkdown { color: var(--ms-text); }
.stApp a { color: var(--ms-primary); }
.stCaption, [data-testid="stCaptionContainer"], .stApp small { color: var(--ms-muted) !important; }

/* ── Hero ── */
.cip-hero {
    border-radius: var(--ms-r-xl);
    padding: 46px 48px;
    background: linear-gradient(135deg, #FF8FBF 0%, #FF7EB6 38%, #FFA26B 92%, #F9A826 120%);
    box-shadow: var(--ms-shadow-glow);
    margin-bottom: 30px;
    position: relative;
    overflow: hidden;
}
.cip-hero::after {
    content: ""; position: absolute; right: -60px; top: -60px;
    width: 260px; height: 260px; border-radius: 50%;
    background: radial-gradient(circle, rgba(255,255,255,0.35), transparent 70%);
}
.cip-hero .eyebrow {
    display: inline-block; font-size: 12.5px; font-weight: 700; letter-spacing: 0.12em;
    text-transform: uppercase; color: #fff;
    background: rgba(255,255,255,0.22); border: 1px solid rgba(255,255,255,0.45);
    padding: 6px 14px; border-radius: var(--ms-r-pill); margin-bottom: 18px;
    backdrop-filter: blur(4px);
}
.cip-hero h1 {
    font-family: var(--ms-font-display);
    font-size: 3.4rem; font-weight: 600; margin: 0 0 8px 0; line-height: 1.02; color: #fff;
    letter-spacing: -0.01em;
}
.cip-hero .sub { color: rgba(255,255,255,0.94); font-size: 1.12rem; margin: 0 0 18px 0; max-width: 640px; }
.cip-hero .pillars { display: flex; flex-wrap: wrap; gap: 9px; }
.cip-hero .pill {
    font-size: 13px; font-weight: 600; color: #fff; background: rgba(255,255,255,0.18);
    border: 1px solid rgba(255,255,255,0.35); padding: 7px 14px; border-radius: var(--ms-r-pill);
}

/* ── Section label (Level 2) ── */
.cip-section-label {
    font-size: 12px; font-weight: 700; letter-spacing: 0.14em; text-transform: uppercase;
    color: var(--ms-muted); margin: 26px 0 14px 4px;
}

/* ── Module header (Level 3) ── */
.cip-module-head { display: flex; align-items: center; gap: 16px; margin: 6px 0 20px 0; }
.cip-module-icon {
    width: 54px; height: 54px; display: grid; place-items: center; font-size: 26px;
    border-radius: var(--ms-r-md);
    background: linear-gradient(135deg, rgba(255,126,182,0.22), rgba(249,168,38,0.20));
    box-shadow: var(--ms-shadow-soft); flex: 0 0 auto;
}
.cip-module-title { font-family: var(--ms-font-display); font-size: 1.75rem; font-weight: 600; line-height: 1.12; color: var(--ms-text); }
.cip-module-sub { font-size: 0.98rem; color: var(--ms-muted); margin-top: 3px; }

/* ── Mood tiles (warm, creative — not analytics cards) ── */
.cip-metric {
    position: relative; overflow: hidden;
    border-radius: var(--ms-r-lg);
    padding: 20px 20px 18px;
    background: linear-gradient(160deg, #FFFFFF 0%, var(--ms-surface-2) 130%);
    box-shadow: var(--ms-shadow-soft);
    border: 1px solid var(--ms-border);
    transition: transform .22s cubic-bezier(.34,1.4,.64,1), box-shadow .22s ease;
    height: 100%;
}
.cip-metric::after {
    content: ""; position: absolute; right: -28px; bottom: -34px; width: 110px; height: 110px;
    border-radius: 50%; background: radial-gradient(circle, rgba(255,126,182,0.12), transparent 70%);
    pointer-events: none;
}
.cip-metric:hover { transform: translateY(-5px); box-shadow: var(--ms-shadow-glow); }
/* the old analytics indicator bar is retired in favour of an emoji bubble */
.cip-metric .bar { display: none; }
.cip-metric .m-top { display: flex; flex-direction: column; align-items: flex-start; gap: 12px; }
.cip-metric .m-ico {
    width: 48px; height: 48px; border-radius: 50%; display: grid; place-items: center;
    font-size: 25px; line-height: 1;
    background: linear-gradient(135deg, rgba(255,126,182,0.20), rgba(249,168,38,0.18));
    box-shadow: inset 0 0 0 1px rgba(255,255,255,0.6);
}
.cip-metric .m-label {
    order: 2; font-size: 11.5px; font-weight: 700; color: var(--ms-muted);
    letter-spacing: 0.10em; text-transform: uppercase;
}
.cip-metric .m-value {
    font-family: var(--ms-font-display); font-size: 1.5rem; font-weight: 600;
    margin-top: 12px; line-height: 1.1; color: var(--ms-text) !important;
}
.cip-metric .m-sub { font-size: 12.5px; color: var(--ms-muted); margin-top: 7px; }
/* tone classes kept for compatibility but kept gentle inside mood tiles */
.tone-good { color: var(--ms-success); }
.tone-warn { color: var(--ms-accent); }
.tone-bad  { color: var(--ms-danger); }
.bar-good, .bar-warn, .bar-bad, .bar-accent, .bar-neutral { background: var(--ms-secondary); }

/* ── Module container cards ── */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background: var(--ms-surface);
    border: 1px solid var(--ms-border) !important;
    border-radius: var(--ms-r-xl) !important;
    box-shadow: var(--ms-shadow-card);
    padding: 18px 24px;
    transition: box-shadow .25s ease;
}
div[data-testid="stVerticalBlockBorderWrapper"]:hover { box-shadow: var(--ms-shadow-glow); }

/* ── Native metric widget ── */
div[data-testid="stMetric"] {
    background: linear-gradient(160deg, #FFFFFF 0%, var(--ms-surface-2) 130%);
    border: 1px solid var(--ms-border);
    border-radius: var(--ms-r-lg);
    padding: 18px 20px;
    box-shadow: var(--ms-shadow-soft);
}
div[data-testid="stMetricLabel"] p { color: var(--ms-muted) !important; font-weight: 700; letter-spacing: 0.04em; }
div[data-testid="stMetricValue"] { font-family: var(--ms-font-display); font-weight: 600; color: var(--ms-text); }

/* ── Buttons ── */
.stButton > button, .stDownloadButton > button {
    border-radius: var(--ms-r-pill); font-weight: 600; border: 1px solid var(--ms-border-strong);
    background: var(--ms-surface); color: var(--ms-text);
    padding: 9px 20px;
    transition: transform .14s ease, box-shadow .18s ease, filter .18s ease;
    box-shadow: var(--ms-shadow-soft);
}
.stButton > button:hover, .stDownloadButton > button:hover {
    transform: translateY(-2px); color: var(--ms-text); border-color: var(--ms-secondary);
}
.stButton > button[kind="primary"], .stDownloadButton > button[kind="primary"],
.stForm [data-testid="stFormSubmitButton"] button {
    background: var(--ms-mod-grad, linear-gradient(135deg, var(--ms-primary), var(--ms-accent)));
    border: none; color: #fff; box-shadow: var(--ms-shadow-glow);
}
.stButton > button[kind="primary"]:hover, .stDownloadButton > button[kind="primary"]:hover,
.stForm [data-testid="stFormSubmitButton"] button:hover { filter: brightness(1.04); color: #fff; }

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #FFFFFF 0%, #FFF5EF 100%);
    border-right: 1px solid var(--ms-border);
}
section[data-testid="stSidebar"] .block-container { padding-top: 1.4rem; }
.cip-brand { display: flex; align-items: center; gap: 13px; padding: 4px 2px 6px; }
.cip-brand .logo {
    display: flex; align-items: center; justify-content: center;
    flex: 0 0 auto;
}
.cip-brand .name { font-family: var(--ms-font-display); font-weight: 600; font-size: 1.32rem; line-height: 1.05; color: var(--ms-text); }
.cip-brand .tag { font-size: 11.5px; color: var(--ms-muted); letter-spacing: 0.02em; margin-top: 2px; }

/* Sidebar nav group labels */
.ms-navgroup {
    font-size: 11px; font-weight: 700; letter-spacing: 0.16em; text-transform: uppercase;
    color: var(--ms-muted); opacity: 0.65; margin: 20px 0 6px 14px;
}
.ms-navgroup:first-of-type { margin-top: 6px; }
section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] { gap: 0.35rem; }
section[data-testid="stSidebar"] hr { margin: 14px 0; border-color: var(--ms-border); }

/* Sidebar nav buttons */
section[data-testid="stSidebar"] .stButton > button {
    justify-content: flex-start; text-align: left; width: 100%;
    background: transparent; border: 1px solid transparent; color: var(--ms-muted);
    font-weight: 600; padding: 10px 14px; box-shadow: none; border-radius: var(--ms-r-md);
}
section[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(255,126,182,0.10); color: var(--ms-text); transform: translateX(3px);
    border-color: transparent;
}
section[data-testid="stSidebar"] .stButton > button[kind="primary"] {
    background: linear-gradient(135deg, rgba(255,126,182,0.20), rgba(249,168,38,0.16));
    color: var(--ms-text); border: 1px solid rgba(255,126,182,0.35); box-shadow: none;
}

/* Sub-tabs inside modules */
.stTabs [data-baseweb="tab-list"] { gap: 6px; border-bottom: 1px solid var(--ms-border); }
.stTabs [data-baseweb="tab"] {
    border-radius: var(--ms-r-sm) var(--ms-r-sm) 0 0; padding: 8px 16px; color: var(--ms-muted);
}
.stTabs [aria-selected="true"] { color: var(--ms-mod, var(--ms-primary)) !important; }
.stTabs [data-baseweb="tab-highlight"] { background: var(--ms-mod, var(--ms-primary)); }

/* Inputs */
.stTextInput input, .stTextArea textarea, .stNumberInput input, .stDateInput input,
div[data-baseweb="select"] > div {
    border-radius: var(--ms-r-sm) !important; background: var(--ms-surface) !important;
    border-color: var(--ms-border-strong) !important;
}
.stTextInput input:focus, .stTextArea textarea:focus { border-color: var(--ms-primary) !important; }

/* Alerts → softer, warmer */
div[data-testid="stAlert"] { border-radius: var(--ms-r-md); border: none; }

/* Expander */
details, .streamlit-expanderHeader { border-radius: var(--ms-r-md) !important; }

/* Dataframe */
div[data-testid="stDataFrame"] { border-radius: var(--ms-r-md); overflow: hidden; }

/* ── Dashboard: greeting hero ── */
.ms-greet {
    border-radius: var(--ms-r-xl); padding: 44px 48px; margin-bottom: 28px;
    background: linear-gradient(135deg, #FFF0E6 0%, #FFE6F0 55%, #FFEFD9 100%);
    border: 1px solid var(--ms-border); box-shadow: var(--ms-shadow-soft);
    position: relative; overflow: hidden;
}
.ms-greet::after {
    content: ""; position: absolute; right: -40px; top: -50px; width: 230px; height: 230px;
    border-radius: 50%; background: radial-gradient(circle, rgba(255,126,182,0.22), transparent 70%);
}
.ms-greet .brand { font-family: var(--ms-font-display); font-weight: 700; color: var(--ms-primary); font-size: 1rem; margin-bottom: 10px; }
.ms-greet h1 { font-family: var(--ms-font-display); font-weight: 600; font-size: 2.7rem; line-height: 1.04; color: var(--ms-text); margin: 0 0 10px 0; }
.ms-greet p { color: var(--ms-muted); font-size: 1.08rem; margin: 0; max-width: 580px; }

/* ── Dashboard: quick-action cards (div + st.button below) ── */
.ms-action {
    display: flex; flex-direction: column;
    background: var(--ms-surface); border: 1px solid var(--ms-border); border-radius: var(--ms-r-lg);
    padding: 20px 18px 10px; box-shadow: var(--ms-shadow-soft);
    transition: transform .2s ease, box-shadow .2s ease, border-color .2s ease;
    margin-bottom: -4px;
}
.ms-action:hover { transform: translateY(-2px); box-shadow: var(--ms-shadow-card); border-color: var(--ms-secondary); }
.ms-action .ic {
    width: 50px; height: 50px; border-radius: var(--ms-r-md); display: grid; place-items: center;
    margin-bottom: 14px;
    background: linear-gradient(135deg, rgba(255,126,182,0.18), rgba(249,168,38,0.14));
}
.ms-action .ttl { font-weight: 700; font-size: 1rem; color: var(--ms-text); }
.ms-action .desc { color: var(--ms-muted); font-size: 12px; margin-top: 5px; flex: 1; line-height: 1.4; }

/* ── Dashboard: continue working cards (div + st.button below) ── */
.ms-recent-card {
    display: flex; align-items: center; gap: 12px;
    background: var(--ms-surface); border: 1px solid var(--ms-border); border-radius: var(--ms-r-md);
    padding: 14px 14px 8px; box-shadow: var(--ms-shadow-soft); margin-bottom: -4px;
}
.ms-recent-card .ic {
    width: 38px; height: 38px; border-radius: var(--ms-r-sm); display: grid; place-items: center;
    flex: 0 0 auto;
    background: linear-gradient(135deg, rgba(255,126,182,0.14), rgba(249,168,38,0.12));
}
.ms-recent-card .nm { font-weight: 600; font-size: .92rem; color: var(--ms-text); }

/* ── Dashboard: onboarding empty states ── */
.ms-onboard {
    border-radius: var(--ms-r-lg); padding: 30px 32px; margin-bottom: 24px;
    background: linear-gradient(135deg, rgba(255,126,182,0.12), rgba(249,168,38,0.12));
    border: 1px dashed rgba(255,126,182,0.45);
}
.ms-onboard .big { font-family: var(--ms-font-display); font-weight: 600; font-size: 1.45rem; color: var(--ms-text); margin-bottom: 6px; }
.ms-onboard p { color: var(--ms-muted); font-size: 1rem; margin: 0 0 18px 0; max-width: 580px; }
.ms-onboard .cta {
    display: inline-block; text-decoration: none !important; color: #fff !important; font-weight: 700; font-size: 14px;
    background: linear-gradient(135deg, var(--ms-primary), var(--ms-accent));
    padding: 12px 24px; border-radius: var(--ms-r-pill); box-shadow: var(--ms-shadow-glow);
}
.ms-onboard.soft { background: var(--ms-surface); border: 1px dashed var(--ms-border-strong); text-align: center; }
.ms-onboard.soft p { margin-left: auto; margin-right: auto; margin-bottom: 0; }

/* ── Per-module themed hero ── */
.ms-mhero {
    border-radius: var(--ms-r-xl); padding: 30px 34px; margin-bottom: 20px;
    box-shadow: var(--ms-shadow-soft); position: relative; overflow: hidden;
}
.ms-mhero::after {
    content: ""; position: absolute; right: -50px; top: -55px; width: 220px; height: 220px;
    border-radius: 50%; background: radial-gradient(circle, rgba(255,255,255,0.30), transparent 70%);
}
.ms-mhero .eyebrow {
    display: inline-block; font-size: 11.5px; font-weight: 700; letter-spacing: 0.12em;
    text-transform: uppercase; padding: 5px 13px; border-radius: var(--ms-r-pill); margin-bottom: 16px;
}
.ms-mhero .row { display: flex; align-items: center; gap: 16px; }
.ms-mhero .icon {
    width: 58px; height: 58px; border-radius: var(--ms-r-md); display: grid; place-items: center;
    font-size: 29px; flex: 0 0 auto;
}
.ms-mhero .title { font-family: var(--ms-font-display); font-weight: 600; font-size: 1.95rem; line-height: 1.06; }
.ms-mhero .sub { font-size: 0.98rem; opacity: 0.94; margin-top: 4px; max-width: 660px; }
.ms-mhero .icon { transition: transform .3s cubic-bezier(.34,1.56,.64,1); }
.ms-mhero:hover .icon { transform: rotate(-7deg) scale(1.08); }
.ms-mhero.light { color: #fff; }
.ms-mhero.light .eyebrow { background: rgba(255,255,255,0.22); border: 1px solid rgba(255,255,255,0.45); color: #fff; }
.ms-mhero.light .icon { background: rgba(255,255,255,0.20); border: 1px solid rgba(255,255,255,0.42); }
.ms-mhero.dark { color: var(--ms-text); }
.ms-mhero.dark::after { background: radial-gradient(circle, rgba(255,255,255,0.45), transparent 70%); }
.ms-mhero.dark .eyebrow { background: rgba(45,27,61,0.10); border: 1px solid rgba(45,27,61,0.16); color: var(--ms-text); }
.ms-mhero.dark .icon { background: rgba(45,27,61,0.10); border: 1px solid rgba(45,27,61,0.16); }

/* ── Per-module themed empty state (with illustration bubble) ── */
.ms-empty {
    display: flex; align-items: center; gap: 20px;
    border-radius: var(--ms-r-lg); padding: 24px 28px; margin-bottom: 18px;
}
.ms-empty .bubble {
    width: 66px; height: 66px; border-radius: 50%; display: grid; place-items: center;
    font-size: 32px; flex: 0 0 auto; box-shadow: var(--ms-shadow-soft);
    transition: transform .3s cubic-bezier(.34,1.56,.64,1);
}
.ms-empty:hover .bubble { transform: scale(1.08) rotate(-6deg); }
.ms-empty .txt { flex: 1; }
.ms-empty .et { font-family: var(--ms-font-display); font-weight: 600; font-size: 1.25rem; color: var(--ms-text); margin-bottom: 4px; }
.ms-empty p { color: var(--ms-muted); font-size: 0.98rem; margin: 0; max-width: 600px; }

/* ══ PREMIUM POLISH ══════════════════════════════════════════════════════════ */

/* Smooth transitions on interactive surfaces */
.stButton > button, .stDownloadButton > button, a, input, textarea, select,
.stTabs [data-baseweb="tab"], .cip-metric, .ms-action, .ms-recent-card, .cip-brand .logo {
    transition: transform .18s ease, box-shadow .2s ease, background .2s ease,
                border-color .2s ease, color .2s ease, filter .2s ease;
}

/* Button press + focus ring (premium tactile feel) */
.stButton > button:active, .stDownloadButton > button:active,
.stForm [data-testid="stFormSubmitButton"] button:active { transform: translateY(0) scale(.985); }
.stButton > button:focus-visible, .stDownloadButton > button:focus-visible {
    outline: none; box-shadow: 0 0 0 3px rgba(255,126,182,0.32);
}
.stButton > button[kind="primary"]:hover, .stDownloadButton > button[kind="primary"]:hover {
    box-shadow: var(--ms-shadow-glow), 0 14px 30px -12px rgba(45,27,61,0.30);
}

/* Input focus glow in the active module accent */
.stTextInput input:focus, .stTextArea textarea:focus, .stNumberInput input:focus {
    box-shadow: 0 0 0 3px rgba(255,126,182,0.16) !important;
    border-color: var(--ms-mod, var(--ms-primary)) !important;
}
div[data-baseweb="select"]:focus-within > div {
    box-shadow: 0 0 0 3px rgba(255,126,182,0.16) !important;
    border-color: var(--ms-mod, var(--ms-primary)) !important;
}

/* Dashboard card micro-interactions */
.ms-recent-card .ic { transition: transform .2s ease; }

/* Report / markdown typography — editorial & consistent */
.stMarkdown h2 { font-size: 1.4rem; font-weight: 700; margin: 1.5rem 0 .6rem; }
.stMarkdown h3 { font-size: 1.12rem; font-weight: 700; margin: 1.15rem 0 .45rem; }
.stMarkdown h4 { font-size: 1rem; font-weight: 700; margin: 1rem 0 .35rem; color: var(--ms-muted); }
.stMarkdown p, .stMarkdown li { line-height: 1.68; }
.stMarkdown blockquote {
    border-left: 3px solid var(--ms-mod, var(--ms-primary));
    background: var(--ms-surface-2); border-radius: 0 var(--ms-r-sm) var(--ms-r-sm) 0;
    padding: 12px 18px; margin: 14px 0; color: var(--ms-text);
}
.stMarkdown hr { border: none; border-top: 1px solid var(--ms-border); margin: 1.5rem 0; }
.stMarkdown code { background: var(--ms-surface-2); padding: 2px 7px; border-radius: 7px; font-size: .9em; }
.stMarkdown table { border-radius: var(--ms-r-sm); overflow: hidden; border: 1px solid var(--ms-border); }
.stMarkdown thead tr { background: var(--ms-surface-2); }

/* Spinner in accent */
.stSpinner > div > div { border-top-color: var(--ms-mod, var(--ms-primary)) !important; }

/* Custom scrollbars */
* { scrollbar-width: thin; scrollbar-color: var(--ms-secondary) transparent; }
::-webkit-scrollbar { width: 10px; height: 10px; }
::-webkit-scrollbar-thumb {
    background: var(--ms-secondary); border-radius: 999px;
    border: 2px solid transparent; background-clip: content-box;
}
::-webkit-scrollbar-thumb:hover { background: var(--ms-primary); background-clip: content-box; }
::selection { background: rgba(255,126,182,0.28); color: var(--ms-text); }

/* ══ SIDEBAR NAV BUTTONS ══════════════════════════════════════════════════════ */

/* Make sidebar secondary (inactive) nav buttons look like clean nav items */
section[data-testid="stSidebar"] .stButton > button[kind="secondary"] {
    background: transparent !important;
    border: none !important;
    color: var(--ms-muted) !important;
    font-weight: 500 !important;
    font-size: .88rem !important;
    text-align: left !important;
    padding: 9px 12px !important;
    border-radius: var(--ms-r-md) !important;
    transition: background .15s ease, color .15s ease !important;
    box-shadow: none !important;
    justify-content: flex-start !important;
}
section[data-testid="stSidebar"] .stButton > button[kind="secondary"]:hover {
    background: rgba(255,126,182,.09) !important;
    color: var(--ms-text) !important;
}
/* Active (primary) nav buttons */
section[data-testid="stSidebar"] .stButton > button[kind="primary"] {
    background: linear-gradient(135deg, rgba(255,126,182,.20), rgba(249,168,38,.13)) !important;
    border: none !important;
    color: var(--ms-primary) !important;
    font-weight: 700 !important;
    font-size: .88rem !important;
    text-align: left !important;
    padding: 9px 12px !important;
    border-radius: var(--ms-r-md) !important;
    box-shadow: none !important;
    justify-content: flex-start !important;
}
section[data-testid="stSidebar"] .stButton > button[kind="primary"]:hover {
    filter: brightness(1.03) !important;
}
/* Logout / signup action buttons — keep standard styling, override font size */
section[data-testid="stSidebar"] .ms-sidebar-footer .stButton > button {
    font-size: .87rem !important;
}
.ms-sidebar-footer { padding: 4px 0 8px; }

/* Workspace meta row */
.ms-workspace .ws-meta { display: flex; align-items: center; justify-content: space-between; margin-top: 4px; }
.ms-workspace .ws-title { font-family: var(--ms-font-display); font-size: .96rem; font-weight: 600; color: var(--ms-text); }

/* ══ LANDING PAGE ════════════════════════════════════════════════════════════ */

/* ── Landing Navbar ─────────────────────────────────────────────────────────── */
.lp-nav {
    display: flex; align-items: center; justify-content: space-between;
    padding: 14px 56px; position: sticky; top: 0; z-index: 100;
    background: rgba(255,248,243,.97); backdrop-filter: blur(16px);
    border-bottom: 1px solid rgba(0,0,0,.07);
}
.lp-nav-left { display: flex; align-items: center; gap: 10px; }
.lp-nav-mark {
    width: 36px; height: 36px; border-radius: 10px; display: grid; place-items: center;
    background: linear-gradient(135deg, var(--ms-primary), var(--ms-accent));
    box-shadow: 0 2px 10px rgba(255,126,182,.35);
}
.lp-nav-name {
    font-family: var(--ms-font-display); font-size: 1.25rem; font-weight: 700;
    color: var(--ms-text); letter-spacing: -.01em;
}
.lp-nav-right { display: flex; align-items: center; gap: 10px; }
.lp-nav-link {
    font-size: .9rem; font-weight: 600; color: var(--ms-muted);
    text-decoration: none !important; padding: 8px 16px; border-radius: var(--ms-r-pill);
    transition: color .2s ease, background .2s ease;
}
.lp-nav-link:hover { color: var(--ms-text); background: rgba(0,0,0,.04); }
.lp-nav-cta {
    display: inline-flex; align-items: center; gap: 6px;
    font-size: .9rem; font-weight: 700; color: #fff !important;
    background: linear-gradient(135deg, var(--ms-primary), var(--ms-accent));
    padding: 9px 20px; border-radius: var(--ms-r-pill);
    text-decoration: none !important; box-shadow: 0 3px 12px rgba(255,126,182,.35);
    transition: filter .2s ease, transform .18s ease;
}
.lp-nav-cta:hover { filter: brightness(1.06); transform: translateY(-1px); }

/* ── Landing Hero ─────────────────────────────────────────────────────────── */
.lp-hero {
    padding: 96px 56px 80px; text-align: center;
    max-width: 840px; margin: 0 auto;
}
.lp-hero-badge {
    display: inline-block; font-size: 11.5px; font-weight: 700;
    letter-spacing: .12em; text-transform: uppercase; color: var(--ms-primary);
    background: rgba(255,126,182,.11); border: 1px solid rgba(255,126,182,.28);
    padding: 6px 18px; border-radius: var(--ms-r-pill); margin-bottom: 28px;
}
.lp-hero-h1 {
    font-family: var(--ms-font-display); font-size: clamp(2.9rem,6.5vw,4.6rem);
    font-weight: 700; line-height: 1.05; letter-spacing: -.025em; color: var(--ms-text);
    margin: 0 0 22px;
}
.lp-grad {
    background: linear-gradient(125deg, var(--ms-primary) 0%, var(--ms-accent) 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
}
.lp-hero-sub {
    font-size: 1.15rem; color: var(--ms-muted); max-width: 580px;
    margin: 0 auto 40px; line-height: 1.72;
}
.lp-hero-ctas {
    display: flex; align-items: center; justify-content: center; gap: 14px;
    flex-wrap: wrap; margin-bottom: 30px;
}
.lp-btn-primary {
    display: inline-flex; align-items: center; gap: 7px;
    font-size: 1rem; font-weight: 700; color: #fff !important;
    background: linear-gradient(135deg, var(--ms-primary), var(--ms-accent));
    padding: 14px 30px; border-radius: var(--ms-r-pill);
    text-decoration: none !important; box-shadow: 0 4px 18px rgba(255,126,182,.38);
    transition: filter .2s ease, transform .18s cubic-bezier(.34,1.4,.64,1);
}
.lp-btn-primary:hover { filter: brightness(1.06); transform: translateY(-2px); }
.lp-btn-ghost {
    display: inline-flex; align-items: center; gap: 7px;
    font-size: 1rem; font-weight: 600; color: var(--ms-text) !important;
    background: #fff; border: 1.5px solid var(--ms-border);
    padding: 13px 26px; border-radius: var(--ms-r-pill);
    text-decoration: none !important; box-shadow: 0 2px 8px rgba(0,0,0,.07);
    transition: transform .18s ease, box-shadow .2s ease;
}
.lp-btn-ghost:hover { transform: translateY(-2px); box-shadow: 0 6px 18px rgba(0,0,0,.1); }
.lp-trust {
    display: flex; align-items: center; justify-content: center; gap: 20px;
    flex-wrap: wrap; font-size: .84rem; font-weight: 600; color: var(--ms-muted);
}
.lp-trust span { display: inline-flex; align-items: center; gap: 5px; }

/* ── Stats bar ──────────────────────────────────────────────────────────────── */
.lp-stats-bar {
    display: flex; justify-content: center; align-items: stretch;
    border-top: 1px solid var(--ms-border); border-bottom: 1px solid var(--ms-border);
    background: #fff;
}
.lp-stat {
    flex: 1; min-width: 140px; text-align: center; padding: 36px 24px;
    border-right: 1px solid var(--ms-border);
}
.lp-stat:last-child { border-right: none; }
.lp-stat-v {
    font-family: var(--ms-font-display); font-size: 2.5rem; font-weight: 700;
    color: var(--ms-text); line-height: 1; letter-spacing: -.02em;
}
.lp-stat-l { font-size: .84rem; color: var(--ms-muted); margin-top: 7px; font-weight: 500; }

/* ── Feature section ────────────────────────────────────────────────────────── */
.lp-section { padding: 80px 56px; }
.lp-alt { background: #fff; }
.lp-eyebrow {
    text-align: center; font-size: 11.5px; font-weight: 700;
    letter-spacing: .12em; text-transform: uppercase; color: var(--ms-primary);
    margin-bottom: 14px;
}
.lp-section-h2 {
    font-family: var(--ms-font-display); font-size: clamp(1.85rem,3vw,2.7rem);
    font-weight: 700; text-align: center; color: var(--ms-text);
    letter-spacing: -.015em; margin-bottom: 52px;
}
.lp-feat-grid {
    display: grid; grid-template-columns: repeat(auto-fit, minmax(280px,1fr));
    gap: 18px; max-width: 1100px; margin: 0 auto;
}
.lp-feat-card {
    background: #fff; border: 1px solid var(--ms-border);
    border-radius: var(--ms-r-xl); padding: 26px 24px;
    box-shadow: 0 1px 6px rgba(0,0,0,.04);
    transition: transform .22s cubic-bezier(.34,1.4,.64,1), box-shadow .22s ease;
}
.lp-feat-card:hover { transform: translateY(-5px); box-shadow: 0 10px 28px rgba(0,0,0,.09); }
.lp-feat-icon {
    width: 50px; height: 50px; border-radius: 12px;
    display: grid; place-items: center; margin-bottom: 16px;
}
.lp-feat-title { font-weight: 700; font-size: 1rem; color: var(--ms-text); margin-bottom: 7px; }
.lp-feat-desc { font-size: .89rem; color: var(--ms-muted); line-height: 1.62; }

/* ── Steps ────────────────────────────────────────────────────────────────── */
.lp-steps {
    display: grid; grid-template-columns: 1fr auto 1fr auto 1fr;
    align-items: start; max-width: 880px; margin: 0 auto;
}
.lp-step { text-align: center; padding: 0 20px; }
.lp-step-connector {
    margin-top: 18px; border-top: 1.5px dashed rgba(0,0,0,.15); width: 50px; align-self: start;
}
.lp-step-num {
    font-family: var(--ms-font-display); font-size: 2.2rem; font-weight: 700;
    background: linear-gradient(135deg, var(--ms-primary), var(--ms-accent));
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
    margin-bottom: 12px; line-height: 1;
}
.lp-step-title { font-weight: 700; font-size: 1.02rem; color: var(--ms-text); margin-bottom: 9px; }
.lp-step-desc { font-size: .88rem; color: var(--ms-muted); line-height: 1.62; }

/* ── CTA section ────────────────────────────────────────────────────────────── */
.lp-cta-section {
    text-align: center; padding: 90px 56px;
    background: linear-gradient(160deg, rgba(255,126,182,.1) 0%, rgba(249,168,38,.08) 100%);
    border-top: 1px solid rgba(255,126,182,.18);
}
.lp-cta-h2 {
    font-family: var(--ms-font-display); font-size: clamp(2rem,4vw,3rem);
    font-weight: 700; color: var(--ms-text); letter-spacing: -.02em; margin-bottom: 16px;
}
.lp-cta-sub { color: var(--ms-muted); font-size: 1.05rem; margin-bottom: 36px; }

/* ── Footer ────────────────────────────────────────────────────────────────── */
.lp-footer {
    display: flex; justify-content: space-between; align-items: center;
    padding: 22px 56px; border-top: 1px solid var(--ms-border);
    color: var(--ms-muted); font-size: .84rem; flex-wrap: wrap; gap: 8px;
}

/* ══ AUTH GATE ══════════════════════════════════════════════════════════════ */
.ms-auth-back {
    display: inline-flex; align-items: center; gap: 6px;
    font-size: .85rem; color: var(--ms-muted); text-decoration: none !important;
    margin-bottom: 1.4rem; transition: color .2s ease;
}
.ms-auth-back:hover { color: var(--ms-text); }
.ms-auth-guest-link {
    display: block; text-align: center; font-size: .92rem; font-weight: 600;
    color: var(--ms-muted) !important; text-decoration: none !important;
    padding: 10px; border-radius: var(--ms-r-md); transition: color .2s ease, background .2s ease;
}
.ms-auth-guest-link:hover { color: var(--ms-text) !important; background: var(--ms-surface-2); }
/* ══ AUTH GATE ORIGINAL ══════════════════════════════════════════════════════ */

.ms-auth-brand {
    text-align: center; margin-bottom: 2.2rem;
}
.ms-auth-logo {
    width: 60px; height: 60px; border-radius: 16px;
    background: linear-gradient(135deg, var(--ms-primary), var(--ms-accent));
    display: grid; place-items: center; margin: 0 auto .75rem;
    box-shadow: 0 4px 16px rgba(255,126,182,.35);
    animation: auth-float 3s ease-in-out infinite;
}

/* Two-column auth layout */
.ms-auth-left {
    display: flex; flex-direction: column;
    justify-content: center; padding: 2.5rem 1.5rem 2.5rem 0;
    height: 100%;
}
.ms-auth-logo-wrap { margin-bottom: 1.4rem; }
.ms-auth-left .ms-auth-name {
    font-family: var(--ms-font-display); font-size: 2.6rem; font-weight: 700;
    color: var(--ms-text); letter-spacing: -.02em; line-height: 1; margin-bottom: .5rem;
    text-align: left;
}
.ms-auth-left .ms-auth-tag {
    font-size: 1rem; color: var(--ms-muted); margin-bottom: 2rem; text-align: left;
}
.ms-auth-features {
    list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 12px;
}
.ms-auth-features li {
    display: flex; align-items: center; gap: 10px;
    font-size: .95rem; font-weight: 500; color: var(--ms-text);
}
.ms-auth-form-panel {
    background: var(--ms-surface); border: 1px solid var(--ms-border);
    border-radius: var(--ms-r-xl); padding: 2.2rem 2rem;
    box-shadow: 0 4px 24px rgba(0,0,0,.06);
}
@keyframes auth-float {
    0%,100% { transform: translateY(0); }
    50%      { transform: translateY(-6px); }
}
.ms-auth-name {
    font-family: var(--ms-font-display); font-size: 2.4rem; font-weight: 700;
    color: var(--ms-text); letter-spacing: -0.02em; line-height: 1;
}
.ms-auth-tag {
    font-size: .95rem; color: var(--ms-muted); margin-top: .35rem;
}
.ms-auth-divider {
    display: flex; align-items: center; gap: 12px; margin: 1.4rem 0 1rem;
    color: var(--ms-muted); font-size: .85rem;
}
.ms-auth-divider::before, .ms-auth-divider::after {
    content: ""; flex: 1; height: 1px; background: var(--ms-border);
}
.ms-auth-note {
    text-align: center; color: var(--ms-muted); font-size: .82rem; margin-top: .6rem;
}
.ms-auth-pillars {
    display: flex; justify-content: center; flex-wrap: wrap; gap: 8px;
    margin-top: 1.8rem;
}
.ms-auth-pillars span {
    font-size: 12px; font-weight: 600; color: var(--ms-muted);
    background: var(--ms-surface-2); border: 1px solid var(--ms-border);
    padding: 5px 13px; border-radius: var(--ms-r-pill);
}

/* ══ WORKSPACE SIDEBAR HEADER ════════════════════════════════════════════════ */

.ms-workspace {
    padding: 12px 14px 10px; margin-bottom: 2px;
    border-bottom: 1px solid var(--ms-border);
}
.ms-workspace .ws-user {
    display: flex; align-items: center; gap: 10px; margin-bottom: 8px;
}
.ms-workspace .ws-avatar {
    width: 36px; height: 36px; border-radius: 50%; display: grid; place-items: center;
    font-size: 18px; background: linear-gradient(135deg, rgba(255,126,182,.22), rgba(249,168,38,.20));
    flex: 0 0 auto; box-shadow: var(--ms-shadow-soft);
}
.ms-workspace .ws-name {
    font-weight: 700; font-size: .95rem; color: var(--ms-text); line-height: 1.1;
}
.ms-workspace .ws-email {
    font-size: .75rem; color: var(--ms-muted);
}
.ms-workspace .ws-label {
    font-size: 11.5px; color: var(--ms-muted); margin-bottom: 4px; font-weight: 600;
}
.ms-workspace .ws-title {
    font-family: var(--ms-font-display); font-size: 1.02rem; font-weight: 600;
    color: var(--ms-text); white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}

/* Plan badge */
.ms-plan-badge {
    display: inline-flex; align-items: center; gap: 5px;
    font-size: 11px; font-weight: 700; letter-spacing: .05em; text-transform: uppercase;
    padding: 4px 10px; border-radius: var(--ms-r-pill); margin-top: 6px;
    cursor: pointer;
}
.ms-plan-free   { background: var(--ms-surface-2); color: var(--ms-muted); border: 1px solid var(--ms-border); }
.ms-plan-pro    { background: linear-gradient(135deg,rgba(255,126,182,.22),rgba(249,168,38,.18)); color: var(--ms-text); border: 1px solid rgba(255,126,182,.35); }
.ms-plan-agency { background: linear-gradient(135deg,rgba(249,168,38,.28),rgba(255,126,182,.20)); color: var(--ms-text); border: 1px solid rgba(249,168,38,.40); }

/* ══ ONBOARDING WIZARD ═══════════════════════════════════════════════════════ */

.ms-onboard-step {
    text-align: center; padding: 3rem 1rem 2rem;
}
.ms-onboard-step .step-emoji {
    font-size: 3.6rem; margin-bottom: 1rem;
    animation: auth-float 3s ease-in-out infinite;
}
.ms-onboard-step .step-title {
    font-family: var(--ms-font-display); font-size: 2rem; font-weight: 700;
    color: var(--ms-text); margin-bottom: .5rem;
}
.ms-onboard-step .step-sub {
    color: var(--ms-muted); font-size: 1.05rem; max-width: 520px; margin: 0 auto 1.6rem;
}
.ms-stepper {
    display: flex; justify-content: center; gap: 8px; margin-bottom: 2.4rem;
}
.ms-stepper .dot {
    width: 10px; height: 10px; border-radius: 50%;
    background: var(--ms-border);
    transition: background .25s ease, transform .25s ease;
}
.ms-stepper .dot.active {
    background: var(--ms-primary); transform: scale(1.35);
}
.ms-stepper .dot.done {
    background: var(--ms-success);
}

/* ══ WORKSPACE OVERVIEW STATS ROW ═══════════════════════════════════════════ */

.ms-ws-stats {
    display: grid; grid-template-columns: repeat(auto-fit, minmax(180px,1fr)); gap: 14px;
    margin-bottom: 8px;
}
.ms-ws-stat {
    background: var(--ms-surface); border: 1px solid var(--ms-border);
    border-radius: var(--ms-r-lg); padding: 18px 20px;
    box-shadow: var(--ms-shadow-soft);
    transition: transform .2s ease, box-shadow .2s ease;
}
.ms-ws-stat:hover { transform: translateY(-3px); box-shadow: var(--ms-shadow-card); }
.ms-ws-stat .ws-stat-label {
    font-size: 11px; font-weight: 700; letter-spacing: .10em; text-transform: uppercase;
    color: var(--ms-muted); margin-bottom: 8px; display: flex; align-items: center; gap: 6px;
}
.ms-ws-stat .ws-stat-val {
    font-family: var(--ms-font-display); font-size: 1.8rem; font-weight: 700;
    color: var(--ms-text); line-height: 1;
}
.ms-ws-stat .ws-stat-sub { font-size: .8rem; color: var(--ms-muted); margin-top: 5px; }

/* ══ MUSE MEMORY CARD ════════════════════════════════════════════════════════ */

.ms-memory-card {
    background: linear-gradient(135deg, rgba(255,126,182,.08) 0%, rgba(249,168,38,.06) 100%);
    border: 1px solid rgba(255,126,182,.22); border-radius: var(--ms-r-xl);
    padding: 22px 24px; margin-bottom: 24px; position: relative; overflow: hidden;
}
.ms-memory-card::after {
    content: ""; position: absolute; right: -40px; top: -40px; width: 160px; height: 160px;
    border-radius: 50%; background: radial-gradient(circle, rgba(255,126,182,.14), transparent 70%);
    pointer-events: none;
}
.ms-memory-card .mm-header {
    display: flex; align-items: center; gap: 12px; margin-bottom: 16px;
}
.ms-memory-card .mm-brain {
    width: 46px; height: 46px; border-radius: 50%; font-size: 22px;
    display: grid; place-items: center; flex: 0 0 auto;
    background: linear-gradient(135deg, rgba(255,126,182,.25), rgba(249,168,38,.20));
    box-shadow: var(--ms-shadow-soft);
}
.ms-memory-card .mm-title {
    font-family: var(--ms-font-display); font-weight: 700; font-size: 1.08rem; color: var(--ms-text);
}
.ms-memory-card .mm-sub { font-size: .82rem; color: var(--ms-muted); margin-top: 2px; }
.ms-memory-card .mm-status {
    margin-left: auto; font-size: 11.5px; font-weight: 700; padding: 4px 11px;
    border-radius: var(--ms-r-pill); flex: 0 0 auto;
}
.ms-memory-card .mm-status.active {
    background: rgba(123,196,127,.16); color: #3A8A3E; border: 1px solid rgba(123,196,127,.35);
}
.ms-memory-card .mm-status.empty {
    background: var(--ms-surface-2); color: var(--ms-muted); border: 1px solid var(--ms-border);
}
.ms-memory-card .mm-items { display: flex; flex-wrap: wrap; gap: 8px; }
.ms-memory-card .mm-item {
    background: var(--ms-surface); border: 1px solid var(--ms-border);
    border-radius: var(--ms-r-md); padding: 8px 14px;
    display: flex; flex-direction: column; gap: 2px;
}
.ms-memory-card .mm-key {
    font-size: 10.5px; font-weight: 700; letter-spacing: .08em; text-transform: uppercase;
    color: var(--ms-muted);
}
.ms-memory-card .mm-val { font-size: .88rem; font-weight: 600; color: var(--ms-text); }

/* ══ PLAN GATE BANNER ════════════════════════════════════════════════════════ */

.ms-plan-gate {
    display: flex; align-items: center; gap: 10px;
    background: linear-gradient(135deg, rgba(249,168,38,.12), rgba(255,126,182,.08));
    border: 1px solid rgba(249,168,38,.30); border-radius: var(--ms-r-md);
    padding: 12px 18px; margin: 12px 0; font-size: .9rem; color: var(--ms-text);
}
.ms-plan-gate a { color: var(--ms-primary); font-weight: 700; text-decoration: none; }
.ms-plan-gate a:hover { text-decoration: underline; }

/* ══ LIBRARY PAGE ════════════════════════════════════════════════════════════ */

.ms-lib-grid {
    display: grid; grid-template-columns: repeat(auto-fill, minmax(290px,1fr)); gap: 16px;
}
.ms-lib-card {
    background: var(--ms-surface); border: 1px solid var(--ms-border);
    border-radius: var(--ms-r-lg); padding: 20px 22px; position: relative; overflow: hidden;
    transition: transform .2s ease, box-shadow .2s ease;
    box-shadow: var(--ms-shadow-soft);
}
.ms-lib-card:hover { transform: translateY(-4px); box-shadow: var(--ms-shadow-card); }
.ms-lib-card::after {
    content: ""; position: absolute; right: -24px; bottom: -28px;
    width: 90px; height: 90px; border-radius: 50%;
    background: radial-gradient(circle, rgba(255,126,182,.10), transparent 70%);
}
.ms-lib-card .lc-type {
    display: inline-block; font-size: 11px; font-weight: 700; letter-spacing: .08em;
    text-transform: uppercase; color: var(--ms-muted);
    background: var(--ms-surface-2); border: 1px solid var(--ms-border);
    padding: 3px 10px; border-radius: var(--ms-r-pill); margin-bottom: 10px;
}
.ms-lib-card .lc-title {
    font-family: var(--ms-font-display); font-size: 1.1rem; font-weight: 600;
    color: var(--ms-text); margin-bottom: 6px;
}
.ms-lib-card .lc-date { font-size: .8rem; color: var(--ms-muted); }

/* ══ SETTINGS PAGE ═══════════════════════════════════════════════════════════ */

.ms-plan-card {
    border: 2px solid var(--ms-border); border-radius: var(--ms-r-lg);
    padding: 22px 22px 18px; height: 100%; transition: border-color .2s ease, box-shadow .2s ease;
}
.ms-plan-card:hover { border-color: var(--ms-primary); box-shadow: var(--ms-shadow-glow); }
.ms-plan-card.current { border-color: var(--ms-primary); box-shadow: var(--ms-shadow-glow); }
.ms-plan-card .pc-name {
    font-family: var(--ms-font-display); font-size: 1.35rem; font-weight: 700;
    color: var(--ms-text); margin-bottom: 4px;
}
.ms-plan-card .pc-price {
    font-size: 2rem; font-weight: 700; color: var(--ms-text); line-height: 1;
    margin-bottom: 14px;
}
.ms-plan-card .pc-price span { font-size: 1rem; font-weight: 400; color: var(--ms-muted); }
.ms-plan-card ul { padding-left: 0; list-style: none; margin: 0 0 16px 0; }
.ms-plan-card ul li { font-size: .9rem; color: var(--ms-muted); padding: 4px 0; }
.ms-plan-card ul li::before { content: "✓  "; color: var(--ms-success); font-weight: 700; }
.ms-plan-lock {
    display: inline-flex; align-items: center; gap: 5px; font-size: 11px; font-weight: 700;
    color: var(--ms-muted); background: var(--ms-surface-2); border: 1px solid var(--ms-border);
    padding: 3px 9px; border-radius: var(--ms-r-pill);
}

#MainMenu, footer { visibility: hidden; }
"""


def inject_styles():
    st.markdown(f"<style>{_root_vars()}{_CSS}</style>", unsafe_allow_html=True)
