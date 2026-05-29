# 🚀 Job Application Autopilot — Walkthrough

A multi-agent pipeline that takes a **job posting URL** and your **resume PDF**, then runs 4 sequential AI agents to produce **tailored resume bullets** and a **cold recruiter email**.

---

## 1. Prerequisites

| Requirement | Version |
|---|---|
| Python | 3.10 or higher |
| pip | Latest recommended |
| Git | For cloning the repo |

---

## 2. Installation

```bash
# Clone the repository
git clone <your-repo-url> job-autopilot
cd job-autopilot

# Create and activate a virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

## 3. Environment Setup

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key_here
```

### Where to get a free Groq API key

1. Go to **[https://console.groq.com](https://console.groq.com)**
2. Sign up for a free account
3. Navigate to **API Keys** in the dashboard
4. Create a new key and paste it into your `.env` file

> The free tier is sufficient for this project. The `llama-3.1-8b-instant` model is available at no cost.

---

## 4. How to Run

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`.

---

## 5. How to Use the App

1. **Paste a Job URL** — enter any public job posting link (LinkedIn, Greenhouse, Lever, company career pages, etc.)
2. **Upload your Resume** — click the upload area and select your resume in PDF format
3. **Click "Run Agents"** — the system will run all 4 agents sequentially (takes ~15-30 seconds)
4. **Review the Outputs** — four expandable sections will appear:
   - **Job Analysis** — extracted job title, company, skills, and summary
   - **Resume Match Score** — a 0-100 score with a list of missing skills
   - **Rewritten Resume Bullets** — your experience bullets rephrased to match JD language
   - **Cold Recruiter Email** — a ready-to-send outreach email

---

## 6. Architecture

The app uses **LangGraph** to orchestrate 4 sequential agents in a `StateGraph`:

```
START → JD Scraper → Resume Scorer → Bullet Rewriter → Email Generator → END
```

| Agent | File | What it does |
|---|---|---|
| **JD Scraper** | `nodes/jd_scraper.py` | Fetches the job URL, strips HTML, and uses LLM to extract job title, company, required skills, and a role summary. |
| **Resume Scorer** | `nodes/resume_scorer.py` | Compares resume text against JD keywords and returns a match score (0-100) plus a list of missing skills. |
| **Bullet Rewriter** | `nodes/bullet_rewriter.py` | Rewrites resume experience bullets using JD language while keeping all facts truthful. |
| **Email Generator** | `nodes/email_generator.py` | Generates a concise cold outreach email referencing the specific role and candidate strengths. |

All agents share a common `AgentState` TypedDict and communicate through it.

---

## 7. Demo Tips

- **Best job URLs to try**: LinkedIn job postings, Greenhouse/Lever pages, or any company careers page with a clean job description.
- **Resume format**: Single or multi-page PDF. The parser handles all pages.
- **Groq free tier**: The `llama-3.1-8b-instant` model is fast and free — no credit card required.
- **Iteration**: You can run the agents multiple times with different job URLs to compare outputs.
- **Copy outputs**: Use the copy functionality in the email section to quickly paste the email into your email client.

---

## 8. Supported Job URL Sources

The URL scraper works with public job pages including:
- **Internshala** (internshala.com) — recommended for demo
- **Naukri** (naukri.com)
- **Wellfound / AngelList** (wellfound.com)
- **Company careers pages** (e.g. careers.google.com, notion.so/careers, any `/careers` or `/jobs` page)

> **⚠️ LinkedIn URLs will NOT work** because LinkedIn requires login to view job postings. If you paste a LinkedIn URL, the app will automatically detect the login wall and prompt you to paste the JD text directly instead.

For demo purposes, use an **Internshala URL** for a clean end-to-end demonstration of the URL scraping flow.

---

## Tech Stack

| Technology | Purpose |
|---|---|
| **LangGraph** | Agent orchestration |
| **LangChain** | LLM integration |
| **Groq** | LLM inference (LLaMA 3.1 8B) |
| **Streamlit** | Web UI |
| **BeautifulSoup4** | HTML parsing |
| **pdfplumber** | PDF text extraction |
