"""Node 2: Score resume against JD keywords."""

import os
import json
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv
import streamlit as st
load_dotenv()


def resume_scorer(state: dict) -> dict:
    """Use Groq LLM to score how well the resume matches JD keywords
    and identify missing skills."""
    if state.get("error"):
        return state

    try:
        llm = ChatGroq(
            model="llama-3.1-8b-instant",
            temperature=0.3,
            api_key=st.secrets.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY"),
        )

        keywords_str = ", ".join(state.get("keywords", []))

        prompt = f"""You are an expert resume reviewer.

Compare the following resume text against the required job keywords.

Resume:
\"\"\"
{state.get('resume_text', '')}
\"\"\"

Required Keywords/Skills:
{keywords_str}

Respond in STRICT JSON format only — no markdown, no explanation, no extra text:
{{"score": <0-100>, "missing_skills": ["skill1", "skill2"]}}

Rules:
- score: integer from 0 to 100 representing how well the resume matches.
- missing_skills: list of keywords from the job that are NOT present in the resume.
"""

        result = llm.invoke([HumanMessage(content=prompt)])
        raw = result.content.strip()

        # Try to extract JSON from the response
        # Sometimes LLMs wrap JSON in markdown code blocks
        if "```" in raw:
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
            raw = raw.strip()

        parsed = json.loads(raw)
        state["match_score"] = int(parsed.get("score", 0))
        state["missing_skills"] = parsed.get("missing_skills", [])

    except json.JSONDecodeError:
        state["match_score"] = 0
        state["missing_skills"] = []
        state["error"] = "Resume Scorer: Failed to parse LLM JSON response."
    except Exception as e:
        state["match_score"] = 0
        state["missing_skills"] = []
        state["error"] = f"Resume Scorer error: {e}"

    return state
