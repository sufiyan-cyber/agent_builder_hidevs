"""Node 3: Rewrite resume experience bullets to better match the JD."""

import os
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv
import streamlit as st
load_dotenv()


def bullet_rewriter(state: dict) -> dict:
    """Use Groq LLM to rewrite resume experience bullets using JD language."""
    if state.get("error"):
        return state

    try:
        llm = ChatGroq(
            model="llama-3.1-8b-instant",
            temperature=0.3,
            api_key=st.secrets.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY"),
        )

        keywords_str = ", ".join(state.get("keywords", []))

        prompt = f"""You are an expert resume writer.

Below is a candidate's resume and a job description they are applying to.

Resume:
\"\"\"
{state.get('resume_text', '')}
\"\"\"

Job Description:
\"\"\"
{state.get('jd_text', '')}
\"\"\"

Target Keywords: {keywords_str}

Rewrite the experience/project bullet points from the resume so they:
1. Use language and terminology from the job description where truthful.
2. Highlight relevant experience that matches the JD requirements.
3. Keep all facts truthful — do NOT invent skills or technologies the person did not use.
4. Use strong action verbs and quantify impact where possible.

Return ONLY the rewritten bullet points, formatted as a bulleted list using "•" characters.
Group them under their original job title / project heading if possible."""

        result = llm.invoke([HumanMessage(content=prompt)])
        state["rewritten_bullets"] = result.content.strip()

    except Exception as e:
        state["rewritten_bullets"] = ""
        state["error"] = f"Bullet Rewriter error: {e}"

    return state
