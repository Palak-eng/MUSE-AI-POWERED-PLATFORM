"""Page renderers, sidebar, and router (presentation layer only).

Each render_* function reuses the untouched business-logic functions from
`cip.features` and `cip.ai`; only layout/composition lives here.
"""
from datetime import date, datetime

import pandas as pd
import streamlit as st

from .ai import get_context, get_profile, ask_ai
from .theme import BRAND_NAME, BRAND_TAGLINE
from .ui import (
    NAV_GROUPS, go_to, nav_href, section_label, metric_card,
    module_page, module_empty, download_and_copy, context_warning,
    store_report, store_deal, delete_deal_by_idx,
    safe_float, safe_first_name,
)
from .features import (
    generate_media_kit, media_kit_to_markdown,
    generate_content_plan, generate_hooks, hooks_to_markdown,
    analyze_photo_for_captions, photo_analysis_to_markdown,
    pre_publish_check, pre_publish_to_markdown,
    growth_strategy_report,
    brand_dna_match, brand_dna_match_to_markdown,
    brand_reputation_check, brand_reputation_to_markdown,
    generate_campaign_brief, campaign_brief_to_markdown,
    generate_shoppable_content, shoppable_content_to_markdown,
    solve_problem, problem_solution_to_markdown,
    wellbeing_checkin, predict_burnout, burnout_to_markdown,
    generate_trends_report,
    analyze_fake_followers, analyze_fake_comments, fake_audience_to_markdown,
)


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR  (branding + navigation + creator profile)
# ══════════════════════════════════════════════════════════════════════════════
def render_sidebar():
    """Navigation sidebar — workspace header, grouped HTML nav links, logout."""
    from cip.auth.auth import logout, current_user
    from cip.ui import icon as _icon, logo_img as _logo

    with st.sidebar:
        # ── Brand mark ────────────────────────────────────────────────────────
        st.markdown(
            f'<div class="cip-brand">'
            f'<div class="logo">{_logo(28)}</div>'
            f'<div><div class="name">{BRAND_NAME}</div>'
            f'<div class="tag">{BRAND_TAGLINE}</div></div></div>',
            unsafe_allow_html=True,
        )

        # ── Workspace header ──────────────────────────────────────────────────
        user = current_user()
        if user:
            import html as _html

            plan = user.get("plan", "free")
            plan_label = {"free": "Free", "pro": "Pro", "agency": "Agency"}.get(plan, "Free")
            plan_cls   = f"ms-plan-{plan}"
            _first = safe_first_name(user.get("name", ""))
            workspace_name = (
                "Guest Workspace" if user.get("is_guest")
                else f"{_html.escape(_first)}'s Workspace"
            )
            st.markdown(
                f'<div class="ms-workspace">'
                f'<div class="ws-user">'
                f'<div class="ws-avatar">{_icon("user", 18, "var(--ms-primary)")}</div>'
                f'<div>'
                f'<div class="ws-name">{_html.escape(str(user.get("name", "")))}</div>'
                f'<div class="ws-email">{_html.escape("Guest" if user.get("is_guest") else str(user.get("email", "")))}</div>'
                f'</div></div>'
                f'<div class="ws-meta">'
                f'<div class="ws-title">{workspace_name}</div>'
                f'<span class="{plan_cls} ms-plan-badge">{plan_label} Plan</span>'
                f'</div></div>',
                unsafe_allow_html=True,
            )

        # ── Grouped navigation (st.button keeps WebSocket session alive) ─────
        for group_title, items in NAV_GROUPS:
            if group_title:
                st.markdown(
                    f'<div class="ms-navgroup">{group_title}</div>',
                    unsafe_allow_html=True,
                )
            for ico_name, label, page in items:
                active = st.session_state.page == page
                ico_svg = _icon(ico_name, 15, "currentColor")
                if st.button(
                    label,
                    key=f"nav_{page}",
                    use_container_width=True,
                    type="primary" if active else "secondary",
                ):
                    if not active:
                        go_to(page)

        # ── Footer actions ────────────────────────────────────────────────────
        st.markdown('<div class="ms-sidebar-footer">', unsafe_allow_html=True)
        if user and not user.get("is_guest"):
            if st.button("Sign Out", use_container_width=True, key="nav_logout"):
                logout()
        else:
            st.caption("Guest session — work won't be saved.")
            if st.button("Create Free Account", use_container_width=True,
                         key="nav_signup", type="primary"):
                from cip.auth.auth import logout as _lo
                _lo()
        st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# DASHBOARD HOME
# ══════════════════════════════════════════════════════════════════════════════
# Large quick-action cards: (icon, title, helper copy, destination page)
DASH_ACTIONS = [
    ("photo",    "Generate Captions",   "Turn a photo into captions & trends",    "Caption Magic"),
    ("pen",      "Create Content Plan", "Captions, hooks & a 7-day calendar",     "Content Studio"),
    ("trending", "Run Growth Audit",    "A personalised 30-day roadmap",           "Growth Coach"),
    ("link",     "Check Brand Match",   "See how well a brand deal fits you",      "Brand Match"),
    ("currency", "Track Revenue",       "Log deals & watch earnings grow",         "Creator Earnings"),
]

# Map a saved creation to (icon_name, source page) so users can continue working.
REPORT_MAP = {
    "Media Kit":              ("sparkles", "Brand DNA"),
    "Content Plan":           ("pen",      "Content Studio"),
    "Hook Generator":         ("pen",      "Content Studio"),
    "Photo Caption Match":    ("photo",    "Caption Magic"),
    "Pre-Publish Check":      ("shield",   "Pre-Publish"),
    "Growth Plan":            ("trending", "Growth Coach"),
    "Problem Solver":         ("trending", "Growth Coach"),
    "Brand Fit Check":        ("link",     "Brand Match"),
    "Brand Reputation Check": ("shield",   "Brand Match"),
    "Campaign Brief":         ("pen",      "Brand Match"),
    "Social Commerce":        ("link",     "Brand Match"),
    "Deals & Revenue Summary":("currency", "Creator Earnings"),
    "Wellbeing Check-In":     ("heart",    "Wellbeing"),
    "Burnout Predictor":      ("heart",    "Wellbeing"),
    "Fake Audience Analysis": ("user",     "Wellbeing"),
    "Trends Hub":             ("fire",     "Trends"),
}


def _greeting():
    h = datetime.now().hour
    if h < 12:
        return "Good Morning"
    if h < 17:
        return "Good Afternoon"
    return "Good Evening"


def _emotion(score, words):
    """Map a numeric score to an emotional label + tone (not analytical)."""
    try:
        s = float(score)
    except (TypeError, ValueError):
        return words["none"], "neutral"
    if s >= 70:
        return words["good"], "good"
    if s >= 40:
        return words["warn"], "warn"
    return words["bad"], "bad"


