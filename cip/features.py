"""Feature generation + markdown formatting functions.

BUSINESS LOGIC — preserved verbatim from the original app. AI prompts, JSON
schemas, API calls, and data processing must not be modified here.
"""
import json

from google.genai import types

from .ai import ask_ai, ask_ai_with_search, ask_ai_json, get_client, generate_with_fallback


# ── Media Kit ─────────────────────────────────────────────────────────────────
def generate_media_kit(text):
    prompt = (
        f"Build a one-page creator media kit. JSON schema:\n"
        f'{{"authority_score": int, "primary_niche": string, "secondary_niche": string, '
        f'"style_summary": string, "creator_dna": string, "audience_persona": string, '
        f'"swot": {{"strengths": [string], "weaknesses": [string], "opportunities": [string], "threats": [string]}}}}\n\n'
        f"Creator content:\n{text}"
    )
    return ask_ai_json(prompt)


def media_kit_to_markdown(data):
    swot = data.get("swot", {})

    def bullets(items):
        return "\n".join(f"- {i}" for i in items) if items else "- N/A"

    return (
        f"# Creator Media Kit\n\n"
        f"## Style Snapshot\n{data.get('style_summary', '')}\n\n"
        f"## Creator DNA\n{data.get('creator_dna', '')}\n\n"
        f"## Audience Persona\n{data.get('audience_persona', '')}\n\n"
        f"## Niche & Authority\n"
        f"- Primary Niche: {data.get('primary_niche', '')}\n"
        f"- Secondary Niche: {data.get('secondary_niche', '')}\n"
        f"- Authority Score: {data.get('authority_score', '?')}/100\n\n"
        f"## SWOT\n### Strengths\n{bullets(swot.get('strengths'))}\n\n"
        f"### Weaknesses\n{bullets(swot.get('weaknesses'))}\n\n"
        f"### Opportunities\n{bullets(swot.get('opportunities'))}\n\n"
        f"### Threats\n{bullets(swot.get('threats'))}\n"
    )


# ── Content Studio ────────────────────────────────────────────────────────────
def generate_content_plan(text, topic):
    return ask_ai(
        f"Using the creator's writing style below, create a content plan for '{topic}'.\n\n"
        f"## Caption Ideas\n5 ready-to-post captions in the creator's voice.\n\n"
        f"## Reel / Short-Form Concepts\n3 hooks + one-line concept each.\n\n"
        f"## 7-Day Content Calendar\nDay 1–7 with idea + format per day.\n\n"
        f"Creator style:\n{text}"
    )


def generate_hooks(text, topic):
    topic_part = f" for a new post about '{topic}'" if topic.strip() else " for new posts in the same style"
    prompt = (
        f"Analyse the creator's past posts/captions to identify hook patterns, titles, and CTAs, "
        f"then generate fresh ones{topic_part}. JSON schema:\n"
        f'{{"patterns_identified": [string], '
        f'"hooks": [{{"hook": string, "type": string}}], '
        f'"titles": [string], "ctas": [string]}}\n\n'
        f"Generate 8 hooks (types: Curiosity, Bold Claim, Relatable Pain Point, Question, Story Opener, "
        f"Controversy, Stat/Number, Challenge), 6 titles, and 6 CTAs.\n\n"
        f"Creator's past posts:\n{text}"
    )
    return ask_ai_json(prompt)


def hooks_to_markdown(topic, data):
    def bullets(items):
        return "\n".join(f"- {i}" for i in items) if items else "- N/A"

    hooks = data.get("hooks", [])
    hooks_md = "\n".join(f"- **[{h.get('type','')}]** {h.get('hook','')}" for h in hooks) or "- N/A"
    title_line = f"\n\n## Topic\n{topic}" if topic.strip() else ""
    return (
        f"# Hook & CTA Report{title_line}\n\n"
        f"## Patterns in Your Past Posts\n{bullets(data.get('patterns_identified'))}\n\n"
        f"## Generated Hooks\n{hooks_md}\n\n"
        f"## Title / Headline Ideas\n{bullets(data.get('titles'))}\n\n"
        f"## Call-to-Action Lines\n{bullets(data.get('ctas'))}\n"
    )


