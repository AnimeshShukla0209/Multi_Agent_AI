import streamlit as st
import os
from agents import build_search_agent, build_reader_agent, writer_chain, critic_chain
from vector_store import store_research, retrieve_relevant_context

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

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: #0d0d0d;
    color: #e8e4dc;
}
.stApp { background: #0d0d0d; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2.5rem 3rem 4rem; max-width: 1100px; }

/* ── Hero ── */
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
.hero-title em { font-style: italic; color: #c8a96e; }
.hero-sub {
    font-size: 0.95rem;
    color: #6b6560;
    margin-top: 0.75rem;
    font-weight: 300;
}

/* ── Input ── */
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
.step-title { font-size: 0.9rem; font-weight: 500; color: #e8e4dc; }
.step-status-done { color: #6dbf8a; font-size: 0.8rem; margin-left: auto; }
.step-status-running {
    color: #c8a96e;
    font-size: 0.8rem;
    margin-left: auto;
    animation: pulse 1.2s ease-in-out infinite;
}
.step-status-wait { color: #2a2a2a; font-size: 0.8rem; margin-left: auto; }
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.4} }

/* ── Result blocks ── */
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

/* ── RAG badge ── */
.rag-badge {
    display: inline-block;
    font-family: 'DM Mono', monospace;
    font-size: 0.6rem;
    letter-spacing: 0.12em;
    color: #6dbf8a;
    background: rgba(109,191,138,0.1);
    border: 1px solid rgba(109,191,138,0.2);
    padding: 0.2rem 0.5rem;
    border-radius: 2px;
    text-transform: uppercase;
    margin-left: 0.5rem;
    vertical-align: middle;
}

/* ── Score ── */
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

/* ── Section heading ── */
.section-heading {
    font-family: 'DM Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.2em;
    color: #3d3935;
    text-transform: uppercase;
    margin: 2.5rem 0 1rem;
}

hr { border-color: #1e1e1e !important; margin: 2rem 0 !important; }
</style>
""", unsafe_allow_html=True)


# ── Hero ───────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-label">Multi-Agent System</div>
    <h1 class="hero-title">Research <em>Intelligence</em></h1>
    <p class="hero-sub">Search → Scrape → Store → Retrieve → Write → Critique — fully automated with RAG.</p>
</div>
""", unsafe_allow_html=True)


# ── Input row ──────────────────────────────────────────────────────────────────
col1, col2 = st.columns([5, 1], gap="small")
with col1:
    topic = st.text_input(
        "Research Topic",
        placeholder="e.g. 'Latest breakthroughs in quantum computing'",
        label_visibility="collapsed"
    )
with col2:
    st.write("")
    run = st.button("RUN →")


# ── Helpers ────────────────────────────────────────────────────────────────────
def render_step(slot, label, title, status):
    """status: 'wait' | 'running' | 'done'"""
    status_html = {
        "wait":    '<span class="step-status-wait">Waiting</span>',
        "running": '<span class="step-status-running">● Running</span>',
        "done":    '<span class="step-status-done">✓ Done</span>',
    }[status]
    slot.markdown(f"""
    <div class="step-card">
        <div class="step-header">
            <span class="step-number">{label}</span>
            <span class="step-title">{title}</span>
            {status_html}
        </div>
    </div>""", unsafe_allow_html=True)


# ── Pipeline ───────────────────────────────────────────────────────────────────
if run and topic.strip():

    steps = [
        ("STEP 01", "Search Agent — finding sources"),
        ("STEP 02", "Reader Agent — scraping content"),
        ("STEP 03", "Vector DB — storing & retrieving via RAG"),
        ("STEP 04", "Writer — drafting report"),
        ("STEP 05", "Critic — reviewing report"),
    ]

    # Render all steps as waiting
    slots = []
    for label, title in steps:
        slot = st.empty()
        render_step(slot, label, title, "wait")
        slots.append((slot, label, title))

    state = {}

    # ── Step 1: Search ──
    render_step(*slots[0], "running")
    search_agent = build_search_agent()
    search_result = search_agent.invoke({
        "messages": [("user", f"Find recent, reliable and detailed information about: {topic}")]
    })
    state["search_results"] = search_result['messages'][-1].content
    render_step(*slots[0], "done")

    # ── Step 2: Scrape ──
    render_step(*slots[1], "running")
    reader_agent = build_reader_agent()
    reader_result = reader_agent.invoke({
        "messages": [("user",
            f"Based on the following search results about '{topic}', "
            f"pick the most relevant URL and scrape it for deeper content.\n\n"
            f"Search Results:\n{state['search_results'][:800]}"
        )]
    })
    state["scraped_content"] = reader_result['messages'][-1].content
    render_step(*slots[1], "done")

    # ── Step 3: Store + RAG retrieve ──
    render_step(*slots[2], "running")
    store_research(topic=topic, content=state["scraped_content"], source="scraped_web")
    store_research(topic=topic, content=state["search_results"], source="search_results")
    state["rag_context"] = retrieve_relevant_context(
        topic=topic,
        query=f"key facts, findings and insights about {topic}"
    )
    render_step(*slots[2], "done")

    # ── Step 4: Write ──
    render_step(*slots[3], "running")
    research_combined = (
        f"SEARCH RESULTS:\n{state['search_results']}\n\n"
        f"SCRAPED CONTENT:\n{state['scraped_content']}\n\n"
        f"MOST RELEVANT CHUNKS (via RAG):\n{state['rag_context']}"
    )
    state["report"] = writer_chain.invoke({"topic": topic, "research": research_combined})
    render_step(*slots[3], "done")

    # ── Step 5: Critic ──
    render_step(*slots[4], "running")
    state["feedback"] = critic_chain.invoke({"report": state["report"]})
    render_step(*slots[4], "done")

    # ── Results ────────────────────────────────────────────────────────────────
    st.markdown("<hr>", unsafe_allow_html=True)

    # Final report
    st.markdown('<div class="section-heading">Output</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="result-block">
        <div class="result-label">Final Report <span class="rag-badge">RAG Enhanced</span></div>
        <div class="result-text">{state["report"]}</div>
    </div>
    """, unsafe_allow_html=True)

    # Critic score + feedback
    feedback_text = state["feedback"]
    score_line = ""
    for line in feedback_text.splitlines():
        if line.strip().lower().startswith("score"):
            score_line = line.strip()
            break
    score_display = score_line.replace("Score:", "").replace("Score", "").strip() or "—"

    st.markdown('<div class="section-heading">Evaluation</div>', unsafe_allow_html=True)
    c1, c2 = st.columns([1, 4], gap="medium")
    with c1:
        st.markdown(f"""
        <div style="text-align:center;padding:1.5rem;background:#111;border:1px solid #1e1e1e;border-radius:4px;height:100%;">
            <div class="score-badge">{score_display}</div>
            <div class="score-label">Critic Score</div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="result-block" style="margin-top:0;">
            <div class="result-label">Critic Feedback</div>
            <div class="result-text">{feedback_text}</div>
        </div>
        """, unsafe_allow_html=True)

    # RAG context used
    st.markdown('<div class="section-heading">Research Data</div>', unsafe_allow_html=True)
    with st.expander("RAG — Retrieved Chunks"):
        st.text(state["rag_context"])
    with st.expander("RAW — Search Results"):
        st.text(state["search_results"])
    with st.expander("RAW — Scraped Content"):
        st.text(state["scraped_content"])

elif run and not topic.strip():
    st.warning("Please enter a topic first.")
