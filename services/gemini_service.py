import json
import os
from typing import Dict, Any

from config import MODEL_NAME
from logger_config import logger

try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None
    types = None

api_key = os.environ.get("GEMINI_API_KEY", "").strip()
if genai and api_key:
    client = genai.Client(api_key=api_key)
else:
    client = None

def is_gemini_available():
    return client is not None

def simplify_document(complex_text: str, scheme_name: str) -> Dict[str, Any]:
    """Call Gemini API to simplify a scheme document."""
    if client is None:
        raise RuntimeError(
            "PDF simplification needs GEMINI_API_KEY. Built-in health schemes still work."
        )
    prompt = f"""
You simplify Indian government health scheme documents for rural Andhra Pradesh citizens.

Scheme/document name: {scheme_name}
Text:
\"\"\"{complex_text}\"\"\"

Return simple, accurate information. Do not invent benefits that are not present in the text.
Use easy English, then translate to clear Telugu.

Return strictly this JSON object:
{{
  "simplified": {{
    "eligibility": "Who can apply?",
    "benefits": "What do they get?",
    "documents": "What documents are needed?",
    "steps": "How to apply step by step?"
  }},
  "telugu": {{
    "eligibility": "Telugu translation of eligibility",
    "benefits": "Telugu translation of benefits",
    "documents": "Telugu translation of documents",
    "steps": "Telugu translation of steps"
  }}
}}
"""
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.2,
        ),
    )
    try:
        result = json.loads(response.text)
    except json.JSONDecodeError:
        logger.exception("Gemini returned invalid JSON.")
        raise ValueError("Invalid AI response.")
    if "simplified" not in result or "telugu" not in result:
        raise ValueError("Gemini returned an unexpected shape")
    return result