# ── Photo Caption ─────────────────────────────────────────────────────────────
def analyze_photo_for_captions(image_bytes, mime_type, niche=""):
    niche_part = f" The creator's niche is '{niche}'." if niche.strip() else ""
    prompt = (
        f"Analyse this photo for a social media post.{niche_part} "
        f"Respond ONLY with valid JSON, no markdown fences. JSON schema:\n"
        f'{{"photo_description": string, "mood_vibe": string, '
        f'"suggested_captions": [string], "suggested_hashtags": [string], '
        f'"trending_song_suggestions": [string], "reel_concept_ideas": [string]}}\n\n'
        f"5 captions in different tones, 8–10 hashtags (no # symbol), "
        f"3–5 trending songs with artist name, 2–3 reel concepts."
    )
    image_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
    from .ai import _ensure_key as _ensure_gemini_key
    _ensure_gemini_key()
    client = get_client()
    if client is None:
        _ensure_gemini_key()
    try:
        response = generate_with_fallback(
            client,
            [image_part, prompt],
            config=types.GenerateContentConfig(tools=[types.Tool(google_search=types.GoogleSearch())]),
        )
        text, grounded = response.text, True
    except Exception as first_err:
        try:
            response = generate_with_fallback(client, [image_part, prompt])
            text, grounded = response.text, False
        except Exception as second_err:
            raise RuntimeError(f"Gemini photo analysis failed: {second_err}") from second_err

    cleaned = text.strip().strip("`")
    if cleaned.lower().startswith("json"):
        cleaned = cleaned[4:]
    try:
        return json.loads(cleaned), text, grounded
    except Exception:
        return None, text, grounded


def photo_analysis_to_markdown(data):
    def bullets(items):
        return "\n".join(f"- {i}" for i in items) if items else "- N/A"

    hashtags = data.get("suggested_hashtags", [])
    hashtag_line = " ".join(f"#{h.lstrip('#')}" for h in hashtags) if hashtags else "N/A"
    return (
        f"# Photo → Caption & Trend Match\n\n"
        f"## Vibe\n{data.get('mood_vibe', '')}\n\n"
        f"## What the Photo Shows\n{data.get('photo_description', '')}\n\n"
        f"## Suggested Captions\n{bullets(data.get('suggested_captions'))}\n\n"
        f"## Suggested Hashtags\n{hashtag_line}\n\n"
        f"## Trending Song Suggestions\n{bullets(data.get('trending_song_suggestions'))}\n\n"
        f"## Reel Concept Ideas\n{bullets(data.get('reel_concept_ideas'))}\n"
    )


# ── Pre-Publish Checker ───────────────────────────────────────────────────────
def pre_publish_check(draft_post, context_text):
    prompt = (
        f"Review this draft post. JSON schema:\n"
        f'{{"virality_score": int, "virality_reasoning": string, '
        f'"engagement_level": "Low"|"Medium"|"High", "engagement_reasoning": string, '
        f'"brand_safety_status": "Safe"|"Needs Review", "brand_safety_notes": string, '
        f'"fact_check_flags": [string], "copyright_flags": [string]}}\n\n'
        f"Creator context:\n{context_text}\n\nDRAFT POST:\n{draft_post}"
    )
    return ask_ai_json(prompt)


def pre_publish_to_markdown(draft_post, data):
    def bullets(items):
        return "\n".join(f"- {i}" for i in items) if items else "- None flagged"

    return (
        f"# Pre-Publish Report\n\n## Draft Post\n> {draft_post}\n\n"
        f"## Virality Score\n{data.get('virality_score', '?')}/100 — {data.get('virality_reasoning', '')}\n\n"
        f"## Predicted Engagement\n{data.get('engagement_level', '')} — {data.get('engagement_reasoning', '')}\n\n"
        f"## Brand Safety\n{data.get('brand_safety_status', '')} — {data.get('brand_safety_notes', '')}\n\n"
        f"## Fact-Check Flags\n{bullets(data.get('fact_check_flags'))}\n\n"
        f"## Copyright Watch\n{bullets(data.get('copyright_flags'))}\n"
    )


# ── Growth ────────────────────────────────────────────────────────────────────
def growth_strategy_report(text, topic):
    extra = f" Niche: '{topic}'. Include how to stand out from similar creators." if topic else ""
    return ask_ai(
        f"Create a 30-day growth strategy + monetisation roadmap.{extra} "
        f"Use markdown headers: ## Growth Plan, ## Monetisation Ideas, ## How to Stand Out.\n\nCreator content:\n{text}"
    )


