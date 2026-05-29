"""Extract text from uploaded resume PDF using pdfplumber."""

import pdfplumber


def extract_text_from_pdf(uploaded_file) -> str:
    """Extract all text from an uploaded PDF file.

    Args:
        uploaded_file: A file-like object (e.g., from Streamlit's file_uploader).

    Returns:
        Clean extracted text as a single string.
    """
    text_pages = []
    try:
        with pdfplumber.open(uploaded_file) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_pages.append(page_text)
    except Exception as e:
        return f"Error reading PDF: {e}"

    return "\n\n".join(text_pages).strip()
