"""Node 1: Scrape and parse job description from a URL."""

import os
import requests
from bs4 import BeautifulSoup
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv
import streamlit as st
load_dotenv()

# Keywords that indicate a login wall / blocked page
LOGIN_WALL_KEYWORDS = [
    "sign in", "log in", "login", "join now",
    "authwall", "checkpoint", "please enable js",
]


def _detect_login_wall(text: str) -> bool:
    """Return True if the text looks like a login-wall page."""
    lower = text.lower()
    return any(kw in lower for kw in LOGIN_WALL_KEYWORDS)


def _extract_best_content(soup: BeautifulSoup) -> str:
    """Try several selectors in priority order and return the one with
    the most text content.  Falls back to <body>."""
    selectors = [
        "article",
        "main",
        ".job-description",
        ".description",
        "#job-description",
        "body",
    ]
    best_text = ""
    for sel in selectors:
        el = soup.select_one(sel)
        if el:
            candidate = el.get_text(separator="\n", strip=True)
            if len(candidate) > len(best_text):
                best_text = candidate
    return best_text


def _run_llm_extraction(clean_text: str, state: dict) -> dict:
    """Use Groq LLM to extract structured info from the JD text."""
    llm = ChatGroq(
        model="llama-3.1-8b-instant",
        temperature=0.3,
        api_key=st.secrets.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY"),
    )

    prompt = f"""Analyze the following job posting text and return:
1. Job Title
2. Company Name
3. Required Skills / Technologies (as a comma-separated list)
4. A 3-sentence summary of the role

Format your response EXACTLY like this:
JOB TITLE: <title>
COMPANY: <company>
SKILLS: <skill1>, <skill2>, <skill3>, ...
SUMMARY: <3-sentence summary>

Job Posting:
\"\"\" 
{clean_text}
\"\"\""""

    result = llm.invoke([HumanMessage(content=prompt)])
    llm_output = result.content

    # Parse keywords from LLM output
    keywords = []
    for line in llm_output.splitlines():
        if line.upper().startswith("SKILLS:"):
            skills_str = line.split(":", 1)[1].strip()
            keywords = [s.strip() for s in skills_str.split(",") if s.strip()]
            break

    state["jd_text"] = llm_output
    state["keywords"] = keywords
    state["error"] = ""
    return state


def jd_scraper(state: dict) -> dict:
    """Fetch a job posting URL, extract clean text, and use Groq LLM to
    identify the job title, company, required skills, and a role summary.

    If the URL is empty or scraping fails / hits a login wall, the node
    sets state["scrape_failed"] = True so the caller can fall back to
    pasted JD text.
    """
    job_url = state.get("job_url", "").strip()

    # If no URL was provided, check for pasted JD text
    if not job_url:
        jd_raw = state.get("jd_raw_text", "").strip()
        if jd_raw:
            state["scrape_failed"] = True
            # Use pasted text directly through LLM extraction
            try:
                truncated = jd_raw[:6000] if len(jd_raw) > 6000 else jd_raw
                state = _run_llm_extraction(truncated, state)
                state["scrape_failed"] = True  # still mark as scrape-failed
            except Exception as e:
                state["jd_text"] = jd_raw
                state["keywords"] = []
                state["error"] = f"LLM extraction error: {e}"
            return state
        else:
            state["scrape_failed"] = True
            state["jd_text"] = ""
            state["keywords"] = []
            state["error"] = "No job URL or JD text provided."
            return state

    # ---- Attempt to scrape the URL ----
    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept": (
                "text/html,application/xhtml+xml,application/xml;"
                "q=0.9,image/avif,image/webp,*/*;q=0.8"
            ),
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
        }
        response = requests.get(job_url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # Remove script/style elements
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()

        # Extract best content section
        clean_text = _extract_best_content(soup)

        # Collapse excessive blank lines
        lines = [line.strip() for line in clean_text.splitlines() if line.strip()]
        clean_text = "\n".join(lines)

        # Check for login wall or insufficient content
        if len(clean_text) < 200 or _detect_login_wall(clean_text):
            state["scrape_failed"] = True
            state["jd_text"] = ""
            state["keywords"] = []
            # Don't set error — the app.py layer handles fallback
            return state

        # Truncate to ~6000 chars to stay within context limits
        if len(clean_text) > 6000:
            clean_text = clean_text[:6000]

        # ---- LLM extraction ----
        state = _run_llm_extraction(clean_text, state)
        state["scrape_failed"] = False

    except requests.RequestException:
        state["scrape_failed"] = True
        state["jd_text"] = ""
        state["keywords"] = []
        # Don't set a hard error — let app.py fall back to pasted text
    except Exception as e:
        state["scrape_failed"] = True
        state["jd_text"] = ""
        state["keywords"] = []
        state["error"] = f"JD Scraper error: {e}"

    return state