# ── Brand tools ───────────────────────────────────────────────────────────────
def build_creator_profile_text(profile):
    lines = []
    if profile.get("niche"):
        lines.append(f"Niche/Category: {profile['niche']}")
    if profile.get("platforms"):
        lines.append(f"Platforms: {', '.join(profile['platforms'])}")
    if profile.get("followers"):
        lines.append(f"Follower/Subscriber count: {profile['followers']}")
    if profile.get("age_range"):
        lines.append(f"Audience age range: {profile['age_range']}")
    if profile.get("gender_split"):
        lines.append(f"Audience gender split: {profile['gender_split']}")
    if profile.get("geography"):
        lines.append(f"Audience geography: {profile['geography']}")
    if profile.get("tone"):
        lines.append(f"Content tone/style: {', '.join(profile['tone'])}")
    if profile.get("engagement_rate"):
        lines.append(f"Average engagement rate: {profile['engagement_rate']}")
    if profile.get("past_brands"):
        lines.append(f"Past brand collabs: {profile['past_brands']}")
    if profile.get("no_go"):
        lines.append(f"Topics/products creator will NOT promote: {profile['no_go']}")
    return "\n".join(lines) if lines else "No profile details provided."


def brand_dna_match(profile, campaign_brief):
    profile_text = build_creator_profile_text(profile)
    prompt = (
        f"A creator is evaluating a brand campaign brief. Score the fit. JSON schema:\n"
        f'{{"audience_match_score": int, "audience_match_reasoning": string, '
        f'"content_style_match_score": int, "content_style_match_reasoning": string, '
        f'"brand_safety_score": int, "brand_safety_notes": string, '
        f'"estimated_engagement_level": "Low"|"Medium"|"High", "estimated_engagement_reasoning": string, '
        f'"overall_fit_score": int, "overall_verdict": "Strong Fit"|"Moderate Fit"|"Weak Fit", '
        f'"campaign_concept": string, "pitch_angle": string, '
        f'"red_flags": [string], "negotiation_tips": [string]}}\n\n'
        f"Creator profile:\n{profile_text}\n\nCampaign Brief:\n{campaign_brief}"
    )
    return ask_ai_json(prompt)


def brand_dna_match_to_markdown(campaign_brief, data):
    def bullets(items):
        return "\n".join(f"- {i}" for i in items) if items else "- None"

    verdict_emoji = {"Strong Fit": "🟢", "Moderate Fit": "🟡", "Weak Fit": "🔴"}.get(
        data.get("overall_verdict", ""), "⚪"
    )
    return (
        f"# Brand Fit Report\n\n"
        f"## Campaign Brief\n> {campaign_brief}\n\n"
        f"## Overall Verdict\n{verdict_emoji} **{data.get('overall_verdict', '')}** — "
        f"Overall Fit Score: {data.get('overall_fit_score', '?')}/100\n\n"
        f"## Audience Match\n{data.get('audience_match_score', '?')}/100 — {data.get('audience_match_reasoning', '')}\n\n"
        f"## Content Style Match\n{data.get('content_style_match_score', '?')}/100 — {data.get('content_style_match_reasoning', '')}\n\n"
        f"## Brand Safety Score\n{data.get('brand_safety_score', '?')}/100 — {data.get('brand_safety_notes', '')}\n\n"
        f"## Estimated Engagement\n{data.get('estimated_engagement_level', '')} — {data.get('estimated_engagement_reasoning', '')}\n\n"
        f"## Campaign Concept\n{data.get('campaign_concept', '')}\n\n"
        f"## Pitch Angle\n{data.get('pitch_angle', '')}\n\n"
        f"## Red Flags\n{bullets(data.get('red_flags'))}\n\n"
        f"## Negotiation Tips\n{bullets(data.get('negotiation_tips'))}\n"
    )


