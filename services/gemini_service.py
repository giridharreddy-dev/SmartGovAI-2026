"""Integration helpers for calling the Gemini API to simplify scheme documents."""

import hashlib
import json
import os
import threading
from collections import OrderedDict
from functools import lru_cache
from typing import Any, Dict

from config import MODEL_NAME
from logger_config import logger

try:
    from google import genai
    from google.genai import types
    from google.genai import Client
except ImportError:
    genai = None
    types = None
    Client = Any

_GEMINI_CACHE_SIZE = 64
_gemini_response_cache: "OrderedDict[str, Dict[str, Any]]" = OrderedDict()
_gemini_pending: dict[str, threading.Event] = {}
_gemini_lock = threading.Lock()

@lru_cache(maxsize=1)
def get_client() -> Client | None:
    """Return a cached Gemini client when the API key is configured."""
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if genai and api_key:
        return genai.Client(api_key=api_key)
    return None


def is_gemini_available() -> bool:
    """Return whether the Gemini API client is available."""
    return get_client() is not None


def _make_gemini_cache_key(complex_text: str, scheme_name: str) -> str:
    digest_input = scheme_name.encode("utf-8") + b"\x00" + complex_text.encode("utf-8")
    return hashlib.sha256(digest_input).hexdigest()


def _prune_gemini_cache() -> None:
    while len(_gemini_response_cache) > _GEMINI_CACHE_SIZE:
        _gemini_response_cache.popitem(last=False)


def _call_gemini(client: Client, complex_text: str, scheme_name: str) -> Dict[str, Any]:
    prompt = f'''You simplify Indian government health scheme documents for rural Andhra Pradesh citizens.

Scheme/document name: {scheme_name}
Text:
"""{complex_text}"""

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
}}'''
    # Some test environments or installs may not have google.genai.types available.
    # If `types` is not present, call the client without the typed config.
    if types is not None and hasattr(types, "GenerateContentConfig"):
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.2,
            ),
        )
    else:
        response = client.models.generate_content(model=MODEL_NAME, contents=prompt)
    try:
        result = json.loads(response.text)
    except json.JSONDecodeError:
        logger.exception("Gemini returned invalid JSON.")
        raise ValueError("Invalid AI response.")
    if "simplified" not in result or "telugu" not in result:
        raise ValueError("Gemini returned an unexpected shape")
    return result


def simplify_document(complex_text: str, scheme_name: str) -> Dict[str, Any]:
    """Call Gemini API to simplify a scheme document."""
    client = get_client()
    if client is None:
        raise RuntimeError(
            "PDF simplification needs GEMINI_API_KEY. Built-in health schemes still work."
        )

    # Include the client object's id in the cache key so different client
    # instances (e.g., test mocks) do not share cache entries.
    cache_key = _make_gemini_cache_key(complex_text, scheme_name) + f":{id(client)}"
    with _gemini_lock:
        if cache_key in _gemini_response_cache:
            logger.info("Gemini cache hit: scheme='%s'", scheme_name)
            _gemini_response_cache.move_to_end(cache_key)
            return _gemini_response_cache[cache_key]

        pending = _gemini_pending.get(cache_key)
        if pending is None:
            pending = threading.Event()
            _gemini_pending[cache_key] = pending
            first_request = True
        else:
            first_request = False

    if not first_request:
        logger.info("Waiting for duplicate Gemini request to complete: scheme='%s'", scheme_name)
        pending.wait()
        with _gemini_lock:
            if cache_key in _gemini_response_cache:
                return _gemini_response_cache[cache_key]
            raise RuntimeError("Gemini request failed during duplicate wait.")

    logger.info("Gemini request started: scheme='%s'", scheme_name)
    try:
        result = _call_gemini(client, complex_text, scheme_name)
        with _gemini_lock:
            _gemini_response_cache[cache_key] = result
            _prune_gemini_cache()
            pending.set()
            del _gemini_pending[cache_key]
        return result
    except Exception:
        with _gemini_lock:
            pending.set()
            del _gemini_pending[cache_key]
        raise
