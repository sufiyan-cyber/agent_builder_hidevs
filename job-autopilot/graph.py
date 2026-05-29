"""LangGraph graph definition for the Job Application Autopilot."""

import os
from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv
import streamlit as st

from nodes.jd_scraper import jd_scraper
from nodes.resume_scorer import resume_scorer
from nodes.bullet_rewriter import bullet_rewriter
from nodes.email_generator import email_generator

load_dotenv()


class AgentState(TypedDict):
    """Shared state passed through all LangGraph nodes."""
    job_url: str
    resume_text: str
    jd_text: str
    keywords: list[str]
    match_score: int
    missing_skills: list[str]
    rewritten_bullets: str
    cold_email: str
    error: str
    jd_raw_text: str         # pasted JD text from user
    scrape_failed: bool      # whether URL scraping failed


def jd_fallback(state: dict) -> dict:
    """If scraping failed but the user pasted JD text, run LLM extraction
    on the pasted text so downstream nodes have jd_text and keywords."""
    # Only run if scrape actually failed AND we don't already have jd_text
    if not state.get("scrape_failed", False):
        return state

    if state.get("jd_text", "").strip():
        # jd_scraper already populated jd_text (e.g. from pasted text path)
        return state

    jd_raw = state.get("jd_raw_text", "").strip()
    if not jd_raw:
        state["error"] = (
            "Could not extract job details from URL and no JD text provided. "
            "Please paste the job description manually."
        )
        return state

    try:
        llm = ChatGroq(
            model="llama-3.1-8b-instant",
            temperature=0.3,
            api_key=st.secrets.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY"),
        )

        truncated = jd_raw[:6000] if len(jd_raw) > 6000 else jd_raw

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
{truncated}
\"\"\""""

        result = llm.invoke([HumanMessage(content=prompt)])
        llm_output = result.content

        keywords = []
        for line in llm_output.splitlines():
            if line.upper().startswith("SKILLS:"):
                skills_str = line.split(":", 1)[1].strip()
                keywords = [s.strip() for s in skills_str.split(",") if s.strip()]
                break

        state["jd_text"] = llm_output
        state["keywords"] = keywords
        state["error"] = ""

    except Exception as e:
        state["jd_text"] = jd_raw
        state["keywords"] = []
        state["error"] = f"LLM extraction error on pasted JD: {e}"

    return state


def build_graph():
    """Build and compile the LangGraph StateGraph."""
    graph = StateGraph(AgentState)

    # Add nodes
    graph.add_node("jd_scraper", jd_scraper)
    graph.add_node("jd_fallback", jd_fallback)
    graph.add_node("resume_scorer", resume_scorer)
    graph.add_node("bullet_rewriter", bullet_rewriter)
    graph.add_node("email_generator", email_generator)

    # Define edges
    graph.add_edge(START, "jd_scraper")
    graph.add_edge("jd_scraper", "jd_fallback")
    graph.add_edge("jd_fallback", "resume_scorer")
    graph.add_edge("resume_scorer", "bullet_rewriter")
    graph.add_edge("bullet_rewriter", "email_generator")
    graph.add_edge("email_generator", END)

    return graph.compile()


# Pre-compile the graph
compiled_graph = build_graph()


def run_graph(job_url: str, resume_text: str, jd_raw_text: str = "") -> AgentState:
    """Execute the full agent pipeline.

    Args:
        job_url: URL of the job posting to analyse (can be empty).
        resume_text: Extracted plain-text from the candidate's resume PDF.
        jd_raw_text: Pasted JD text from the user (fallback if URL fails).

    Returns:
        Final AgentState dict with all fields populated.
    """
    initial_state: AgentState = {
        "job_url": job_url,
        "resume_text": resume_text,
        "jd_text": "",
        "keywords": [],
        "match_score": 0,
        "missing_skills": [],
        "rewritten_bullets": "",
        "cold_email": "",
        "error": "",
        "jd_raw_text": jd_raw_text,
        "scrape_failed": False,
    }

    result = compiled_graph.invoke(initial_state)
    return result
