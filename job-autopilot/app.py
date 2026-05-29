"""Streamlit UI for Job Application Autopilot."""

import streamlit as st
from utils.pdf_parser import extract_text_from_pdf
from graph import run_graph

# ── Page configuration ──────────────────────────────────────────────
st.set_page_config(
    page_title="Job Application Autopilot",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ──────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

/* ── Global ── */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* ── Main header area ── */
.main-header {
    text-align: center;
    padding: 2.5rem 1rem 1.5rem;
}
.main-header h1 {
    font-size: 2.8rem;
    font-weight: 800;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.25rem;
}
.main-header p {
    font-size: 1.1rem;
    color: #9ca3af;
    font-weight: 500;
}

/* ── Card style for expanders ── */
.stExpander {
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 14px;
    background: rgba(255,255,255,0.02);
    margin-bottom: 1rem;
    transition: border-color 0.3s ease;
}
.stExpander:hover {
    border-color: rgba(102,126,234,0.4);
}

/* ── Metric styling ── */
[data-testid="stMetricValue"] {
    font-size: 3.2rem !important;
    font-weight: 800 !important;
    background: linear-gradient(135deg, #667eea, #764ba2);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

/* ── Keyword tags ── */
.keyword-tag {
    display: inline-block;
    padding: 0.3rem 0.75rem;
    margin: 0.2rem;
    border-radius: 20px;
    font-size: 0.82rem;
    font-weight: 600;
    background: linear-gradient(135deg, #667eea22, #764ba222);
    color: #a78bfa;
    border: 1px solid rgba(167,139,250,0.25);
    transition: all 0.2s ease;
}
.keyword-tag:hover {
    background: linear-gradient(135deg, #667eea44, #764ba244);
    transform: translateY(-1px);
}

/* ── Missing skill tags ── */
.missing-tag {
    display: inline-block;
    padding: 0.3rem 0.75rem;
    margin: 0.2rem;
    border-radius: 20px;
    font-size: 0.82rem;
    font-weight: 600;
    background: rgba(239,68,68,0.1);
    color: #f87171;
    border: 1px solid rgba(248,113,113,0.25);
}

/* ── Run button ── */
.stButton > button {
    width: 100%;
    padding: 0.85rem 2rem;
    font-size: 1.1rem;
    font-weight: 700;
    border: none;
    border-radius: 12px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    cursor: pointer;
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px rgba(102,126,234,0.3);
}
.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 25px rgba(102,126,234,0.45);
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
}
section[data-testid="stSidebar"] h2 {
    color: #a78bfa;
}

/* ── Progress animation ── */
@keyframes shimmer {
    0% { background-position: -200% 0; }
    100% { background-position: 200% 0; }
}
.shimmer-bar {
    height: 6px;
    border-radius: 3px;
    background: linear-gradient(90deg, #667eea, #764ba2, #667eea);
    background-size: 200% 100%;
    animation: shimmer 2s infinite;
    margin: 1rem 0;
}

/* ── Score ring colours ── */
.score-excellent { color: #34d399 !important; }
.score-good { color: #fbbf24 !important; }
.score-low { color: #f87171 !important; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📖 How to Use")
    st.markdown("""
    1. **Paste a Job URL** — any public job posting link  
       *(Internshala, Naukri, company sites)*
    2. **Or paste the JD text** directly if the URL  
       doesn't work (e.g. LinkedIn)
    3. **Upload your Resume** — PDF format only
    4. **Click Run Agents** — the system runs 4 AI agents  
       sequentially via LangGraph
    5. **Review Outputs** — tailored bullets & cold email
    """)
    st.divider()
    st.markdown("### 🔗 Agent Pipeline")
    st.markdown("""
    ```
    ① JD Scraper
        ↓
    ② Resume Scorer
        ↓
    ③ Bullet Rewriter
        ↓
    ④ Email Generator
    ```
    """)
    st.divider()
    st.markdown(
        "<small style='color:#6b7280;'>Powered by Groq · LLaMA 3.1 · LangGraph</small>",
        unsafe_allow_html=True,
    )

# ── Header ─────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1>🚀 Job Application Autopilot</h1>
    <p>Powered by LangGraph + Groq</p>
</div>
""", unsafe_allow_html=True)

# ── Inputs ─────────────────────────────────────────────────────────
col_input, col_pdf = st.columns(2, gap="large")

with col_input:
    st.markdown("##### 🔗 Job Posting URL")
    job_url = st.text_input(
        "Job URL",
        placeholder="Paste any public job URL (Internshala, Naukri, company careers page)...",
        label_visibility="collapsed",
    )
    st.markdown("##### 📝 Or Paste Job Description Directly")
    jd_paste = st.text_area(
        "Paste JD",
        placeholder="Paste the full job description text here if URL doesn't work or you're using LinkedIn...",
        height=250,
        label_visibility="collapsed",
    )

with col_pdf:
    st.markdown("##### 📄 Resume PDF")
    uploaded_file = st.file_uploader(
        "Upload Resume",
        type=["pdf"],
        label_visibility="collapsed",
    )

st.markdown("")

# ── Run button ─────────────────────────────────────────────────────
run_clicked = st.button("⚡  Run Agents", use_container_width=True)

if run_clicked:
    # ── Validation ─────────────────────────────────────────────────
    if not job_url and not jd_paste.strip():
        st.warning("Please provide a job URL or paste the job description.")
        st.stop()
    if not uploaded_file:
        st.error("Please upload your resume PDF.")
        st.stop()

    # Parse PDF
    resume_text = extract_text_from_pdf(uploaded_file)
    if resume_text.startswith("Error reading PDF"):
        st.error(resume_text)
        st.stop()

    # Show progress
    st.markdown('<div class="shimmer-bar"></div>', unsafe_allow_html=True)

    with st.spinner("🤖 Running 4 agents… this takes about 15-30 seconds"):
        state = run_graph(
            job_url=job_url.strip(),
            resume_text=resume_text,
            jd_raw_text=jd_paste.strip(),
        )

    # ── Determine which input source was used ──────────────────────
    scrape_failed = state.get("scrape_failed", False)

    if job_url.strip() and not scrape_failed:
        st.toast("✅ Using scraped URL content", icon="🌐")
    elif jd_paste.strip():
        if job_url.strip():
            st.toast("⚠️ URL scraping failed — using pasted job description", icon="📝")
        else:
            st.toast("✅ Using pasted job description", icon="📝")
    else:
        # URL was given but scrape failed and no pasted text
        if not state.get("jd_text"):
            st.error(
                "Could not extract job details from URL and no JD text provided. "
                "Please paste the job description manually."
            )
            st.stop()

    # ── Error handling ─────────────────────────────────────────────
    if state.get("error"):
        st.error(f"⚠️ {state['error']}")

    # ── Results ────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("## 📊 Results")

    # 1 — Job Analysis
    with st.expander("🔍  Job Analysis", expanded=True):
        if state.get("jd_text"):
            st.markdown(state["jd_text"])
            st.markdown("")
            if state.get("keywords"):
                st.markdown("**Extracted Keywords:**")
                tags_html = " ".join(
                    f'<span class="keyword-tag">{kw}</span>'
                    for kw in state["keywords"]
                )
                st.markdown(tags_html, unsafe_allow_html=True)
        else:
            st.info("No job analysis available.")

    # 2 — Resume Match Score
    with st.expander("📈  Resume Match Score", expanded=True):
        score = state.get("match_score", 0)
        score_cols = st.columns([1, 2])
        with score_cols[0]:
            st.metric(label="Match Score", value=f"{score}/100")
        with score_cols[1]:
            if score >= 75:
                st.success("🎯 Strong match! Your resume aligns well with this role.")
            elif score >= 50:
                st.warning("⚡ Moderate match. Consider tailoring your resume further.")
            else:
                st.error("🔻 Low match. Significant gaps detected — see missing skills.")

        missing = state.get("missing_skills", [])
        if missing:
            st.markdown("**Missing Skills:**")
            missing_html = " ".join(
                f'<span class="missing-tag">✗ {skill}</span>'
                for skill in missing
            )
            st.markdown(missing_html, unsafe_allow_html=True)

    # 3 — Rewritten Resume Bullets
    with st.expander("✍️  Rewritten Resume Bullets", expanded=True):
        bullets = state.get("rewritten_bullets", "")
        if bullets:
            st.text_area(
                "Rewritten Bullets",
                value=bullets,
                height=300,
                label_visibility="collapsed",
            )
        else:
            st.info("No rewritten bullets available.")

    # 4 — Cold Recruiter Email
    with st.expander("📧  Cold Recruiter Email", expanded=True):
        email = state.get("cold_email", "")
        if email:
            st.code(email, language="text")
        else:
            st.info("No email generated.")