def brand_reputation_check(brand_name, deal_details):
    extra = f"\n\nDeal offered:\n{deal_details}" if deal_details.strip() else ""
    prompt = (
        f"A content creator is about to sign a brand deal with '{brand_name}' and wants a reputation check. "
        f"JSON schema:\n"
        f'{{"trust_score": int, "reputation_summary": string, '
        f'"known_controversies": [string], "payment_reliability_notes": string, '
        f'"creator_community_sentiment": string, "positive_signals": [string], '
        f'"red_flags": [string], "verdict": "Proceed"|"Proceed with Caution"|"Avoid", '
        f'"recommendations": [string]}}\n\n'
        f"Brand: {brand_name}{extra}"
    )
    return ask_ai_json(prompt)


def brand_reputation_to_markdown(brand_name, data):
    def bullets(items):
        return "\n".join(f"- {i}" for i in items) if items else "- None found"

    verdict_emoji = {"Proceed": "🟢", "Proceed with Caution": "🟡", "Avoid": "🔴"}.get(
        data.get("verdict", ""), "⚪"
    )
    return (
        f"# Brand Reputation Report — {brand_name}\n\n"
        f"## Verdict\n{verdict_emoji} **{data.get('verdict', '')}** — Trust Score: {data.get('trust_score', '?')}/100\n\n"
        f"## Reputation Summary\n{data.get('reputation_summary', '')}\n\n"
        f"## Creator Community Sentiment\n{data.get('creator_community_sentiment', '')}\n\n"
        f"## Payment Reliability\n{data.get('payment_reliability_notes', '')}\n\n"
        f"## Known Controversies\n{bullets(data.get('known_controversies'))}\n\n"
        f"## Positive Signals\n{bullets(data.get('positive_signals'))}\n\n"
        f"## Red Flags\n{bullets(data.get('red_flags'))}\n\n"
        f"## Recommendations\n{bullets(data.get('recommendations'))}\n\n"
        f"---\n*⚠️ Based on AI's general knowledge — not a legal/financial verification. "
        f"For high-value deals, verify via creator forums and a lawyer.*\n"
    )

# ── Campaign Brief ────────────────────────────────────────────────────────────
def generate_campaign_brief(text, brand, goal):
    prompt = (
        f"Campaign brief for creator × '{brand}', goal: '{goal}'. JSON:\n"
        f'{{"fit_summary": string, "deliverables": [string], '
        f'"timeline": [{{"phase": string, "duration": string, "description": string}}], '
        f'"kpis": [string], "estimated_duration_weeks": int}}\n\nCreator content:\n{text}'
    )
    return ask_ai_json(prompt)


def campaign_brief_to_markdown(brand, goal, data):
    def bullets(items):
        return "\n".join(f"- {i}" for i in items) if items else "- N/A"

    timeline = data.get("timeline", [])
    timeline_md = "\n".join(
        f"- **{t.get('phase','')}** ({t.get('duration','')}): {t.get('description','')}" for t in timeline
    ) or "- N/A"
    return (
        f"# Campaign Brief — {brand}\n\n## Campaign Goal\n{goal}\n\n"
        f"## Fit Summary\n{data.get('fit_summary', '')}\n\n"
        f"## Deliverables\n{bullets(data.get('deliverables'))}\n\n"
        f"## Timeline\n{timeline_md}\n\n"
        f"## KPIs\n{bullets(data.get('kpis'))}\n\n"
        f"## Estimated Duration\n{data.get('estimated_duration_weeks', '?')} weeks\n"
    )


# ── Social Commerce ───────────────────────────────────────────────────────────
def generate_shoppable_content(text, product):
    prompt = (
        f"Creator wants to promote '{product}'. JSON:\n"
        f'{{"hook_captions": [string], "shoppable_reel_concepts": [string], '
        f'"placement_tips": [string], "conversion_score": int, "conversion_reasoning": string}}\n\n'
        f"Creator style:\n{text}"
    )
    return ask_ai_json(prompt)


def shoppable_content_to_markdown(product, data):
    def numbered(items):
        return "\n".join(f"{i+1}. {x}" for i, x in enumerate(items)) if items else "- N/A"

    return (
        f"# Shoppable Content Plan — {product}\n\n"
        f"## Conversion Score\n{data.get('conversion_score', '?')}/100 — {data.get('conversion_reasoning', '')}\n\n"
        f"## Hook Captions\n{numbered(data.get('hook_captions'))}\n\n"
        f"## Shoppable Reel Concepts\n{numbered(data.get('shoppable_reel_concepts'))}\n\n"
        f"## Placement Tips\n{numbered(data.get('placement_tips'))}\n"
    )


