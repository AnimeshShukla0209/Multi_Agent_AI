import streamlit as st
import os
from datetime import datetime
from fpdf import FPDF
from agents import build_search_agent, build_reader_agent, writer_chain, critic_chain
from vector_store import store_research, retrieve_relevant_context

st.set_page_config(
    page_title="Research Intelligence",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Syne:wght@700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background: #eef0fb;
    color: #1a1a2e;
}

.stApp {
    background: linear-gradient(135deg, #dde1f5 0%, #eef0fb 40%, #f0e8f5 70%, #fce8f0 100%);
    min-height: 100vh;
}

.stApp::before {
    content: '';
    position: fixed;
    inset: 0;
    background-image:
        linear-gradient(rgba(99,102,241,0.035) 1px, transparent 1px),
        linear-gradient(90deg, rgba(99,102,241,0.035) 1px, transparent 1px);
    background-size: 56px 56px;
    pointer-events: none;
    z-index: 0;
}

#MainMenu, footer, header { visibility: hidden; }
.block-container {
    padding: 2rem 2.5rem 4rem !important;
    max-width: 960px !important;
    margin: 0 auto !important;
}

/* ── TOPBAR ── */
.topbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: rgba(255,255,255,0.65);
    backdrop-filter: blur(20px);
    border: 1px solid rgba(255,255,255,0.85);
    border-radius: 16px;
    padding: 0.75rem 1.25rem;
    margin-bottom: 2.5rem;
    box-shadow: 0 2px 20px rgba(99,102,241,0.07);
}
.topbar-left {
    display: flex; align-items: center; gap: 8px;
    font-size: 0.8rem; font-weight: 500; color: #64748b;
}
.topbar-center {
    font-size: 0.88rem; font-weight: 700; color: #1a1a2e;
    letter-spacing: -0.01em;
}
.topbar-right {
    background: #1a1a2e; color: white;
    font-size: 0.72rem; font-weight: 600;
    padding: 0.35rem 0.9rem; border-radius: 100px;
    display: flex; align-items: center; gap: 5px;
}

