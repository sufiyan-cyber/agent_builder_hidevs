"""Node 4: Generate a cold outreach email to the recruiter/hiring manager."""

import os
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv
import streamlit as st
load_dotenv()


def email_generator(state: dict) -> dict:
    """Use Groq LLM to generate a concise cold recruiter email."""
    if state.get("error"):
        return state

    try:
        llm = ChatGroq(
            model="llama-3.1-8b-instant",
            temperature=0.3,
            api_key=st.secrets.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY"),
        )

        prompt = f"""You are an expert career coach.

Write a cold outreach email to the recruiter or hiring manager for the following role.

Job Description:
\"\"\"
{state.get('jd_text', '')}
\"\"\"

Candidate's Key Strengths (rewritten bullets):
\"\"\"
{state.get('rewritten_bullets', '')}
\"\"\"

Email requirements:
- Be concise: under 150 words total.
- Reference the specific role and company by name.
- Mention 2-3 concrete strengths from the candidate's background.
- End with a clear call to action (e.g., requesting a brief call).
- Tone: professional, confident, not generic.
- Format: include Subject line, then the email body.
- Do NOT include placeholders like [Your Name] — leave those for the user to fill in."""

        result = llm.invoke([HumanMessage(content=prompt)])
        state["cold_email"] = result.content.strip()

    except Exception as e:
        state["cold_email"] = ""
        state["error"] = f"Email Generator error: {e}"

    return state