def render_dashboard():
    from cip.auth.auth import current_user
    import html as _html
    user = current_user()
    first_name = "Creator"
    if user and not user.get("is_guest"):
        first_name = safe_first_name(user.get("name", "Creator"))

    m = st.session_state.metrics
    reports = st.session_state.reports
    has_context = bool(get_context())

    from cip.ui import icon as _icon
    # ── Hero greeting ──
    st.markdown(
        f'<div class="ms-greet">'
        f'<div class="brand">{_icon("sparkles", 18, "var(--ms-primary)")} {BRAND_NAME}</div>'
        f'<h1>{_greeting()}, {_html.escape(first_name)}</h1>'
        f"<p>Let's create something amazing today. Pick a starting point below — "
        f"Muse handles the heavy lifting so you can stay in your flow.</p>"
        f'</div>',
        unsafe_allow_html=True,
    )

    # ── Workspace Overview (real data from DB / session) ──
    deals = st.session_state.get("deals", [])
    total_earned   = sum(safe_float(d.get("Amount (₹)", 0)) for d in deals if d.get("Status") == "Completed")
    pending_pay    = sum(safe_float(d.get("Amount (₹)", 0)) for d in deals if d.get("Payment") == "Pending")
    reports_count  = len(reports)
    tools_used_set = {REPORT_MAP.get(k, ("", k))[1] for k in reports if k in REPORT_MAP}
    days_active    = 1
    if user and not user.get("is_guest"):
        try:
            _created = datetime.fromisoformat(user.get("created_at", datetime.now().isoformat()))
            days_active = max(1, (datetime.now() - _created).days + 1)
        except Exception:
            days_active = 1

    section_label("Workspace Overview")
    stats_html = (
        f'<div class="ms-ws-stats">'
        f'<div class="ms-ws-stat"><div class="ws-stat-label">{_icon("archive", 14, "var(--ms-primary)")} Reports Saved</div>'
        f'<div class="ws-stat-val">{reports_count if reports_count else "—"}</div>'
        f'<div class="ws-stat-sub">in your library</div></div>'
        f'<div class="ms-ws-stat"><div class="ws-stat-label">{_icon("currency", 14, "var(--ms-primary)")} Total Earned</div>'
        f'<div class="ws-stat-val">{"₹{:,.0f}".format(total_earned) if total_earned else "—"}</div>'
        f'<div class="ws-stat-sub">from brand deals</div></div>'
        f'<div class="ms-ws-stat"><div class="ws-stat-label">{_icon("chart-bar", 14, "var(--ms-primary)")} Pending</div>'
        f'<div class="ws-stat-val">{"₹{:,.0f}".format(pending_pay) if pending_pay else "—"}</div>'
        f'<div class="ws-stat-sub">awaiting payment</div></div>'
        f'<div class="ms-ws-stat"><div class="ws-stat-label">{_icon("sparkles", 14, "var(--ms-primary)")} Tools Used</div>'
        f'<div class="ws-stat-val">{len(tools_used_set) if tools_used_set else "—"}</div>'
        f'<div class="ws-stat-sub">of 10 AI tools</div></div>'
        f'<div class="ms-ws-stat"><div class="ws-stat-label">{_icon("trending", 14, "var(--ms-primary)")} Days Active</div>'
        f'<div class="ws-stat-val">{days_active}</div>'
        f'<div class="ws-stat-sub">since you joined</div></div>'
        f'</div>'
    )
    st.markdown(stats_html, unsafe_allow_html=True)

    # ── Onboarding for brand-new creators ──
    if not has_context and not reports:
        st.markdown(
            '<div class="ms-onboard">'
            '<div class="big">Start by adding a few recent posts</div>'
            "<p>We'll learn your voice and personalise every recommendation — captions, "
            "growth tips, and brand matches that actually sound like you.</p>"
            '</div>',
            unsafe_allow_html=True,
        )
        if st.button("Set up my profile →", key="dash_setup_profile"):
            go_to("Profile")

    # ── Quick actions (large, clickable cards) ──
    section_label("Quick Actions")
    qa_cols = st.columns(len(DASH_ACTIONS))
    for i, (ico_name, title, desc, page) in enumerate(DASH_ACTIONS):
        with qa_cols[i]:
            st.markdown(
                f'<div class="ms-action">'
                f'<div class="ic">{_icon(ico_name, 26, "var(--ms-primary)")}</div>'
                f'<div class="ttl">{title}</div>'
                f'<div class="desc">{desc}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
            if st.button("Open →", key=f"qa_{page}", use_container_width=True):
                go_to(page)

    # ── Creator snapshot (emotional, not analytical) ──
    section_label("Creator Snapshot")
    glow_v, glow_t = _emotion(m.get("brand_readiness"), {
        "good": "Glowing", "warn": "Warming up", "bad": "Finding its shine", "none": "Let's begin"})
    spark_v, spark_t = _emotion(m.get("content_health"), {
        "good": "Blazing", "warn": "Kindling", "bad": "Warming up", "none": "Spark something"})
    match_v, match_t = _emotion(m.get("audience_match"), {
        "good": "In sync", "warn": "Getting closer", "bad": "Worth a look", "none": "Discover your fit"})
    energy_v, energy_t = {
        "Low": ("Recharged", "good"), "Medium": ("Steady", "warn"), "High": ("Needs rest", "bad"),
    }.get(m.get("wellness"), ("Check in", "neutral"))
    growth_done = "Growth Plan" in reports

    s = st.columns(5)
    with s[0]:
        metric_card(_icon("sparkles", 18, "var(--ms-primary)"), "Brand Glow", glow_v, "How brand-ready you feel", glow_t)
    with s[1]:
        metric_card(_icon("trending", 18, "var(--ms-primary)"), "Growth Momentum",
                    "On the rise" if growth_done else "Ready to climb",
                    "Your growth energy", "good" if growth_done else "neutral")
    with s[2]:
        metric_card(_icon("heart", 18, "var(--ms-primary)"), "Creator Energy", energy_v, "How you're doing", energy_t)
    with s[3]:
        metric_card(_icon("user", 18, "var(--ms-primary)"), "Audience Match", match_v, "You & your audience", match_t)
    with s[4]:
        metric_card(_icon("fire", 18, "var(--ms-primary)"), "Content Spark", spark_v, "Your content's pull", spark_t)

    # ── Continue working ──
    section_label("Continue Working")
    if reports:
        rw_items = list(reversed(list(reports)))[:6]
        rw_cols  = st.columns(min(len(rw_items), 3))
        for j, name in enumerate(rw_items):
            ico_name, page = REPORT_MAP.get(name, ("chart-bar", "Insights"))
            with rw_cols[j % 3]:
                st.markdown(
                    f'<div class="ms-recent-card">'
                    f'<div class="ic">{_icon(ico_name, 18, "var(--ms-primary)")}</div>'
                    f'<div class="nm">{name}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
                if st.button("Continue", key=f"rw_{name}_{j}", use_container_width=True):
                    go_to(page)
    else:
        st.markdown(
            '<div class="ms-onboard soft">'
            '<div class="big">Your creations will live here</div>'
            '<p>Run any Quick Action above and your captions, plans, and reports will appear '
            'here — so you can pick up right where you left off.</p>'
            '</div>',
            unsafe_allow_html=True,
        )


# ══════════════════════════════════════════════════════════════════════════════
# 1. CREATOR DNA / MEDIA KIT
# ══════════════════════════════════════════════════════════════════════════════
def render_creator_dna():
    with module_page("Brand DNA"):
        context_warning()
        if st.button("Generate Media Kit", type="primary", key="btn_mk"):
            text = get_context()
            if not text:
                st.warning("Add your recent posts in Settings → Profile first.")
            else:
                with st.spinner("Building your media kit…"):
                    data, raw = generate_media_kit(text)
                if data:
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Authority Score", f"{data.get('authority_score', '?')}/100")
                    c2.metric("Primary Niche", data.get("primary_niche", "—"))
                    c3.metric("Secondary Niche", data.get("secondary_niche", "—"))
                    md = media_kit_to_markdown(data)
                    st.markdown(md)
                    store_report("Media Kit", md)
                    st.session_state.metrics["creator_score"] = data.get("authority_score")
                    download_and_copy("Media Kit", md, "creator_media_kit.md")
                else:
                    st.markdown(raw)
                    store_report("Media Kit", raw)


# ══════════════════════════════════════════════════════════════════════════════
# 2. CONTENT STUDIO
# ══════════════════════════════════════════════════════════════════════════════
def render_content_studio():
    with module_page("Content Studio"):
        context_warning()
        sub_content, sub_hooks = st.tabs(["Content Plan", "Hooks, Titles & CTAs"])

        with sub_content:
            st.caption("Captions, reel hooks, and a 7-day calendar — in your voice.")
            topic_cs = st.text_input("Topic / Niche", placeholder="AI, Fitness, Productivity…", key="cs_topic")
            if st.button("Generate Content Plan", type="primary", key="btn_cs"):
                text = get_context()
                if not text:
                    st.warning("Add your recent posts in Settings → Profile first.")
                elif not topic_cs.strip():
                    st.warning("Enter a topic or niche.")
                else:
                    with st.spinner("Drafting your content plan…"):
                        plan = generate_content_plan(text, topic_cs)
                    st.markdown(plan)
                    full = f"# Content Plan — {topic_cs}\n\n{plan}"
                    store_report("Content Plan", full)
                    download_and_copy("Content Plan", full, "content_plan.md")

        with sub_hooks:
            st.caption(
                "Analyses your past posts to find what hooks work for you, "
                "then generates fresh hooks, titles, and CTAs in your voice."
            )
            topic_hk = st.text_input(
                "New post topic (optional)",
                placeholder="e.g. My morning routine, 5 budget travel tips…",
                key="hk_topic",
            )
            if st.button("Generate Hooks, Titles & CTAs", type="primary", key="btn_hk"):
                text = get_context()
                if not text:
                    st.warning("Add your recent posts in Settings → Profile first.")
                else:
                    with st.spinner("Analysing your style and generating hooks…"):
                        data, raw = generate_hooks(text, topic_hk)
                    if data:
                        st.markdown("#### 🎯 Patterns in Your Past Posts")
                        for p in data.get("patterns_identified", []):
                            st.write(f"- {p}")
                        st.markdown("#### 🪝 Generated Hooks")
                        for h in data.get("hooks", []):
                            st.markdown(f"**[{h.get('type','')}]** {h.get('hook','')}")
                        md = hooks_to_markdown(topic_hk, data)
                        with st.expander("📋 Full Report"):
                            st.markdown(md)
                        store_report("Hook Generator", md)
                        download_and_copy("Hook Generator Report", md, "hook_generator.md")
                    else:
                        st.markdown(raw)
                        store_report("Hook Generator", raw)


# ══════════════════════════════════════════════════════════════════════════════
# 3. PHOTO CAPTIONS
# ══════════════════════════════════════════════════════════════════════════════
def render_photo_captions():
    with module_page("Caption Magic"):
        photo_file = st.file_uploader("Upload a photo", type=["jpg", "jpeg", "png", "webp"], key="photo_upload")
        photo_niche = st.text_input(
            "Your niche (optional)",
            placeholder="e.g. Travel, Fashion, Fitness…",
            key="photo_niche",
        )
        if photo_file:
            st.image(photo_file, caption="Uploaded photo", width=300)

        if st.button("✨ Get Captions & Trends for This Photo", type="primary", key="btn_photo"):
            if photo_file is None:
                st.warning("Upload a photo first.")
            else:
                image_bytes = photo_file.getvalue()
                mime_type = photo_file.type or "image/jpeg"
                try:
                    with st.spinner("Analysing your photo…"):
                        data, raw, grounded = analyze_photo_for_captions(image_bytes, mime_type, photo_niche)
                except Exception as err:
                    from cip.ai import friendly_ai_error as _friendly

                    hint = _friendly(err)
                    if hint:
                        st.error(hint)
                    else:
                        st.error(
                            "⚠️ Photo analysis failed. "
                            "If this mentions a model 404, set a working model in "
                            "`.streamlit/secrets.toml` as `GEMINI_MODEL = \"...\"` and restart."
                        )
                    with st.expander("Technical details"):
                        st.code(f"{err}")
                    return
                if data:
                    st.markdown(f"**Vibe:** {data.get('mood_vibe', '')}")
                    st.markdown(f"**What we see:** {data.get('photo_description', '')}")
                    md = photo_analysis_to_markdown(data)
                    st.markdown(md)
                    caption_note = (
                        "🔎 Song suggestions powered by live web search."
                        if grounded
                        else "⚠️ Live search unavailable — song suggestions are based on general AI knowledge."
                    )
                    st.caption(caption_note)
                    store_report("Photo Caption Match", md)
                    download_and_copy("Photo Caption Match Report", md, "photo_caption_match.md")
                else:
                    st.warning("Could not parse the AI response. Raw output below:")
                    st.markdown(raw)
                    store_report("Photo Caption Match", raw)


# ══════════════════════════════════════════════════════════════════════════════
# 4. PRE-PUBLISH CHECKER
# ══════════════════════════════════════════════════════════════════════════════
def render_pre_publish():
    with module_page("Pre-Publish"):
        context_warning()
        draft_post = st.text_area(
            "Paste your draft post / caption / script",
            height=140,
            key="draft_post",
            placeholder="Write or paste the post you want to check…",
        )
        if st.button("Check My Post", type="primary", key="btn_pp"):
            if not draft_post.strip():
                st.warning("Paste a draft post first.")
            else:
                with st.spinner("Reviewing your post…"):
                    data, raw = pre_publish_check(draft_post, get_context())
                if data:
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Virality Score", f"{data.get('virality_score', '?')}/100")
                    c2.metric("Predicted Engagement", data.get("engagement_level", "—"))
                    c3.metric("Brand Safety", data.get("brand_safety_status", "—"))
                    md = pre_publish_to_markdown(draft_post, data)
                    st.markdown(md)
                    store_report("Pre-Publish Check", md)
                    st.session_state.metrics["content_health"] = data.get("virality_score")
                    st.session_state.metrics["engagement_strength"] = data.get("engagement_level")
                    download_and_copy("Pre-Publish Report", md, "pre_publish_report.md")
                else:
                    st.markdown(raw)
                    store_report("Pre-Publish Check", raw)


# ══════════════════════════════════════════════════════════════════════════════
# 5. GROWTH HUB
# ══════════════════════════════════════════════════════════════════════════════
def render_growth():
    with module_page("Growth Coach"):
        context_warning()
        sub_plan, sub_problem, sub_coach = st.tabs(["🗓️ 30-Day Growth Plan", "🧩 Problem Solver", "🤖 AI Coach"])

        with sub_plan:
            st.caption("A personalised 30-day growth strategy + monetisation roadmap.")
            topic_gh = st.text_input("Topic / Niche (optional)", placeholder="AI, Fitness, Productivity…", key="gh_topic")
            if st.button("Generate Growth Plan", type="primary", key="btn_gp"):
                text = get_context()
                if not text:
                    st.warning("Add your recent posts in Settings → Profile first.")
                else:
                    with st.spinner("Mapping out your growth plan…"):
                        growth = growth_strategy_report(text, topic_gh)
                    st.markdown(growth)
                    full = f"# 30-Day Growth Plan\n\n{growth}"
                    store_report("Growth Plan", full)
                    download_and_copy("Growth Plan", full, "growth_plan.md")

        with sub_problem:
            st.caption("Describe a specific problem — get a diagnosis and a clear action plan.")
            problem = st.text_area(
                "What's going on?",
                height=100,
                placeholder="e.g. My reach dropped 60% this month, or I keep getting ghosted by brands…",
                key="ps_problem",
            )
            if st.button("Help Me Fix This", type="primary", key="btn_ps"):
                if not problem.strip():
                    st.warning("Describe your problem first.")
                else:
                    with st.spinner("Diagnosing the issue…"):
                        data, raw = solve_problem(get_context(), problem)
                    if data:
                        st.success(f"**Quick Win:** {data.get('quick_win', '')}")
                        md = problem_solution_to_markdown(problem, data)
                        st.markdown(md)
                        store_report("Problem Solver", md)
                        download_and_copy("Problem Solution", md, "problem_solution.md")
                    else:
                        st.markdown(raw)
                        store_report("Problem Solver", raw)

        with sub_coach:
            st.caption("Ask anything about content, growth, or strategy.")
            coach_question = st.text_input("Your question", placeholder="e.g. How do I grow faster on Instagram Reels?", key="coach_q")
            if coach_question.strip():
                ctx = get_context()
                context_part = f"Creator profile:\n{ctx}\n\n" if ctx else ""
                with st.spinner("Thinking…"):
                    answer = ask_ai(f"Act as a creator coach. {context_part}Question: {coach_question}")
                st.write(answer)


# ══════════════════════════════════════════════════════════════════════════════
# 6. BRAND HUB
# ══════════════════════════════════════════════════════════════════════════════
def render_brand_hub():
    with module_page("Brand Match"):
        context_warning()
        sub_dna, sub_rep, sub_brief, sub_commerce = st.tabs([
            "🎯 Brand Fit Check",
            "🛡️ Reputation Verifier",
            "📋 Campaign Brief",
            "🛍️ Social Commerce",
        ])

        with sub_dna:
            st.caption(
                "Paste any brand's campaign brief to see how well it fits your profile — "
                "audience match, style, safety, and negotiation tips."
            )
            st.info("Your audience & platform details are pulled from your Profile (Settings → Profile). Fill that in for better results.")

            campaign_brief_dna = st.text_area(
                "Paste the brand's campaign brief / collab pitch",
                height=160,
                placeholder="Paste the email, brief, or message the brand sent you…",
                key="dna_brief",
            )
            if st.button("Run Brand Fit Check", type="primary", key="btn_dna"):
                profile = get_profile()
                if not profile.get("niche") and not profile.get("platforms"):
                    st.warning("Fill in at least your niche and platform(s) in Settings → Profile first.")
                elif not campaign_brief_dna.strip():
                    st.warning("Paste the brand's campaign brief.")
                else:
                    with st.spinner("Matching brand against your profile…"):
                        data, raw = brand_dna_match(profile, campaign_brief_dna)
                    if data:
                        verdict = data.get("overall_verdict", "—")
                        verdict_color = {"Strong Fit": "🟢", "Moderate Fit": "🟡", "Weak Fit": "🔴"}.get(verdict, "⚪")
                        c1, c2, c3, c4 = st.columns(4)
                        c1.metric("Overall Fit", f"{data.get('overall_fit_score', '?')}/100")
                        c2.metric("Audience Match", f"{data.get('audience_match_score', '?')}/100")
                        c3.metric("Style Match", f"{data.get('content_style_match_score', '?')}/100")
                        c4.metric("Brand Safety", f"{data.get('brand_safety_score', '?')}/100")
                        st.markdown(f"### Verdict: {verdict_color} {verdict}")
                        st.markdown(f"**Estimated Engagement:** {data.get('estimated_engagement_level', '—')}")
                        md = brand_dna_match_to_markdown(campaign_brief_dna, data)
                        st.markdown(md)
                        store_report("Brand Fit Check", md)
                        st.session_state.metrics["brand_readiness"] = data.get("overall_fit_score")
                        st.session_state.metrics["audience_match"] = data.get("audience_match_score")
                        download_and_copy("Brand Fit Report", md, "brand_fit_report.md")
                    else:
                        st.markdown(raw)
                        store_report("Brand Fit Check", raw)

        with sub_rep:
            st.caption("Before you sign, check the brand's reputation — controversies, payment history, community sentiment.")
            rep_brand = st.text_input(
                "Brand / company name",
                placeholder="e.g. Nykaa, Zomato, a new D2C startup…",
                key="rep_brand",
            )
            rep_details = st.text_area(
                "Deal details (optional — improves accuracy)",
                height=100,
                placeholder="e.g. ₹15,000 for 2 reels, payment after posting, no written contract yet…",
                key="rep_details",
            )
            if st.button("Check Brand Reputation", type="primary", key="btn_rep"):
                if not rep_brand.strip():
                    st.warning("Enter a brand name.")
                else:
                    with st.spinner(f"Checking reputation for {rep_brand}…"):
                        data, raw = brand_reputation_check(rep_brand.strip(), rep_details)
                    if data:
                        verdict = data.get("verdict", "—")
                        verdict_color = {"Proceed": "🟢", "Proceed with Caution": "🟡", "Avoid": "🔴"}.get(verdict, "⚪")
                        c1, c2 = st.columns(2)
                        c1.metric("Trust Score", f"{data.get('trust_score', '?')}/100")
                        c2.metric("Verdict", f"{verdict_color} {verdict}")
                        md = brand_reputation_to_markdown(rep_brand.strip(), data)
                        st.markdown(md)
                        store_report("Brand Reputation Check", md)
                        download_and_copy("Brand Reputation Report", md, "brand_reputation_report.md")
                    else:
                        st.markdown(raw)
                        store_report("Brand Reputation Check", raw)
            st.caption("⚠️ Based on AI's general knowledge — always do your own due diligence for high-value deals.")

        with sub_brief:
            st.caption("Turn a brand goal into a structured campaign brief — deliverables, timeline, KPIs.")
            brand_cb = st.text_input("Brand name", placeholder="Nike, Adidas, Notion…", key="cb_brand")
            campaign_goal = st.text_area(
                "Campaign Goal",
                height=90,
                placeholder="e.g. Drive awareness for a new product launch among Gen Z audiences…",
                key="cb_goal",
            )
            if st.button("Generate Campaign Brief", type="primary", key="btn_cb"):
                text = get_context()
                if not text:
                    st.warning("Add your recent posts in Settings → Profile first.")
                elif not brand_cb.strip():
                    st.warning("Enter a brand name.")
                elif not campaign_goal.strip():
                    st.warning("Describe the campaign goal.")
                else:
                    with st.spinner(f"Drafting brief for {brand_cb}…"):
                        data, raw = generate_campaign_brief(text, brand_cb, campaign_goal)
                    if data:
                        st.metric("Estimated Duration", f"{data.get('estimated_duration_weeks', '?')} weeks")
                        md = campaign_brief_to_markdown(brand_cb, campaign_goal, data)
                        st.markdown(md)
                        store_report("Campaign Brief", md)
                        download_and_copy("Campaign Brief", md, "campaign_brief.md")
                    else:
                        st.markdown(raw)
                        store_report("Campaign Brief", raw)

        with sub_commerce:
            st.caption("Turn a product into shoppable content — hook captions, reel concepts, and placement tips.")
            product_name = st.text_input(
                "Product / Brand to promote",
                placeholder="e.g. a skincare serum, a productivity app…",
                key="sc_product",
            )
            if st.button("Generate Shoppable Content", type="primary", key="btn_sc"):
                text = get_context()
                if not text:
                    st.warning("Add your recent posts in Settings → Profile first.")
                elif not product_name.strip():
                    st.warning("Enter a product or brand to promote.")
                else:
                    with st.spinner("Building your shoppable content plan…"):
                        data, raw = generate_shoppable_content(text, product_name)
                    if data:
                        st.metric("Conversion Score", f"{data.get('conversion_score', '?')}/100")
                        md = shoppable_content_to_markdown(product_name, data)
                        st.markdown(md)
                        store_report("Social Commerce", md)
                        download_and_copy("Shoppable Content Plan", md, "shoppable_content_plan.md")
                    else:
                        st.markdown(raw)
                        store_report("Social Commerce", raw)


# ══════════════════════════════════════════════════════════════════════════════
# 7. DEALS & REVENUE DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
def render_deals():
    with module_page("Creator Earnings"):
        # ── Add deal form ─────────────────────────────────────────────────────
        with st.expander("➕ Log a New Deal", expanded=not bool(st.session_state.deals)):
            with st.form("add_deal_form", clear_on_submit=True):
                r1c1, r1c2, r1c3 = st.columns(3)
                with r1c1:
                    deal_brand = st.text_input("Brand name *", placeholder="Nykaa, Mamaearth…")
                    deal_date  = st.date_input("Campaign date", value=date.today())
                with r1c2:
                    deal_amount  = st.number_input("Deal value (₹) *", min_value=0, step=500)
                    deal_status  = st.selectbox("Deal status", ["Completed", "In Progress", "Pending", "Cancelled"])
                with r1c3:
                    deal_payment = st.selectbox("Payment status", ["Pending", "Invoiced", "Paid", "Overdue"])
                    deal_eng     = st.number_input("Engagement (views / reach)", min_value=0, step=100)

                r2c1, r2c2 = st.columns(2)
                with r2c1:
                    deal_deliv = st.text_input("Deliverables", placeholder="2 Reels + 1 Story + 3 Feed posts")
                with r2c2:
                    deal_notes = st.text_area("Notes", height=68,
                                              placeholder="Contract link, contact name, revision terms…")

                submitted = st.form_submit_button("➕ Add Deal", type="primary", use_container_width=True)
                if submitted:
                    if not deal_brand.strip():
                        st.warning("Enter a brand name.")
                    else:
                        store_deal({
                            "brand":          deal_brand.strip(),
                            "deal_value":     deal_amount,
                            "engagement":     deal_eng,
                            "deliverables":   deal_deliv.strip(),
                            "status":         deal_status,
                            "campaign_date":  str(deal_date),
                            "payment_status": deal_payment,
                            "notes":          deal_notes.strip(),
                        })
                        st.success(f"✅ Deal with {deal_brand.strip()} logged!")

        if not st.session_state.deals:
            module_empty("Creator Earnings")
            return

        # ── Build clean DataFrame ─────────────────────────────────────────────
        _display_cols = ["Brand", "Date", "Amount (₹)", "Status", "Payment", "Engagement", "Deliverables", "Notes"]
        df = pd.DataFrame(st.session_state.deals)
        # Ensure all expected columns exist (handles both new and loaded deals)
        for col in _display_cols:
            if col not in df.columns:
                df[col] = ""
        df_display = df[_display_cols].copy()
        for _num_col in ("Amount (₹)", "Engagement"):
            df_display[_num_col] = pd.to_numeric(df_display[_num_col], errors="coerce").fillna(0)
            df[_num_col] = pd.to_numeric(df[_num_col], errors="coerce").fillna(0)
        df_completed = df[df["Status"] == "Completed"]
        df_paid      = df[df["Payment"] == "Paid"]

        # ── CRM Dashboard metrics ─────────────────────────────────────────────
        total_revenue   = float(df_completed["Amount (₹)"].sum())
        pending_revenue = float(df[df["Payment"].isin(["Pending", "Invoiced"])]["Amount (₹)"].sum())
        deals_closed    = len(df_completed)
        avg_deal_val    = float(df_completed["Amount (₹)"].mean()) if deals_closed else 0
        total_paid      = float(df_paid["Amount (₹)"].sum())

        section_label("Revenue Snapshot")
        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("Total Earned",    f"₹{total_revenue:,.0f}")
        m2.metric("Deals Closed",    deals_closed)
        m3.metric("Avg Deal Value",  f"₹{avg_deal_val:,.0f}")
        m4.metric("Pending Payments", f"₹{pending_revenue:,.0f}")
        m5.metric("Total Paid",      f"₹{total_paid:,.0f}")

        # ── Deal table ────────────────────────────────────────────────────────
        section_label(f"All Deals ({len(df)})")
        st.dataframe(df_display, use_container_width=True, hide_index=True)

        # ── Charts ────────────────────────────────────────────────────────────
        ch1, ch2 = st.columns(2)
        with ch1:
            section_label("Revenue by Brand")
            brand_rev = df_completed.groupby("Brand")["Amount (₹)"].sum().sort_values(ascending=False)
            if not brand_rev.empty:
                st.bar_chart(brand_rev)
            else:
                st.caption("No completed deals yet.")
        with ch2:
            section_label("Cumulative Revenue Over Time")
            time_df = df_completed.copy()
            if not time_df.empty:
                time_df["Date"] = pd.to_datetime(time_df["Date"], errors="coerce")
                time_df = time_df.dropna(subset=["Date"]).sort_values("Date").set_index("Date")
                if not time_df.empty:
                    st.line_chart(time_df["Amount (₹)"].cumsum().rename("Cumulative Revenue (₹)"))
            else:
                st.caption("No completed deals yet.")

        # ── Remove deal ───────────────────────────────────────────────────────
        st.divider()
        del_options = [
            f"{i}: {row['Brand']} — ₹{safe_float(row['Amount (₹)']):,.0f} ({row['Date']})"
            for i, row in df_display.iterrows()
        ]
        del_c1, del_c2 = st.columns([4, 1])
        with del_c1:
            del_choice = st.selectbox("Select a deal to remove", del_options, key="deal_del_choice")
        with del_c2:
            st.write("")
            if st.button("🗑️ Remove", key="btn_del_deal"):
                idx = int(del_choice.split(":")[0])
                delete_deal_by_idx(idx)
                st.rerun()

        # ── Save summary to library ───────────────────────────────────────────
        deal_lines = "\n".join(
            f"- **{r['Brand']}** ({r['Date']}) — ₹{safe_float(r['Amount (₹)']):,.0f} | "
            f"Status: {r['Status']} | Payment: {r['Payment']} | "
            f"Engagement: {safe_float(r['Engagement']):,.0f} | Deliverables: {r['Deliverables'] or 'N/A'}"
            for _, r in df_display.iterrows()
        )
        deals_md = (
            f"# Creator Earnings CRM\n\n"
            f"- Total Earned (Completed): ₹{total_revenue:,.0f}\n"
            f"- Deals Closed: {deals_closed}\n"
            f"- Avg Deal Value: ₹{avg_deal_val:,.0f}\n"
            f"- Pending Payments: ₹{pending_revenue:,.0f}\n"
            f"- Total Paid: ₹{total_paid:,.0f}\n\n"
            f"## Deal Log\n{deal_lines}\n"
        )
        store_report("Deals & Revenue Summary", deals_md)
        download_and_copy("Deals & Revenue Summary", deals_md, "deals_revenue_summary.md")


# ══════════════════════════════════════════════════════════════════════════════
# 8. WELLBEING COACH
# ══════════════════════════════════════════════════════════════════════════════
def render_wellbeing():
    with module_page("Wellbeing"):
        sub_coach_wb, sub_burnout, sub_fake = st.tabs([
            "🧘 Wellbeing Check-In",
            "🧠 Burnout Predictor",
            "🔍 Fake Audience Detector",
        ])

        with sub_coach_wb:
            st.caption("A supportive check-in on burnout signs, handling negativity, and sustainable routines.")
            context_warning()
            if st.button("Run Wellbeing Check-In", type="primary", key="btn_wb"):
                text = get_context()
                if not text:
                    st.warning("Add your recent posts in Settings → Profile first.")
                else:
                    with st.spinner("Reflecting on your content…"):
                        checkin = wellbeing_checkin(text)
                    st.markdown(checkin)
                    full = f"# Wellbeing Check-In\n\n{checkin}"
                    store_report("Wellbeing Check-In", full)
                    download_and_copy("Wellbeing Check-In", full, "wellbeing_checkin.md")
            st.caption("Supportive guidance only — not a substitute for professional mental health care.")

        with sub_burnout:
            st.caption("A quick self-check based on posting habits, energy, and engagement trends.")
            b1, b2 = st.columns(2)
            with b1:
                bo_posts = st.number_input("Posts per week", min_value=0, max_value=50, value=5, key="bo_posts")
                bo_freq = st.selectbox(
                    "Posting frequency change recently",
                    ["Stayed about the same", "Increased a lot", "Increased slightly", "Decreased slightly", "Decreased a lot / stopped"],
                    key="bo_freq",
                )
                bo_energy = st.slider("Energy/motivation for creating (1 = drained, 10 = excited)", 1, 10, 6, key="bo_energy")
                bo_hours = st.number_input("Hours on content per day", min_value=0.0, max_value=24.0, value=2.0, step=0.5, key="bo_hours")
            with b2:
                bo_eng_trend = st.selectbox(
                    "Engagement trend last month",
                    ["Increasing", "Stable", "Slightly declining", "Dropped significantly"],
                    key="bo_eng_trend",
                )
                bo_negativity = st.selectbox(
                    "Negative comments / hate frequency",
                    ["Rare", "Occasional", "Frequent", "Constant"],
                    key="bo_negativity",
                )
                bo_break = st.number_input("Days since last full break day", min_value=0, max_value=365, value=7, key="bo_break")

            bo_notes = st.text_area(
                "Anything else on your mind? (optional)",
                height=80,
                placeholder="e.g. Feeling pressure to post daily, comparing myself to others…",
                key="bo_notes",
            )
            if st.button("Check My Burnout Risk", type="primary", key="btn_burnout"):
                profile = {
                    "posts_per_week": bo_posts,
                    "frequency_change": bo_freq,
                    "energy_level": bo_energy,
                    "engagement_trend": bo_eng_trend,
                    "hours_per_day": bo_hours,
                    "negativity_level": bo_negativity,
                    "days_since_break": bo_break,
                    "notes": bo_notes,
                }
                with st.spinner("Reviewing your habits…"):
                    data, raw = predict_burnout(profile)
                if data:
                    risk = data.get("burnout_risk", "—")
                    risk_color = {"Low": "🟢", "Medium": "🟡", "High": "🔴"}.get(risk, "⚪")
                    c1, c2 = st.columns(2)
                    c1.metric("Burnout Risk", f"{risk_color} {risk}")
                    c2.metric("Risk Score", f"{data.get('risk_score', '?')}/100")
                    md = burnout_to_markdown(data)
                    st.markdown(md)
                    store_report("Burnout Predictor", md)
                    st.session_state.metrics["wellness"] = data.get("burnout_risk")
                    download_and_copy("Burnout Prediction Report", md, "burnout_prediction.md")
                else:
                    st.markdown(raw)
                    store_report("Burnout Predictor", raw)
            st.caption("Supportive guidance only — not a clinical assessment.")

        with sub_fake:
            st.caption("Analyse followers and comments for bots, spam, and fake engagement. No password needed.")
            st.info(
                "**How to get your data:**\n"
                "- **Instagram:** Settings → Your activity → Download your information\n"
                "- **YouTube:** YouTube Studio → Analytics; paste stats + copy recent comments\n\n"
                "You can also paste a sample of follower usernames or comments directly."
            )
            fa_col1, fa_col2 = st.columns(2)
            with fa_col1:
                fa_platform = st.selectbox("Platform", ["Instagram", "YouTube"], key="fa_platform")
            with fa_col2:
                fa_username = st.text_input("Your Username / Handle", placeholder="@yourcreatorname", key="fa_username")

            st.markdown("#### Engagement Stats (optional)")
            fa_stats = st.text_area(
                "Follower count, avg likes, avg comments, growth rate, etc.",
                height=90,
                placeholder="e.g. Followers: 85,000 | Avg Likes: 420 | Avg Comments: 12 | Gained 4,000 last month with no viral post",
                key="fa_stats",
            )
            st.markdown("#### Follower Sample (optional)")
            fa_followers = st.text_area(
                "Follower usernames (one per line or comma-separated)",
                height=110,
                placeholder="user_xjk829\njohn_fitness_real\nfollower_bot_99\n…",
                key="fa_followers",
            )
            st.markdown("#### Comment Sample")
            fa_comments = st.text_area(
                "Recent comments",
                height=150,
                placeholder="Nice post!\nFollow me back @spamuser123\nThis really helped me, thanks!\nF4F?\n…",
                key="fa_comments",
            )

            run_follower = bool(fa_stats.strip() or fa_followers.strip())
            run_comment = bool(fa_comments.strip())

            if not fa_username.strip():
                st.warning("Enter your username to run the analysis.")
            elif not run_follower and not run_comment:
                st.warning("Paste at least some stats, follower names, or comments to analyse.")
            else:
                if st.button("🔍 Run Fake Audience Analysis", type="primary", key="btn_fake"):
                    follower_result = comment_result = None
                    platform_clean = fa_platform
                    username_clean = fa_username.strip().lstrip("@")

                    if run_follower:
                        with st.spinner("Analysing follower authenticity…"):
                            follower_result, raw_f = analyze_fake_followers(
                                platform_clean, username_clean, fa_followers.strip(), fa_stats.strip()
                            )
                        if follower_result:
                            risk = follower_result.get("fake_follower_risk", "?")
                            risk_color = {"Low": "🟢", "Medium": "🟡", "High": "🔴"}.get(risk, "⚪")
                            c1, c2, c3 = st.columns(3)
                            c1.metric("Authenticity Score", f"{follower_result.get('authenticity_score', '?')}/100")
                            c2.metric("Fake Follower Risk", f"{risk_color} {risk}")
                            c3.metric("Est. Fake %", f"~{follower_result.get('estimated_fake_percentage', '?')}%")
                        else:
                            st.warning("Could not parse follower analysis.")
                            st.code(raw_f)

                    if run_comment:
                        with st.spinner("Scanning comments for bots and spam…"):
                            comment_result, raw_c = analyze_fake_comments(
                                platform_clean, username_clean, fa_comments.strip()
                            )
                        if comment_result:
                            cq1, cq2, cq3 = st.columns(3)
                            cq1.metric("Comment Quality", f"{comment_result.get('comment_quality_score', '?')}/100")
                            cq2.metric("Bot Comments", f"{comment_result.get('bot_comment_percentage', '?')}%")
                            cq3.metric("Genuine Comments", f"{comment_result.get('genuine_comment_percentage', '?')}%")
                        else:
                            st.warning("Could not parse comment analysis.")
                            st.code(raw_c)

                    if follower_result or comment_result:
                        md = fake_audience_to_markdown(platform_clean, username_clean, follower_result, comment_result)
                        st.divider()
                        st.markdown(md)
                        store_report("Fake Audience Analysis", md)
                        download_and_copy("Fake Audience Report", md, "fake_audience_report.md")

            st.caption(
                "⚠️ AI-based pattern recognition — not direct API access. Results are indicative. "
                "For deeper audits, cross-reference with HypeAuditor or Modash."
            )


# ══════════════════════════════════════════════════════════════════════════════
# 9. TRENDS
# ══════════════════════════════════════════════════════════════════════════════
def render_trends():
    with module_page("Trends"):
        tr1, tr2 = st.columns(2)
        with tr1:
            trends_niche = st.text_input(
                "Your niche (optional)",
                placeholder="e.g. Fitness, Tech, Comedy, Beauty…",
                key="trends_niche",
                value=st.session_state.get("g_niche", ""),
            )
        with tr2:
            trends_platform = st.selectbox(
                "Platform focus",
                ["All Platforms", "Instagram", "YouTube", "TikTok", "X (Twitter)"],
                key="trends_platform",
            )

        if st.button("🔄 Get Latest Trends", type="primary", key="btn_trends"):
            platform_arg = None if trends_platform == "All Platforms" else trends_platform
            with st.spinner("Pulling the latest trends…"):
                text, grounded = generate_trends_report(trends_niche.strip(), platform_arg)
            st.markdown(text)
            st.caption(
                "🔎 Powered by live web search."
                if grounded
                else "⚠️ Live search unavailable — based on AI's general knowledge, may not reflect very latest trends."
            )
            full_md = f"# Trends Hub Briefing\n\n{text}"
            store_report("Trends Hub", full_md)
            download_and_copy("Trends Briefing", full_md, "trends_hub.md")
        else:
            module_empty("Trends")


# ══════════════════════════════════════════════════════════════════════════════
# 10. REPORTS
# ══════════════════════════════════════════════════════════════════════════════
def render_reports():
    with module_page("Insights"):
        if not st.session_state.reports:
            module_empty("Insights")
        else:
            section_label("Included Sections")
            cols = st.columns(3)
            for i, name in enumerate(st.session_state.reports):
                with cols[i % 3]:
                    metric_card("📄", name, "Ready", "Saved this session", "accent")

            st.write("")
            combined = "\n\n---\n\n".join(st.session_state.reports.values())
            full_md = f"# Muse Report\n\n{combined}"

            st.download_button(
                "⬇️ Download Full Report (.md)",
                full_md,
                file_name="creator_intelligence_report.md",
                mime="text/markdown",
                type="primary",
            )
            with st.expander("📋 Copy full report"):
                st.code(full_md, language="markdown")
            with st.expander("Preview Full Report"):
                st.markdown(full_md)

            if st.button("🗑️ Clear all reports", type="secondary", key="btn_clear"):
                st.session_state.reports = {}
                st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# SETTINGS — PROFILE (moved out of the sidebar into its own page)
# ══════════════════════════════════════════════════════════════════════════════
def render_profile():
    from cip.auth.auth import current_user
    from cip.database.db import save_profile as _db_save_profile

    user = current_user()
    is_guest = not user or user.get("is_guest")

    with module_page("Profile"):

        # ── Muse Memory showcase ──────────────────────────────────────────────
        niche     = st.session_state.get("g_niche", "")
        platforms = st.session_state.get("g_platforms", [])
        tone      = st.session_state.get("g_tone", [])
        posts     = st.session_state.get("global_posts", "")
        followers = st.session_state.get("g_followers", "")
        age       = st.session_state.get("g_age", "")
        geo       = st.session_state.get("g_geo", "")
        gender    = st.session_state.get("g_gender", "")
        has_memory = bool(niche or platforms or posts.strip())

        def _mm_item(key, val):
            return (
                f'<div class="mm-item">'
                f'<span class="mm-key">{key}</span>'
                f'<span class="mm-val">{val}</span>'
                f'</div>'
            )

        if has_memory:
            items_html = ""
            if niche:           items_html += _mm_item("Niche", niche)
            if platforms:       items_html += _mm_item("Platforms", " · ".join(platforms))
            if tone:            items_html += _mm_item("Voice & Tone", ", ".join(tone))
            if followers:       items_html += _mm_item("Followers", followers)
            if age:             items_html += _mm_item("Audience Age", age)
            if gender:          items_html += _mm_item("Gender Split", gender)
            if geo:             items_html += _mm_item("Geography", geo)
            post_count = len([l for l in posts.strip().split("\n") if l.strip()])
            from cip.ui import icon as _icon
            if posts.strip(): items_html += _mm_item("Recent Posts", f"Loaded — {post_count} lines")
            _brain_svg = _icon("sparkles", 22, "#fff")
            st.markdown(
                '<div class="ms-memory-card">'
                '<div class="mm-header">'
                f'<div class="mm-brain">{_brain_svg}</div>'
                '<div><div class="mm-title">Muse Memory</div>'
                '<div class="mm-sub">What your AI knows about you — used in every tool</div></div>'
                '<div class="mm-status active">Active</div>'
                '</div>'
                f'<div class="mm-items">{items_html}</div>'
                '</div>',
                unsafe_allow_html=True,
            )
        else:
            from cip.ui import icon as _icon
            _brain_svg = _icon("sparkles", 22, "#fff")
            st.markdown(
                '<div class="ms-memory-card">'
                '<div class="mm-header">'
                f'<div class="mm-brain">{_brain_svg}</div>'
                '<div><div class="mm-title">Muse Memory</div>'
                '<div class="mm-sub">Fill in your profile and Muse will remember everything</div></div>'
                '<div class="mm-status empty">Empty</div>'
                '</div>'
                '<div class="mm-items">'
                '<div class="mm-item"><span class="mm-key">Status</span>'
                '<span class="mm-val">Complete your profile below to activate</span></div>'
                '</div></div>',
                unsafe_allow_html=True,
            )

        st.divider()

        # ── Identity ──────────────────────────────────────────────────────────
        st.markdown("#### Creator Identity")
        id1, id2, id3 = st.columns(3)
        with id1:
            st.text_input("Handle / username", placeholder="@yourhandle", key="g_username")
        with id2:
            st.text_input("Niche / category", placeholder="Fitness, Tech, Comedy…", key="g_niche")
        with id3:
            st.text_input("Follower count", placeholder="e.g. 85,000", key="g_followers")
        st.text_area(
            "Bio / tagline",
            height=80,
            placeholder="Creative entrepreneur helping people build in public…",
            key="g_bio",
        )

        # ── Voice & Audience ──────────────────────────────────────────────────
        st.markdown("#### Voice, Platform & Audience")
        p1, p2 = st.columns(2)
        with p1:
            st.multiselect(
                "Platform(s)",
                ["Instagram", "YouTube", "TikTok", "X (Twitter)", "LinkedIn", "Facebook"],
                key="g_platforms",
            )
            st.text_input("Avg engagement rate", placeholder="e.g. 4.5%", key="g_engagement")
            st.text_input("Audience age range", placeholder="e.g. 18–25", key="g_age")
            st.text_input("Audience geography", placeholder="e.g. India, Gulf, US", key="g_geo")
        with p2:
            st.multiselect(
                "Content tone / style",
                ["Educational", "Comedy", "Aesthetic/Luxury", "Motivational", "Raw/Authentic", "Edgy/Bold", "Family-friendly"],
                key="g_tone",
            )
            st.text_input("Audience gender split", placeholder="e.g. 60% F / 40% M", key="g_gender")
            st.text_input("Past brand collabs", placeholder="e.g. local skincare, fitness app", key="g_past_brands")
            st.text_area("Will NOT promote", height=68, placeholder="e.g. No gambling, no alcohol…", key="g_no_go")

        # ── Goals ─────────────────────────────────────────────────────────────
        st.markdown("#### Goals & Content Style")
        g1, g2 = st.columns(2)
        with g1:
            st.text_area(
                "Creator goals",
                height=80,
                placeholder="Reach 100K by Dec, land 5 brand deals, launch merch…",
                key="g_goals",
            )
        with g2:
            st.text_area(
                "Content style notes",
                height=80,
                placeholder="Short-form reels, educational carousels, storytelling vlogs…",
                key="g_content_style",
            )

        # ── Recent posts (AI context) ─────────────────────────────────────────
        st.markdown("#### Recent Posts (AI Context)")
        st.text_area(
            "Paste 5–10 recent captions or scripts",
            height=160,
            placeholder="Paste captions, scripts, or recent posts — Muse learns your voice from these…",
            key="global_posts",
        )

        # ── Save ─────────────────────────────────────────────────────────────
        if is_guest:
            st.info("👤 Guest mode — create a free account to save your profile and keep Muse Memory across sessions.")
        else:
            if st.button("💾  Save Profile & Update Memory", type="primary", key="btn_save_profile"):
                _db_save_profile(user["id"], {
                    "bio":           st.session_state.get("g_bio", ""),
                    "username":      st.session_state.get("g_username", ""),
                    "niche":         st.session_state.get("g_niche", ""),
                    "platforms":     st.session_state.get("g_platforms", []),
                    "followers":     st.session_state.get("g_followers", ""),
                    "engagement":    st.session_state.get("g_engagement", ""),
                    "age_range":     st.session_state.get("g_age", ""),
                    "gender_split":  st.session_state.get("g_gender", ""),
                    "geography":     st.session_state.get("g_geo", ""),
                    "tone":          st.session_state.get("g_tone", []),
                    "past_brands":   st.session_state.get("g_past_brands", ""),
                    "no_go":         st.session_state.get("g_no_go", ""),
                    "recent_posts":  st.session_state.get("global_posts", ""),
                    "goals":         st.session_state.get("g_goals", ""),
                    "content_style": st.session_state.get("g_content_style", ""),
                })
                st.success("✅ Profile saved! Muse Memory updated — every AI tool now knows you better.")


# ══════════════════════════════════════════════════════════════════════════════
# MY LIBRARY
# ══════════════════════════════════════════════════════════════════════════════
_LIB_ICONS = {
    "Brand DNA": "sparkles", "Content": "pen",     "Captions": "photo",
    "Pre-Publish": "shield", "Growth": "trending", "Brand": "link",
    "Earnings": "currency",  "Wellbeing": "heart",  "Trends": "fire",
    "General": "chart-bar",
}


def render_library():
    from cip.auth.auth import current_user
    from cip.database.db import get_reports as _db_reports, delete_report as _db_del
    from datetime import datetime as _dt

    user = current_user()
    is_guest = not user or user.get("is_guest")

    with module_page("Library"):
        if is_guest:
            st.markdown(
                '<div class="ms-plan-gate">'
                '<strong>My Library</strong> saves every report forever. '
                'Create a free account to unlock all features.'
                '</div>',
                unsafe_allow_html=True,
            )
            st.caption("Previewing this session's temporary reports:")
            if st.session_state.reports:
                for title, content in reversed(list(st.session_state.reports.items())):
                    with st.expander(title):
                        st.markdown(content)
            return

        # ── Fetch once ────────────────────────────────────────────────────────
        all_rows = _db_reports(user["id"])

        # ── Filter bar ────────────────────────────────────────────────────────
        type_opts = ["All"] + sorted({r["type"] for r in all_rows})
        fc1, fc2 = st.columns([3, 1])
        with fc1:
            search = st.text_input("Search", placeholder="Growth, Caption, Brand…", key="lib_search",
                                   label_visibility="collapsed")
        with fc2:
            ftype = st.selectbox("Type", type_opts, key="lib_type", label_visibility="collapsed")

        db_rows = all_rows
        if ftype and ftype != "All":
            db_rows = [r for r in db_rows if r["type"] == ftype]
        if search.strip():
            q = search.strip().lower()
            db_rows = [r for r in db_rows if q in r["title"].lower() or q in r["content"].lower()]

        if not db_rows:
            st.markdown(
                '<div class="ms-empty" style="background:linear-gradient(135deg,rgba(255,126,182,.10),'
                'rgba(249,168,38,.07));border:1px dashed rgba(255,126,182,.35)">'
                '<div class="bubble" style="background:linear-gradient(135deg,rgba(255,126,182,.24),'
                'rgba(249,168,38,.16))">No reports yet</div>'
                '<div class="txt"><div class="et">Your library is empty</div>'
                '<p>Generate any report and it will live here forever — searchable, downloadable, shareable.</p>'
                '</div></div>',
                unsafe_allow_html=True,
            )
            return

        section_label(f"{len(db_rows)} saved item{'s' if len(db_rows)!=1 else ''}")

        # ── Card grid ─────────────────────────────────────────────────────────
        from cip.ui import icon as _icon
        cards_html = ""
        for r in db_rows:
            ico_name = _LIB_ICONS.get(r["type"], "chart-bar")
            ico_svg  = _icon(ico_name, 14, "var(--ms-primary)")
            try:
                dt = _dt.fromisoformat(r["created_at"]).strftime("%b %d, %Y · %H:%M")
            except Exception:
                dt = str(r["created_at"])[:16]
            cards_html += (
                f'<div class="ms-lib-card">'
                f'<div class="lc-type">{ico_svg} {r["type"]}</div>'
                f'<div class="lc-title">{r["title"]}</div>'
                f'<div class="lc-date">Saved {dt}</div>'
                f'</div>'
            )
        st.markdown(f'<div class="ms-lib-grid">{cards_html}</div>', unsafe_allow_html=True)
        st.write("")

        # ── Per-report actions ────────────────────────────────────────────────
        titles = [r["title"] for r in db_rows]
        sel_title = st.selectbox("Select a report", titles, key="lib_sel", label_visibility="collapsed")
        sel_row   = next((r for r in db_rows if r["title"] == sel_title), None)

        if sel_row:
            section_label(sel_row["title"])
            act1, act2, act3 = st.columns([2, 2, 1])
            with act1:
                st.download_button(
                    "⬇️ Download (.md)",
                    sel_row["content"],
                    file_name=f"{sel_row['title'].lower().replace(' ','_')}.md",
                    mime="text/markdown",
                    key="lib_dl",
                    use_container_width=True,
                )
            with act2:
                with st.expander("👁️ Preview report"):
                    st.markdown(sel_row["content"])
            with act3:
                if st.button("🗑️ Delete", key="lib_del", type="secondary", use_container_width=True):
                    _db_del(sel_row["id"], user["id"])
                    st.session_state.reports.pop(sel_row["title"], None)
                    st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# SETTINGS PAGE
# ══════════════════════════════════════════════════════════════════════════════
_PLAN_FEATURES = {
    "Free": {
        "price": "₹0",
        "period": "forever",
        "features": [
            "All 10 AI tools",
            "Generate unlimited reports",
            "Caption Magic",
            "Growth Coach",
            "Trends Briefing",
        ],
    },
    "Pro": {
        "price": "₹499",
        "period": "/month",
        "features": [
            "Everything in Free",
            "Saved report library",
            "Muse Memory Engine",
            "Advanced Brand Analytics",
            "Priority AI responses",
            "Export to PDF",
        ],
    },
    "Agency": {
        "price": "₹1,999",
        "period": "/month",
        "features": [
            "Everything in Pro",
            "Up to 5 creator workspaces",
            "Team collaboration",
            "White-label reports",
            "Dedicated support",
        ],
    },
}


def render_settings():
    from cip.auth.auth import current_user, logout
    from cip.database.db import update_user_account

    user = current_user()
    is_guest = not user or user.get("is_guest")

    with module_page("Settings"):
        tab_account, tab_plan, tab_data = st.tabs(
            ["👤 Account", "💳 Plan & Billing", "🗄️ Data & Privacy"]
        )

        with tab_account:
            if is_guest:
                st.info("Create a free account to manage your settings.")
                return

            st.markdown("#### Account Details")
            a1, a2 = st.columns(2)
            with a1:
                new_name = st.text_input(
                    "Display Name",
                    value=user.get("name", ""),
                    key="settings_name",
                )
                st.text_input("Email", value=user.get("email", ""), disabled=True, key="settings_email")
            with a2:
                new_avatar = st.text_input("Avatar Emoji", value=user.get("avatar", "✨"), key="settings_avatar")
                st.caption("Use any emoji as your avatar.")

            if st.button("Save Account Changes", type="primary", key="settings_save_acct"):
                if not new_name.strip():
                    st.warning("Display name cannot be empty.")
                else:
                    update_user_account(user["id"], new_name, new_avatar)
                    st.session_state["user"]["name"] = new_name.strip()
                    st.session_state["user"]["avatar"] = new_avatar
                    st.success("✅ Account updated!")

            st.divider()
            st.markdown("#### Danger Zone")
            if st.button("🚪  Sign Out", key="settings_logout"):
                logout()

        with tab_plan:
            current_plan = user.get("plan", "free") if user else "free"
            cols = st.columns(3)
            for i, (plan_name, info) in enumerate(_PLAN_FEATURES.items()):
                is_current = plan_name.lower() == current_plan
                with cols[i]:
                    feat_html = "".join(f"<li>{f}</li>" for f in info["features"])
                    st.markdown(
                        f'<div class="ms-plan-card {"current" if is_current else ""}">'
                        f'<div class="pc-name">{plan_name}</div>'
                        f'<div class="pc-price">{info["price"]}<span> {info["period"]}</span></div>'
                        f'<ul>{feat_html}</ul>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )
                    if is_current:
                        st.button("✓ Current Plan", disabled=True, key=f"plan_{plan_name}", use_container_width=True)
                    else:
                        if st.button(f"Upgrade to {plan_name}", key=f"plan_{plan_name}", use_container_width=True, type="primary"):
                            st.info("💳 Payment integration coming soon. This is a hackathon demo!")

        with tab_data:
            if is_guest:
                return
            st.markdown("#### Export Your Data")
            reports = st.session_state.get("reports", {})
            if reports:
                combined = "\n\n---\n\n".join(reports.values())
                st.download_button(
                    "⬇️ Export All Reports (.md)",
                    combined,
                    file_name="Muse_export.md",
                    mime="text/markdown",
                    type="primary",
                )
            else:
                st.caption("No reports to export yet.")

            st.divider()
            st.markdown("#### Privacy")
            st.info(
                "Muse stores your profile and reports locally in a SQLite database "
                "on the server running this app. No data is shared with third parties. "
                "AI queries are sent to Google Gemini."
            )


# ══════════════════════════════════════════════════════════════════════════════
# ONBOARDING WIZARD (first-time users only)
# ══════════════════════════════════════════════════════════════════════════════

def render_onboarding():
    from cip.auth.auth import current_user, complete_onboarding
    from cip.database.db import save_profile as _db_save_profile

    user = current_user()
    if not user:
        return

    step = st.session_state.get("onboarding_step", 0)
    total = 4

    # ── Progress stepper ──────────────────────────────────────────────────────
    dots = "".join(
        f'<div class="dot {"active" if i == step else "done" if i < step else ""}"></div>'
        for i in range(total)
    )
    st.markdown(f'<div class="ms-stepper">{dots}</div>', unsafe_allow_html=True)

    # ── Steps ─────────────────────────────────────────────────────────────────
    if step == 0:
        import html as _html

        st.markdown(
            '<div class="ms-onboard-step">'
            '<div class="step-emoji">✨</div>'
            f'<div class="step-title">Welcome to {BRAND_NAME},<br>{_html.escape(safe_first_name(user.get("name", "Creator")))}!</div>'
            '<div class="step-sub">Your creative growth companion. '
            'Let\'s spend 60 seconds setting up your workspace so every tool works perfectly for you.</div>'
            '</div>',
            unsafe_allow_html=True,
        )
        if st.button("Let's get started →", type="primary", key="ob0", use_container_width=False):
            st.session_state["onboarding_step"] = 1
            st.rerun()

    elif step == 1:
        st.markdown(
            '<div class="ms-onboard-step">'
            '<div class="step-emoji">🎨</div>'
            '<div class="step-title">Tell us about your content</div>'
            '<div class="step-sub">This helps Muse personalise every recommendation for your niche and audience.</div>'
            '</div>',
            unsafe_allow_html=True,
        )
        ob_niche = st.text_input("What's your niche?", placeholder="Fitness, Tech, Travel, Beauty…", key="ob_niche")
        ob_platforms = st.multiselect(
            "Which platforms are you on?",
            ["Instagram", "YouTube", "TikTok", "X (Twitter)", "LinkedIn", "Facebook"],
            key="ob_platforms",
        )
        ob_followers = st.text_input("Approx. followers", placeholder="e.g. 12,000 or 'just starting'", key="ob_followers")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("← Back", key="ob1b"):
                st.session_state["onboarding_step"] = 0
                st.rerun()
        with c2:
            if st.button("Continue →", type="primary", key="ob1"):
                st.session_state["ob_niche_val"] = ob_niche
                st.session_state["ob_platforms_val"] = ob_platforms
                st.session_state["ob_followers_val"] = ob_followers
                st.session_state["g_niche"] = ob_niche
                st.session_state["g_platforms"] = ob_platforms
                st.session_state["g_followers"] = ob_followers
                st.session_state["onboarding_step"] = 2
                st.rerun()

    elif step == 2:
        st.markdown(
            '<div class="ms-onboard-step">'
            '<div class="step-emoji">📝</div>'
            '<div class="step-title">Paste a few recent captions</div>'
            '<div class="step-sub">Muse learns your voice from your own posts — '
            'so every suggestion sounds exactly like you. You can always update these later.</div>'
            '</div>',
            unsafe_allow_html=True,
        )
        ob_posts = st.text_area(
            "Your recent posts (5–10 is ideal)",
            height=180,
            placeholder="Paste captions, scripts, or anything you've posted recently…",
            key="ob_posts",
        )
        c1, c2 = st.columns(2)
        with c1:
            if st.button("← Back", key="ob2b"):
                st.session_state["onboarding_step"] = 1
                st.rerun()
        with c2:
            if st.button("Continue →", type="primary", key="ob2"):
                st.session_state["global_posts"] = ob_posts
                st.session_state["onboarding_step"] = 3
                st.rerun()

    elif step == 3:
        st.markdown(
            '<div class="ms-onboard-step">'
            '<div class="step-emoji">🚀</div>'
            '<div class="step-title">You\'re all set!</div>'
            '<div class="step-sub">Your workspace is ready. All 10 AI tools are personalised '
            'and waiting for you. Let\'s start creating.</div>'
            '</div>',
            unsafe_allow_html=True,
        )
        c1, c2 = st.columns(2)
        with c1:
            if st.button("← Back", key="ob3b"):
                st.session_state["onboarding_step"] = 2
                st.rerun()
        with c2:
            if st.button("🚀  Launch My Workspace", type="primary", key="ob3"):
                # Save profile to DB
                _db_save_profile(user["id"], {
                    "niche":        st.session_state.get("ob_niche_val", ""),
                    "platforms":    st.session_state.get("ob_platforms_val", []),
                    "followers":    st.session_state.get("ob_followers_val", ""),
                    "recent_posts": st.session_state.get("global_posts", ""),
                })
                # Clean up temp keys
                for k in ["ob_niche_val", "ob_platforms_val", "ob_followers_val", "onboarding_step"]:
                    st.session_state.pop(k, None)
                complete_onboarding(user["id"])


# ══════════════════════════════════════════════════════════════════════════════
# ROUTER
# ══════════════════════════════════════════════════════════════════════════════
ROUTES = {
    "Dashboard":       render_dashboard,
    "Caption Magic":   render_photo_captions,
    "Content Studio":  render_content_studio,
    "Pre-Publish":     render_pre_publish,
    "Growth Coach":    render_growth,
    "Brand Match":     render_brand_hub,
    "Brand DNA":       render_creator_dna,
    "Insights":        render_reports,
    "Creator Earnings": render_deals,
    "Wellbeing":       render_wellbeing,
    "Trends":          render_trends,
    "Profile":         render_profile,
    "Library":         render_library,
    "Settings":        render_settings,
    "Onboarding":      render_onboarding,
}


def render_page():
    page = st.session_state.get("page", "Dashboard")
    ROUTES.get(page, render_dashboard)()