/* ── HERO ── */
.hero-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 2rem;
    gap: 1rem;
}
.hero-greeting {
    font-family: 'Syne', sans-serif;
    font-size: clamp(1.8rem, 3.5vw, 2.6rem);
    font-weight: 700;
    line-height: 1.2;
    color: #94a3b8;
    letter-spacing: -0.02em;
}
.hero-greeting strong { color: #1a1a2e; }
.hero-bot-wrap {
    position: relative; flex-shrink: 0;
}
.hero-bubble {
    position: absolute;
    top: -12px; right: -8px;
    background: white;
    border-radius: 12px 12px 12px 4px;
    padding: 0.45rem 0.7rem;
    font-size: 0.72rem; font-weight: 500; color: #1a1a2e;
    box-shadow: 0 4px 16px rgba(0,0,0,0.1);
    white-space: nowrap;
    z-index: 2;
}
.hero-avatar {
    width: 80px; height: 80px;
    background: linear-gradient(135deg, #c7d2fe, #e0e7ff);
    border-radius: 20px;
    display: flex; align-items: center; justify-content: center;
    font-size: 2.2rem;
    box-shadow: 0 8px 28px rgba(99,102,241,0.18);
}

/* ── FEATURE CARDS ── */
.cards-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1rem;
    margin-bottom: 2rem;
}
.fcard {
    background: rgba(255,255,255,0.72);
    backdrop-filter: blur(16px);
    border: 1px solid rgba(255,255,255,0.9);
    border-radius: 18px;
    padding: 1.4rem;
    box-shadow: 0 2px 16px rgba(99,102,241,0.05);
    transition: all 0.3s cubic-bezier(0.4,0,0.2,1);
    cursor: default;
}
.fcard:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 36px rgba(99,102,241,0.13);
    background: rgba(255,255,255,0.9);
}
.fcard-icon { font-size: 1.7rem; margin-bottom: 0.85rem; display: block; }
.fcard-title {
    font-size: 0.88rem; font-weight: 600; color: #1a1a2e;
    line-height: 1.45; margin-bottom: 0.6rem;
}
.fcard-tag { font-size: 0.7rem; color: #94a3b8; font-weight: 500; }

/* ── INPUT CARD ── */
.input-card {
    background: rgba(255,255,255,0.72);
    backdrop-filter: blur(16px);
    border: 1px solid rgba(255,255,255,0.9);
    border-radius: 20px;
    padding: 1.25rem 1.5rem 1rem;
    box-shadow: 0 4px 24px rgba(99,102,241,0.07);
    margin-bottom: 0.5rem;
}
.input-meta-row {
    display: flex; justify-content: space-between;
    font-size: 0.7rem; color: #94a3b8; font-weight: 500;
    margin-bottom: 0.75rem;
}
.action-pills {
    display: flex; gap: 0.5rem; flex-wrap: wrap;
    margin-top: 0.85rem;
}
.apill {
    background: #1a1a2e; color: white;
    font-size: 0.7rem; font-weight: 600;
    padding: 0.38rem 0.9rem;
    border-radius: 100px;
    display: inline-flex; align-items: center; gap: 5px;
    cursor: pointer;
    transition: background 0.2s;
}
.apill:hover { background: #6366f1; }

/* ── INPUT OVERRIDES ── */
.stTextInput > div > div > input {
    background: transparent !important;
    border: none !important;
    border-bottom: 1.5px solid rgba(99,102,241,0.18) !important;
    border-radius: 0 !important;
    color: #f8fafc !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.95rem !important;
    padding: 0.4rem 0.75rem !important;
    box-shadow: none !important;
    transition: border-color 0.25s !important;
}
.stTextInput > div > div > input:focus {
    border-bottom-color: #6366f1 !important;
    box-shadow: none !important;
}
.stTextInput > div > div > input::placeholder { color: #cbd5e1 !important; }
.stTextInput > div { border: none !important; box-shadow: none !important; background: transparent !important; }
.stTextInput > label { display: none !important; }

/* ── RUN BUTTON ── */
.stButton > button {
    background: #1a1a2e !important;
    color: white !important;
    border: none !important;
    border-radius: 100px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.82rem !important;
    font-weight: 600 !important;
    padding: 0.65rem 1.6rem !important;
    transition: all 0.3s cubic-bezier(0.4,0,0.2,1) !important;
    box-shadow: 0 4px 16px rgba(26,26,46,0.22) !important;
    width: 100% !important;
    margin-top: 0.1rem !important;
}
.stButton > button:hover {
    background: #6366f1 !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 24px rgba(99,102,241,0.38) !important;
}
.stButton > button:active { transform: scale(0.97) !important; }

/* ── DOWNLOAD BUTTON ── */
.stDownloadButton > button {
    background: rgba(99,102,241,0.08) !important;
    color: #6366f1 !important;
    border: 1px solid rgba(99,102,241,0.2) !important;
    border-radius: 100px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.72rem !important;
    font-weight: 600 !important;
    padding: 0.5rem 1rem !important;
    transition: all 0.25s ease !important;
    width: 100% !important;
}
.stDownloadButton > button:hover {
    background: #6366f1 !important;
    color: white !important;
    transform: translateY(-1px) !important;
}

/* ── PIPELINE CARD ── */
.pipeline-card {
    background: rgba(255,255,255,0.65);
    backdrop-filter: blur(16px);
    border: 1px solid rgba(255,255,255,0.9);
    border-radius: 20px;
    padding: 1.25rem 1.5rem;
    margin: 1.5rem 0;
    box-shadow: 0 2px 16px rgba(99,102,241,0.06);
}
.pipeline-title {
    font-size: 0.68rem; font-weight: 700;
    text-transform: uppercase; letter-spacing: 0.14em;
    color: #94a3b8; margin-bottom: 1rem;
}

/* ── STEP ROWS ── */
.step-row {
    display: flex; align-items: center; gap: 0.75rem;
    padding: 0.55rem 0.7rem; border-radius: 10px;
    margin-bottom: 0.3rem;
    transition: all 0.35s cubic-bezier(0.4,0,0.2,1);
}
.step-row.running { background: rgba(99,102,241,0.07); }
.step-row.done    { background: rgba(16,185,129,0.05); }

.sdot {
    width: 7px; height: 7px; border-radius: 50%; flex-shrink: 0;
    background: #e2e8f0; transition: all 0.3s;
}
.step-row.running .sdot {
    background: #6366f1;
    animation: dp 1s ease-in-out infinite;
    box-shadow: 0 0 7px rgba(99,102,241,0.5);
}
.step-row.done .sdot { background: #10b981; }
@keyframes dp { 0%,100%{transform:scale(1)} 50%{transform:scale(1.7)} }

.slabel {
    font-size: 0.8rem; font-weight: 500; color: #94a3b8; flex: 1;
    transition: color 0.3s;
}
.step-row.running .slabel { color: #4f46e5; font-weight: 600; }
.step-row.done .slabel    { color: #475569; }

.schip {
    font-size: 0.62rem; font-weight: 600;
    padding: 0.15rem 0.5rem; border-radius: 100px;
}
.schip-wait    { background: #f1f5f9; color: #cbd5e1; }
.schip-running { background: rgba(99,102,241,0.1); color: #6366f1; }
.schip-done    { background: rgba(16,185,129,0.1);  color: #10b981; }

/* ── RESULT CARDS ── */
.rcard {
    background: rgba(255,255,255,0.75);
    backdrop-filter: blur(16px);
    border: 1px solid rgba(255,255,255,0.9);
    border-radius: 20px;
    padding: 1.6rem;
    box-shadow: 0 4px 24px rgba(99,102,241,0.06);
    animation: su 0.5s cubic-bezier(0.4,0,0.2,1) both;
}
@keyframes su { from{opacity:0;transform:translateY(18px)} to{opacity:1;transform:translateY(0)} }

.rcard-hdr {
    display: flex; align-items: center; gap: 6px;
    margin-bottom: 1.1rem; padding-bottom: 0.7rem;
    border-bottom: 1px solid rgba(99,102,241,0.07);
}
.rcard-title {
    font-size: 0.68rem; font-weight: 700;
    text-transform: uppercase; letter-spacing: 0.12em;
    color: #94a3b8; flex: 1;
}
.brag  { background:rgba(16,185,129,0.1); color:#10b981; font-size:0.6rem; font-weight:600; padding:0.15rem 0.5rem; border-radius:100px; }
.bai   { background:rgba(99,102,241,0.1); color:#6366f1; font-size:0.6rem; font-weight:600; padding:0.15rem 0.5rem; border-radius:100px; }

.rtext {
    font-size: 0.875rem; line-height: 1.8;
    color: #475569; white-space: pre-wrap;
}

/* ── SCORE ── */
.score-card {
    background: linear-gradient(135deg, rgba(99,102,241,0.07), rgba(236,72,153,0.05));
    border: 1px solid rgba(99,102,241,0.14);
    border-radius: 20px; padding: 2rem 1.25rem;
    text-align: center; height: 100%;
    animation: su 0.5s cubic-bezier(0.4,0,0.2,1) both;
}
.snum {
    font-family: 'Syne', sans-serif; font-size: 3rem; font-weight: 800;
    background: linear-gradient(135deg, #6366f1, #ec4899);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text; line-height: 1;
}
.slbl {
    font-size: 0.62rem; font-weight: 600; text-transform: uppercase;
    letter-spacing: 0.12em; color: #94a3b8; margin-top: 0.4rem;
}

/* ── DIVIDER ── */
.sdiv {
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(99,102,241,0.15), transparent);
    margin: 1.75rem 0;
}

/* ── EXPANDERS ── */
.streamlit-expanderHeader {
    background: rgba(255,255,255,0.6) !important;
    border: 1px solid rgba(255,255,255,0.85) !important;
    border-radius: 12px !important;
    font-size: 0.75rem !important; font-weight: 600 !important;
    color: #94a3b8 !important;
}
</style>
""", unsafe_allow_html=True)


# ── Helpers ────────────────────────────────────────────────────────────────────
def clean_text(text):
    return (text
        .replace("\u2014","-").replace("\u2013","-")
        .replace("\u2019","'").replace("\u2018","'")
        .replace("\u201c",'"').replace("\u201d",'"')
        .replace("\u2022","*").replace("\u2026","...")
        .replace("\u00a0"," ")
        .encode("latin-1","replace").decode("latin-1")
    )

def generate_pdf(topic, report, feedback, score):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_fill_color(26,26,46); pdf.rect(0,0,210,32,'F')
    pdf.set_font("Helvetica","B",20); pdf.set_text_color(255,255,255)
    pdf.set_xy(15,9); pdf.cell(0,12,"Research Intelligence Report",ln=True)
    pdf.set_font("Helvetica","",8); pdf.set_text_color(148,163,184); pdf.set_x(15)
    pdf.cell(0,6,f"Generated: {datetime.now().strftime('%B %d, %Y  %H:%M')}   |   RAG Enhanced   |   Multi-Agent System",ln=True)
    pdf.ln(8)
    pdf.set_fill_color(240,240,255); pdf.set_draw_color(99,102,241); pdf.set_line_width(0.4)
    pdf.rect(10,pdf.get_y(),190,14,'FD')
    pdf.set_font("Helvetica","B",11); pdf.set_text_color(99,102,241); pdf.set_x(15)
    pdf.cell(0,14,clean_text(f"Topic: {topic}"),ln=True); pdf.ln(6)
    pdf.set_font("Helvetica","B",7); pdf.set_text_color(148,163,184); pdf.set_x(15)
    pdf.cell(0,6,"FINAL REPORT",ln=True)
    pdf.set_draw_color(226,232,240); pdf.set_line_width(0.3); pdf.line(10,pdf.get_y(),200,pdf.get_y()); pdf.ln(4)
    pdf.set_font("Helvetica","",10); pdf.set_text_color(71,85,105); pdf.set_x(15)
    pdf.multi_cell(180,6,clean_text(report)); pdf.ln(8)
    pdf.set_font("Helvetica","B",7); pdf.set_text_color(148,163,184); pdf.set_x(15)
    pdf.cell(0,6,"CRITIC EVALUATION",ln=True)
    pdf.set_draw_color(226,232,240); pdf.line(10,pdf.get_y(),200,pdf.get_y()); pdf.ln(4)
    cs=clean_text(score)
    pdf.set_fill_color(240,240,255); pdf.set_draw_color(99,102,241)
    pdf.rect(10,pdf.get_y(),40,18,'FD')
    pdf.set_font("Helvetica","B",16); pdf.set_text_color(99,102,241)
    pdf.set_xy(10,pdf.get_y()+3); pdf.cell(40,10,cs,align="C",ln=False)
    pdf.set_font("Helvetica","",7); pdf.set_text_color(148,163,184)
    pdf.set_xy(55,pdf.get_y()-3); pdf.cell(0,6,"Critic Score",ln=True); pdf.ln(10)
    pdf.set_font("Helvetica","",10); pdf.set_text_color(71,85,105); pdf.set_x(15)
    pdf.multi_cell(180,6,clean_text(feedback))
    pdf.set_y(-15); pdf.set_font("Helvetica","",7); pdf.set_text_color(148,163,184)
    pdf.cell(0,10,"Generated by Research Intelligence - Multi-Agent System",align="C")
    return bytes(pdf.output())

def render_step(slot, label, status):
    cc = {"wait":"","running":"running","done":"done"}[status]
    sc = {"wait":"schip-wait","running":"schip-running","done":"schip-done"}[status]
    st_txt = {"wait":"idle","running":"processing...","done":"complete"}[status]
    slot.markdown(f"""
    <div class="step-row {cc}">
        <div class="sdot"></div>
        <span class="slabel">{label}</span>
        <span class="schip {sc}">{st_txt}</span>
    </div>""", unsafe_allow_html=True)


# ── TOPBAR ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="topbar">
    <div class="topbar-left">⚙️ &nbsp;Agent v1.0 &nbsp;∨</div>
    <div class="topbar-center">Research Intelligence</div>
    <div class="topbar-right">✦ Pro Plan</div>
</div>
""", unsafe_allow_html=True)

# ── HERO ───────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-row">
    <div class="hero-greeting">Hi Researcher,<br><strong>Ready to Discover<br>Great Things?</strong></div>
    <div class="hero-bot-wrap">
        <div class="hero-bubble">Hey there! 👋<br>Need research?</div>
        <div class="hero-avatar">🤖</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── FEATURE CARDS ──────────────────────────────────────────────────────────────
st.markdown("""
<div class="cards-grid">
    <div class="fcard">
        <span class="fcard-icon">🔍</span>
        <div class="fcard-title">Search the web for recent, reliable sources on any topic automatically</div>
        <div class="fcard-tag">Web Search</div>
    </div>
    <div class="fcard">
        <span class="fcard-icon">🧠</span>
        <div class="fcard-title">Store research in a vector DB and retrieve the most relevant chunks via RAG</div>
        <div class="fcard-tag">RAG Memory</div>
    </div>
    <div class="fcard">
        <span class="fcard-icon">📋</span>
        <div class="fcard-title">Generate a structured report, then critique and score it automatically</div>
        <div class="fcard-tag">Write + Critique</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── INPUT CARD ─────────────────────────────────────────────────────────────────
st.markdown("""
<div class="input-card">
    <div class="input-meta-row">
        <span>✦ Unlock more with Pro Plan</span>
        <span>⚙️ Powered by Agent v1.0</span>
    </div>
""", unsafe_allow_html=True)

col_in, col_btn = st.columns([5, 1], gap="small")
with col_in:
    topic = st.text_input(
        "Topic",
        placeholder='Example: "Latest breakthroughs in quantum computing"',
        label_visibility="collapsed"
    )
with col_btn:
    run = st.button("→ Run")

st.markdown("""
    <div class="action-pills">
        <span class="apill">🔍 Deep Research</span>
        <span class="apill">📊 Get Report</span>
        <span class="apill">🌐 Search Web</span>
        <span class="apill">✦ Summarise</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ── PIPELINE ───────────────────────────────────────────────────────────────────
if run and topic.strip():

    st.markdown('<div class="pipeline-card"><div class="pipeline-title">Agent Pipeline</div>', unsafe_allow_html=True)

    step_defs = [
        "01 · Search Agent — finding sources",
        "02 · Reader Agent — scraping content",
        "03 · Vector DB — storing & retrieving via RAG",
        "04 · Writer — drafting report",
        "05 · Critic — reviewing report",
    ]
    slots = [st.empty() for _ in step_defs]
    for slot, label in zip(slots, step_defs):
        render_step(slot, label, "wait")

    st.markdown('</div>', unsafe_allow_html=True)

    state = {}

    render_step(slots[0], step_defs[0], "running")
    sa = build_search_agent()
    sr = sa.invoke({"messages":[("user", f"Find recent, reliable and detailed information about: {topic}")]})
    state["search_results"] = sr['messages'][-1].content
    render_step(slots[0], step_defs[0], "done")

    render_step(slots[1], step_defs[1], "running")
    ra = build_reader_agent()
    rr = ra.invoke({"messages":[("user",
        f"Based on these search results about '{topic}', pick the most relevant URL and scrape it.\n\nSearch Results:\n{state['search_results'][:800]}")]})
    state["scraped_content"] = rr['messages'][-1].content
    render_step(slots[1], step_defs[1], "done")

    render_step(slots[2], step_defs[2], "running")
    store_research(topic=topic, content=state["scraped_content"], source="scraped_web")
    store_research(topic=topic, content=state["search_results"], source="search_results")
    state["rag_context"] = retrieve_relevant_context(topic=topic, query=f"key facts and insights about {topic}")
    render_step(slots[2], step_defs[2], "done")

    render_step(slots[3], step_defs[3], "running")
    combined = f"SEARCH RESULTS:\n{state['search_results']}\n\nSCRAPED CONTENT:\n{state['scraped_content']}\n\nRAG CHUNKS:\n{state['rag_context']}"
    state["report"] = writer_chain.invoke({"topic": topic, "research": combined})
    render_step(slots[3], step_defs[3], "done")

    render_step(slots[4], step_defs[4], "running")
    state["feedback"] = critic_chain.invoke({"report": state["report"]})
    render_step(slots[4], step_defs[4], "done")

    # ── RESULTS ────────────────────────────────────────────────────────────────
    st.markdown('<div class="sdiv"></div>', unsafe_allow_html=True)

    feedback_text = state["feedback"]
    score_display = "-"
    for line in feedback_text.splitlines():
        if line.strip().lower().startswith("score"):
            score_display = line.strip().replace("Score:","").replace("Score","").strip()
            break

    rep_col, dl_col = st.columns([8, 1], gap="small")
    with rep_col:
        st.markdown(f"""
        <div class="rcard">
            <div class="rcard-hdr">
                <span class="rcard-title">Final Report</span>
                <span class="brag">RAG Enhanced</span>
                <span class="bai">AI Generated</span>
            </div>
            <div class="rtext">{state["report"]}</div>
        </div>""", unsafe_allow_html=True)
    with dl_col:
        st.write("")
        pdf_bytes = generate_pdf(topic=topic, report=state["report"], feedback=feedback_text, score=score_display)
        st.download_button("⬇ PDF", data=pdf_bytes,
            file_name=f"report_{topic[:30].replace(' ','_')}.pdf", mime="application/pdf")

    sc_col, fb_col = st.columns([1, 3], gap="medium")
    with sc_col:
        st.markdown(f"""
        <div class="score-card">
            <div class="snum">{score_display}</div>
            <div class="slbl">Critic Score</div>
        </div>""", unsafe_allow_html=True)
    with fb_col:
        st.markdown(f"""
        <div class="rcard">
            <div class="rcard-hdr"><span class="rcard-title">Critic Feedback</span></div>
            <div class="rtext">{feedback_text}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown('<div class="sdiv"></div>', unsafe_allow_html=True)
    with st.expander("RAG — Retrieved Chunks"):
        st.text(state["rag_context"])
    with st.expander("RAW — Search Results"):
        st.text(state["search_results"])
    with st.expander("RAW — Scraped Content"):
        st.text(state["scraped_content"])

elif run and not topic.strip():
    st.warning("Please enter a topic first.")