# ── Problem Solver ────────────────────────────────────────────────────────────
def solve_problem(text, problem):
    context = f"Creator context:\n{text}\n\n" if text.strip() else ""
    prompt = (
        f"Diagnose this creator problem and give a concrete action plan. JSON:\n"
        f'{{"diagnosis": string, "root_causes": [string], "action_plan": [string], "quick_win": string}}\n\n'
        f"{context}Problem: {problem}"
    )
    return ask_ai_json(prompt)


def problem_solution_to_markdown(problem, data):
    def bullets(items):
        return "\n".join(f"- {i}" for i in items) if items else "- N/A"

    def numbered(items):
        return "\n".join(f"{i+1}. {x}" for i, x in enumerate(items)) if items else "- N/A"

    return (
        f"# Problem Solver Report\n\n## Problem\n{problem}\n\n"
        f"## Quick Win\n{data.get('quick_win', '')}\n\n"
        f"## Diagnosis\n{data.get('diagnosis', '')}\n\n"
        f"## Root Causes\n{bullets(data.get('root_causes'))}\n\n"
        f"## Action Plan\n{numbered(data.get('action_plan'))}\n"
    )


# ── Wellbeing (merged coach + burnout predictor) ──────────────────────────────
def wellbeing_checkin(text):
    return ask_ai(
        f"Act as a supportive creator wellbeing coach. Respond with:\n\n"
        f"## Check-In\nGentle reflection on possible pressure or burnout signs.\n\n"
        f"## Handling Negativity\n2–3 tips for trolls/hate — when to mute/block/report.\n\n"
        f"## Sustainable Routine\n2–3 realistic suggestions for balance and rest.\n\n"
        f"Creator content:\n{text}"
    )


def predict_burnout(profile):
    lines = [
        f"Posts per week: {profile['posts_per_week']}",
        f"Change in posting frequency: {profile['frequency_change']}",
        f"Energy/motivation (1–10): {profile['energy_level']}",
        f"Engagement trend last month: {profile['engagement_trend']}",
        f"Hours on content per day: {profile['hours_per_day']}",
        f"Negative comments frequency: {profile['negativity_level']}",
        f"Days since last full break: {profile['days_since_break']}",
    ]
    if profile.get("notes", "").strip():
        lines.append(f"Creator's notes: {profile['notes']}")
    prompt = (
        f"Predict burnout risk and give supportive guidance. JSON schema:\n"
        f'{{"burnout_risk": "Low"|"Medium"|"High", "risk_score": int, '
        f'"warning_signs": [string], "contributing_factors": [string], '
        f'"recommendations": [string], "suggested_rest_schedule": string, "encouraging_note": string}}\n\n'
        f"risk_score 0–100. Be supportive, never alarmist.\n\n"
        f"Creator self-assessment:\n" + "\n".join(lines)
    )
    return ask_ai_json(prompt)


def burnout_to_markdown(data):
    def bullets(items):
        return "\n".join(f"- {i}" for i in items) if items else "- N/A"

    risk = data.get("burnout_risk", "—")
    risk_emoji = {"Low": "🟢", "Medium": "🟡", "High": "🔴"}.get(risk, "⚪")
    return (
        f"# Burnout Prediction Report\n\n"
        f"## Risk Level\n{risk_emoji} **{risk}** — Risk Score: {data.get('risk_score', '?')}/100\n\n"
        f"## Warning Signs\n{bullets(data.get('warning_signs'))}\n\n"
        f"## Contributing Factors\n{bullets(data.get('contributing_factors'))}\n\n"
        f"## Recommendations\n{bullets(data.get('recommendations'))}\n\n"
        f"## Suggested Rest Schedule\n{data.get('suggested_rest_schedule', '')}\n\n"
        f"## A Note for You\n{data.get('encouraging_note', '')}\n\n"
        f"---\n*Supportive guidance only — not a clinical assessment. "
        f"If persistently overwhelmed, please speak with a mental health professional.*\n"
    )


