import streamlit as st
import sys
import os

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Research Agent",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Mono:wght@400;500&family=DM+Sans:wght@300;400;500&display=swap');

/* ── Base ── */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: #0d0d0d;
    color: #e8e4dc;
}

.stApp {
    background: #0d0d0d;
}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2.5rem 3rem 4rem; max-width: 1100px; }

/* ── Hero header ── */
.hero {
    border-bottom: 1px solid #2a2a2a;
    padding-bottom: 2rem;
    margin-bottom: 2.5rem;
}
.hero-label {
    font-family: 'DM Mono', monospace;
    font-size: 0.7rem;
    letter-spacing: 0.18em;
    color: #c8a96e;
    text-transform: uppercase;
    margin-bottom: 0.5rem;
}
.hero-title {
    font-family: 'DM Serif Display', serif;
    font-size: 3rem;
    line-height: 1.1;
    color: #f0ebe0;
    margin: 0;
}
.hero-title em {
    font-style: italic;
    color: #c8a96e;
}
.hero-sub {
    font-size: 0.95rem;
    color: #6b6560;
    margin-top: 0.75rem;
    font-weight: 300;
}

/* ── Input area ── */
.stTextInput > div > div > input {
    background: #161616 !important;
    border: 1px solid #2a2a2a !important;
    border-radius: 4px !important;
    color: #e8e4dc !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 1rem !important;
    padding: 0.75rem 1rem !important;
    transition: border-color 0.2s;
}
.stTextInput > div > div > input:focus {
    border-color: #c8a96e !important;
    box-shadow: 0 0 0 2px rgba(200,169,110,0.15) !important;
}
.stTextInput > div > div > input::placeholder { color: #3d3935 !important; }

/* ── Button ── */
.stButton > button {
    background: #c8a96e !important;
    color: #0d0d0d !important;
    border: none !important;
    border-radius: 4px !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.8rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    padding: 0.65rem 1.8rem !important;
    transition: all 0.2s !important;
    cursor: pointer !important;
}
.stButton > button:hover {
    background: #e0c080 !important;
    transform: translateY(-1px);
}

/* ── Step cards ── */
.step-card {
    background: #111111;
    border: 1px solid #1e1e1e;
    border-left: 3px solid #c8a96e;
    border-radius: 4px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 1rem;
}
.step-header {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-bottom: 0.5rem;
}
.step-number {
    font-family: 'DM Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.15em;
    color: #c8a96e;
    text-transform: uppercase;
    background: rgba(200,169,110,0.1);
    padding: 0.2rem 0.5rem;
    border-radius: 2px;
}
.step-title {
    font-size: 0.9rem;
    font-weight: 500;
    color: #e8e4dc;
}
.step-status-done { color: #6dbf8a; font-size: 0.8rem; }
.step-status-running {
    color: #c8a96e;
    font-size: 0.8rem;
    animation: pulse 1.2s ease-in-out infinite;
}
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.4} }

/* ── Result sections ── */
.result-block {
    background: #0a0a0a;
    border: 1px solid #1e1e1e;
    border-radius: 4px;
    padding: 1.5rem;
    margin-top: 2rem;
}
.result-label {
    font-family: 'DM Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.18em;
    color: #c8a96e;
    text-transform: uppercase;
    margin-bottom: 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid #1e1e1e;
}
.result-text {
    font-size: 0.9rem;
    line-height: 1.75;
    color: #b8b4ac;
    white-space: pre-wrap;
    font-family: 'DM Sans', sans-serif;
}

/* ── Score badge ── */
.score-badge {
    display: inline-block;
    font-family: 'DM Serif Display', serif;
    font-size: 2.5rem;
    color: #c8a96e;
    line-height: 1;
}
.score-label {
    font-family: 'DM Mono', monospace;
    font-size: 0.65rem;
    color: #3d3935;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-top: 0.2rem;
}

/* ── Divider ── */
hr { border-color: #1e1e1e !important; margin: 2rem 0 !important; }

/* ── Expander ── */
.streamlit-expanderHeader {
    background: #111111 !important;
    border: 1px solid #1e1e1e !important;
    border-radius: 4px !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.75rem !important;
    letter-spacing: 0.1em !important;
    color: #6b6560 !important;
}
</style>
""", unsafe_allow_html=True)


# ── Hero ───────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-label">Multi-Agent System</div>
    <h1 class="hero-title">Research <em>Intelligence</em></h1>
    <p class="hero-sub">Search → Read → Write → Critique — fully automated.</p>
</div>
""", unsafe_allow_html=True)


