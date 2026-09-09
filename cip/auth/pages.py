"""Landing page, auth gate, and sub-forms.

Landing page is pure HTML — no Streamlit button rendering artifacts.
CTAs use ?_auth= query params handled by app.py.
"""
import streamlit as st

from cip.auth.auth import login, signup
from cip.theme import BRAND_NAME, BRAND_TAGLINE
from cip.ui import icon as _icon, logo_img as _logo

# ─────────────────────────────────────────────────────────────────────────────
# LANDING PAGE  (pure HTML, no st.button)
# ─────────────────────────────────────────────────────────────────────────────

def _feat(ico: str, color: str, title: str, desc: str) -> str:
    svg = _icon(ico, 22, color)
    return (
        f'<div class="lp-feat-card">'
        f'<div class="lp-feat-icon" style="background:{color}18;border:1px solid {color}28">{svg}</div>'
        f'<div class="lp-feat-title">{title}</div>'
        f'<div class="lp-feat-desc">{desc}</div>'
        f'</div>'
    )


def render_landing():
    """Full marketing landing page — shown before authentication."""
    st.markdown("""<style>
        section[data-testid="stSidebar"]{display:none!important;}
        header[data-testid="stHeader"]{display:none!important;}
        .block-container{max-width:100%!important;padding:0!important;}
        .stApp{overflow-x:hidden;}
    </style>""", unsafe_allow_html=True)

    logo_html = _logo(34)
    check     = _icon("check", 16, "var(--ms-success)")
    arr       = _icon("arrow-r", 16, "#fff")

    # ── Navbar ────────────────────────────────────────────────────────────────
    st.markdown(f"""
    <nav class="lp-nav">
      <div class="lp-nav-left">
        {logo_html}
      </div>
      <div class="lp-nav-right">
        <a href="?_auth=login"  class="lp-nav-link">Sign In</a>
        <a href="?_auth=signup" class="lp-nav-cta">Get Started Free {arr}</a>
      </div>
    </nav>
    """, unsafe_allow_html=True)

    # ── Hero ──────────────────────────────────────────────────────────────────
    arr_dark = _icon("arrow-r", 15, "var(--ms-text)")
    st.markdown(f"""
    <section class="lp-hero">
      <div class="lp-hero-badge">AI Platform for Creators</div>
      <h1 class="lp-hero-h1">The creative platform<br><span class="lp-grad">built for your brand.</span></h1>
      <p class="lp-hero-sub">
        10 AI-powered tools that learn your voice, grow your audience,
        and help you close better brand deals — all in one workspace.
      </p>
      <div class="lp-hero-ctas">
        <a href="?_auth=signup" class="lp-btn-primary">Create Free Account {arr}</a>
        <a href="?_auth=guest"  class="lp-btn-ghost">Try as Guest {arr_dark}</a>
      </div>
      <div class="lp-trust">
        <span>{check} Free to start</span>
        <span>{check} No card required</span>
        <span>{check} All AI tools included</span>
        <span>{check} Reports saved forever</span>
      </div>
    </section>
    """, unsafe_allow_html=True)

    # ── Stats ─────────────────────────────────────────────────────────────────
    st.markdown("""
    <section class="lp-stats-bar">
      <div class="lp-stat"><div class="lp-stat-v">10</div><div class="lp-stat-l">AI-powered tools</div></div>
      <div class="lp-stat"><div class="lp-stat-v">100%</div><div class="lp-stat-l">Creator focused</div></div>
      <div class="lp-stat"><div class="lp-stat-v">Free</div><div class="lp-stat-l">To get started</div></div>
      <div class="lp-stat"><div class="lp-stat-v">∞</div><div class="lp-stat-l">Reports saved</div></div>
    </section>
    """, unsafe_allow_html=True)

    # ── Features ──────────────────────────────────────────────────────────────
    f1 = _feat("photo",    "#8B5CF6", "Caption Magic",    "Upload a photo — get captions, hashtags, reel concepts, and trending sounds instantly.")
    f2 = _feat("pen",      "#F9A826", "Content Studio",   "Hooks, captions, and a 7-day calendar written in your own voice and style.")
    f3 = _feat("shield",   "#FB5E78", "Pre-Publish Check","Check virality, brand safety, and engagement prediction before every post.")
    f4 = _feat("trending", "#0EA371", "Growth Coach",     "Personalised 30-day roadmap, problem solver, and an on-demand AI coach.")
    f5 = _feat("link",     "#B8902A", "Brand Match",      "Score brand deals, vet reputations, and draft campaign briefs automatically.")
    f6 = _feat("sparkles", "#FF7EB6", "Brand DNA",        "Generate a one-page media kit — authority score, niche, voice, and audience snapshot.")
    f7 = _feat("currency", "#047857", "Creator Earnings", "Full CRM to track deals, payments, and revenue trends over time.")
    f8 = _feat("heart",    "#EC6FA9", "Wellbeing Coach",  "Burnout predictor, check-ins, and audience authenticity analysis.")
    f9 = _feat("fire",     "#FF4D6D", "Trends Briefing",  "Live-grounded trending topics, sounds, and creator news for your niche.")

    st.markdown(f"""
    <section class="lp-section">
      <p class="lp-eyebrow">Everything you need</p>
      <h2 class="lp-section-h2">10 tools. One workspace. Zero fluff.</h2>
      <div class="lp-feat-grid">
        {f1}{f2}{f3}{f4}{f5}{f6}{f7}{f8}{f9}
      </div>
    </section>
    """, unsafe_allow_html=True)

    # ── How it works ──────────────────────────────────────────────────────────
    st.markdown("""
    <section class="lp-section lp-alt">
      <p class="lp-eyebrow">How it works</p>
      <h2 class="lp-section-h2">Up and running in 60 seconds</h2>
      <div class="lp-steps">
        <div class="lp-step">
          <div class="lp-step-num">01</div>
          <div class="lp-step-title">Set up your profile</div>
          <div class="lp-step-desc">Tell Muse your niche, platforms, and audience once. Every tool personalises around it automatically.</div>
        </div>
        <div class="lp-step lp-step-connector"></div>
        <div class="lp-step">
          <div class="lp-step-num">02</div>
          <div class="lp-step-title">Pick a tool</div>
          <div class="lp-step-desc">Choose from 10 AI tools covering content creation, growth strategy, brand deals, and wellbeing.</div>
        </div>
        <div class="lp-step lp-step-connector"></div>
        <div class="lp-step">
          <div class="lp-step-num">03</div>
          <div class="lp-step-title">Get results instantly</div>
          <div class="lp-step-desc">Generate captions, plans, reports, and pitches in seconds. Saved to your library forever.</div>
        </div>
      </div>
    </section>
    """, unsafe_allow_html=True)

    # ── CTA section ───────────────────────────────────────────────────────────
    arr2 = _icon("arrow-r", 16, "#fff")
    st.markdown(f"""
    <section class="lp-cta-section">
      <p class="lp-eyebrow" style="color:var(--ms-primary)">Start today</p>
      <h2 class="lp-cta-h2">Ready to grow your<br>creator business?</h2>
      <p class="lp-cta-sub">Join creators who use Muse to create smarter, grow faster, and build sustainable brands.</p>
      <div class="lp-hero-ctas">
        <a href="?_auth=signup" class="lp-btn-primary">Create Free Account {arr2}</a>
        <a href="?_auth=login"  class="lp-btn-ghost" style="color:var(--ms-text)!important">Sign In</a>
      </div>
    </section>
    """, unsafe_allow_html=True)

    # ── Footer ────────────────────────────────────────────────────────────────
    st.markdown(f"""
    <footer class="lp-footer">
      <span>{BRAND_NAME} · {BRAND_TAGLINE}</span>
      <span>Built for creators everywhere · 2026</span>
    </footer>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# AUTH GATE  (compact sign-in / create-account card)
# ─────────────────────────────────────────────────────────────────────────────

def render_auth_gate():
    """Two-column professional auth layout — brand panel + form panel."""
    st.markdown("""<style>
        section[data-testid="stSidebar"]{display:none!important;}
        header[data-testid="stHeader"]{display:none!important;}
        .block-container{
            max-width:900px!important;
            padding-top:2.5rem!important;
            padding-bottom:2.5rem!important;
        }
    </style>""", unsafe_allow_html=True)

    # Back link
    st.markdown(
        '<a href="?_auth=back" class="ms-auth-back" target="_self">'
        f'{_icon("x", 13, "var(--ms-muted)")} Back to Muse'
        '</a>',
        unsafe_allow_html=True,
    )

    # Two-column layout: brand panel (left) + form panel (right)
    left, right = st.columns([1, 1], gap="large")

    with left:
        logo_html = _logo(64)
        st.markdown(
            f'<div class="ms-auth-left">'
            f'<div class="ms-auth-logo-wrap">{logo_html}</div>'
            f'<div class="ms-auth-name">{BRAND_NAME}</div>'
            f'<div class="ms-auth-tag">{BRAND_TAGLINE}</div>'
            f'<ul class="ms-auth-features">'
            f'<li>{_icon("sparkles",14,"var(--ms-primary)")} 10 AI-powered creator tools</li>'
            f'<li>{_icon("archive",14,"var(--ms-primary)")} Reports & media kits saved forever</li>'
            f'<li>{_icon("trending",14,"var(--ms-primary)")} Growth plans personalized to you</li>'
            f'<li>{_icon("heart",14,"var(--ms-primary)")} Free to start, no card needed</li>'
            f'</ul>'
            f'</div>',
            unsafe_allow_html=True,
        )

    with right:
        st.markdown('<div class="ms-auth-form-panel">', unsafe_allow_html=True)

        default_view = st.session_state.get("_auth_view", "login")

        if default_view == "signup":
            tab_up, tab_in = st.tabs(["Create Account", "Sign In"])
            with tab_up:
                _render_signup()
            with tab_in:
                _render_login()
        else:
            tab_in, tab_up = st.tabs(["Sign In", "Create Account"])
            with tab_in:
                _render_login()
            with tab_up:
                _render_signup()

        st.markdown('<div class="ms-auth-divider"><span>or</span></div>', unsafe_allow_html=True)
        arr = _icon("arrow-r", 14, "var(--ms-muted)")
        st.markdown(
            f'<a href="?_auth=guest" class="ms-auth-guest-link" target="_self">'
            f'Continue as Guest {arr}</a>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<p class="ms-auth-note">Guest sessions are temporary — create a free account to save your work.</p>',
            unsafe_allow_html=True,
        )
        st.markdown('</div>', unsafe_allow_html=True)


def _render_login():
    with st.form("login_form", clear_on_submit=False):
        email    = st.text_input("Email",    placeholder="you@example.com", key="li_email")
        password = st.text_input("Password", type="password", placeholder="Your password", key="li_pw")
        submitted = st.form_submit_button("Sign In", type="primary", use_container_width=True)
    if submitted:
        if not email.strip() or not password:
            st.error("Please fill in all fields.")
        else:
            ok, msg = login(email.strip(), password)
            if ok:
                st.session_state.pop("_auth_view", None)
                st.rerun()
            else:
                st.error(msg)


def _render_signup():
    with st.form("signup_form", clear_on_submit=False):
        name     = st.text_input("Full Name", placeholder="Your name",        key="su_name")
        email    = st.text_input("Email",     placeholder="you@example.com",  key="su_email")
        password = st.text_input("Password",  type="password",
                                 placeholder="Min. 6 characters",             key="su_pw")
        submitted = st.form_submit_button("Create Account", type="primary", use_container_width=True)
    if submitted:
        if not name.strip() or not email.strip() or not password:
            st.error("Please fill in all fields.")
        else:
            ok, msg = signup(name.strip(), email.strip(), password)
            if ok:
                st.session_state.pop("_auth_view", None)
                st.rerun()
            else:
                st.error(msg)