# ── Trends ────────────────────────────────────────────────────────────────────
def generate_trends_report(niche, platform):
    platform_part = (
        f" on {platform}" if platform else " across major platforms (Instagram, YouTube, TikTok, X)"
    )
    niche_part = f" in the '{niche}' niche" if niche else ""
    prompt = (
        f"Give a creator-focused briefing on what's currently trending{platform_part}{niche_part}. "
        f"Use these exact headers:\n\n"
        f"## Trending Topics & Formats\n3–5 current content trends with a note on why each works.\n\n"
        f"## Trending Sounds & Audio\n3–5 trending audios/sounds.\n\n"
        f"## Creators & Influencers Making Noise\n3–5 buzzing creators{niche_part} with a note on relevance.\n\n"
        f"## Latest Platform & Industry News\n3–5 recent news items (algorithm changes, monetisation, policy).\n\n"
        f"Be concise, specific, and prioritise the most recent information."
    )
    return ask_ai_with_search(prompt)


# ── Fake Audience Detector ────────────────────────────────────────────────────
def analyze_fake_followers(platform, username, follower_sample, engagement_stats):
    prompt = (
        f"Analyse {platform} creator @{username} for fake followers/bot activity. JSON:\n"
        f'{{"fake_follower_risk": "Low"|"Medium"|"High", "estimated_fake_percentage": int, '
        f'"authenticity_score": int, "bot_signals": [string], "suspicious_patterns": [string], '
        f'"healthy_signals": [string], "engagement_verdict": string, "recommendations": [string], "overall_summary": string}}\n\n'
        f"Engagement stats:\n{engagement_stats}\n\nFollower sample:\n{follower_sample}"
    )
    return ask_ai_json(prompt)


def analyze_fake_comments(platform, username, comments_text):
    prompt = (
        f"Analyse comments from {platform} @{username}. JSON:\n"
        f'{{"spam_percentage": int, "bot_comment_percentage": int, "genuine_comment_percentage": int, '
        f'"spam_types": [string], "bot_comment_examples": [string], "genuine_comment_examples": [string], '
        f'"comment_quality_score": int, "pod_activity_detected": bool, "pod_evidence": string, "action_items": [string]}}\n\n'
        f"Comments:\n{comments_text}"
    )
    return ask_ai_json(prompt)


def fake_audience_to_markdown(platform, username, follower_data, comment_data):
    def bullets(items):
        return "\n".join(f"- {i}" for i in items) if items else "- None detected"

    md = f"# Fake Audience Analysis — @{username} ({platform})\n\n"
    if follower_data:
        risk_emoji = {"Low": "🟢", "Medium": "🟡", "High": "🔴"}.get(
            follower_data.get("fake_follower_risk", ""), "⚪"
        )
        md += (
            f"## Audience Authenticity\n"
            f"**Authenticity Score:** {follower_data.get('authenticity_score', '?')}/100\n\n"
            f"**Fake Follower Risk:** {risk_emoji} {follower_data.get('fake_follower_risk', '?')} "
            f"(~{follower_data.get('estimated_fake_percentage', '?')}% estimated fake)\n\n"
            f"**Engagement Verdict:** {follower_data.get('engagement_verdict', '')}\n\n"
            f"### Bot Signals\n{bullets(follower_data.get('bot_signals'))}\n\n"
            f"### Suspicious Patterns\n{bullets(follower_data.get('suspicious_patterns'))}\n\n"
            f"### Healthy Signals\n{bullets(follower_data.get('healthy_signals'))}\n\n"
            f"### Recommendations\n{bullets(follower_data.get('recommendations'))}\n\n"
            f"### Summary\n{follower_data.get('overall_summary', '')}\n\n"
        )
    if comment_data:
        pod_badge = "YES — Pod activity suspected" if comment_data.get("pod_activity_detected") else "No pod activity detected"
        md += (
            f"---\n\n## Comment Quality Analysis\n"
            f"**Comment Quality Score:** {comment_data.get('comment_quality_score', '?')}/100\n\n"
            f"| Category | Percentage |\n|---|---|\n"
            f"| Bot Comments | {comment_data.get('bot_comment_percentage', '?')}% |\n"
            f"| Spam | {comment_data.get('spam_percentage', '?')}% |\n"
            f"| Genuine | {comment_data.get('genuine_comment_percentage', '?')}% |\n\n"
            f"**Engagement Pod Activity:** {pod_badge}\n\n"
            f"### Spam Types Detected\n{bullets(comment_data.get('spam_types'))}\n\n"
            f"### Action Items\n{bullets(comment_data.get('action_items'))}\n"
        )
    return md