# ── Input ──────────────────────────────────────────────────────────────────────
col1, col2 = st.columns([5, 1], gap="small")
with col1:
    topic = st.text_input("", placeholder="Enter a research topic e.g. 'Latest breakthroughs in quantum computing'", label_visibility="collapsed")
with col2:
    st.write("")
    run = st.button("RUN →")


# ── Pipeline ───────────────────────────────────────────────────────────────────
if run and topic.strip():

    from pipeline import run_research_pipeline

    # Step tracker
    steps = [
        ("STEP 01", "Search Agent — finding sources"),
        ("STEP 02", "Reader Agent — scraping content"),
        ("STEP 03", "Writer — drafting report"),
        ("STEP 04", "Critic — reviewing report"),
    ]

    step_slots = []
    for label, title in steps:
        slot = st.empty()
        slot.markdown(f"""
        <div class="step-card">
            <div class="step-header">
                <span class="step-number">{label}</span>
                <span class="step-title">{title}</span>
            </div>
            <span style="color:#2a2a2a;font-size:0.8rem;">Waiting...</span>
        </div>""", unsafe_allow_html=True)
        step_slots.append((slot, label, title))

    def mark_running(i):
        slot, label, title = step_slots[i]
        slot.markdown(f"""
        <div class="step-card">
            <div class="step-header">
                <span class="step-number">{label}</span>
                <span class="step-title">{title}</span>
                <span class="step-status-running">● Running</span>
            </div>
        </div>""", unsafe_allow_html=True)

    def mark_done(i):
        slot, label, title = step_slots[i]
        slot.markdown(f"""
        <div class="step-card">
            <div class="step-header">
                <span class="step-number">{label}</span>
                <span class="step-title">{title}</span>
                <span class="step-status-done">✓ Done</span>
            </div>
        </div>""", unsafe_allow_html=True)

    # ── Run pipeline step by step ──
    from agents import build_search_agent, build_reader_agent, writer_chain, critic_chain

    state = {}

    mark_running(0)
    search_agent = build_search_agent()
    search_result = search_agent.invoke({
        "messages": [("user", f"Find recent, reliable and detailed information about: {topic}")]
    })
    state["search_results"] = search_result['messages'][-1].content
    mark_done(0)

    mark_running(1)
    reader_agent = build_reader_agent()
    reader_result = reader_agent.invoke({
        "messages": [("user",
            f"Based on the following search results about '{topic}', "
            f"pick the most relevant URL and scrape it for deeper content.\n\n"
            f"Search Results:\n{state['search_results'][:800]}"
        )]
    })
    state['scraped_content'] = reader_result['messages'][-1].content
    mark_done(1)

    mark_running(2)
    research_combined = (
        f"SEARCH RESULTS:\n{state['search_results']}\n\n"
        f"DETAILED SCRAPED CONTENT:\n{state['scraped_content']}"
    )
    state["report"] = writer_chain.invoke({"topic": topic, "research": research_combined})
    mark_done(2)

    mark_running(3)
    state["feedback"] = critic_chain.invoke({"report": state["report"]})
    mark_done(3)

    # ── Results ────────────────────────────────────────────────────────────────
    st.markdown("<hr>", unsafe_allow_html=True)

    # Report
    st.markdown(f"""
    <div class="result-block">
        <div class="result-label">Final Report</div>
        <div class="result-text">{state["report"]}</div>
    </div>
    """, unsafe_allow_html=True)

    # Critic feedback — parse score
    feedback_text = state["feedback"]
    score_line = ""
    for line in feedback_text.splitlines():
        if line.strip().lower().startswith("score"):
            score_line = line.strip()
            break

    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2 = st.columns([1, 4], gap="medium")
    with c1:
        st.markdown(f"""
        <div style="text-align:center;padding:1.5rem;background:#111;border:1px solid #1e1e1e;border-radius:4px;">
            <div class="score-badge">{score_line.replace("Score:","").replace("Score","").strip() or "—"}</div>
            <div class="score-label">Critic Score</div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="result-block" style="margin-top:0">
            <div class="result-label">Critic Feedback</div>
            <div class="result-text">{feedback_text}</div>
        </div>
        """, unsafe_allow_html=True)

    # Raw data expanders
    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("RAW — Search Results"):
        st.text(state["search_results"])
    with st.expander("RAW — Scraped Content"):
        st.text(state["scraped_content"])

elif run and not topic.strip():
    st.warning("Please enter a topic first.")
