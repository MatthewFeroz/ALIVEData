import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def summarize_text(ocr_text):
    """Send OCR result to LLM and return step-by-step documentation."""
    prompt = f"""
You are an assistant turning raw OCR text into step-by-step procedural documentation.
Write concise numbered steps describing what the user did,
based only on this OCR text:

{ocr_text}
"""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )
    summary = response.choices[0].message.content.strip()
    return summary

